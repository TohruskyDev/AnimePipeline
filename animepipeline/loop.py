import asyncio
from pathlib import Path

from loguru import logger

from animepipeline.bt import QBittorrentManager
from animepipeline.config import NyaaConfig, RSSConfig, ServerConfig
from animepipeline.encode import FinalRipClient
from animepipeline.mediainfo import FileNameInfo, gen_file_name
from animepipeline.pool import AsyncTaskExecutor
from animepipeline.post import TGChannelSender
from animepipeline.rss import TorrentInfo, parse_nyaa
from animepipeline.store import AsyncJsonStore, TaskStatus


class TaskInfo(TorrentInfo):
    uploader: str
    script: str
    param: str


def build_task_info(torrent_info: TorrentInfo, nyaa_config: NyaaConfig, rss_config: RSSConfig) -> TaskInfo:
    """
    Build TaskInfo from TorrentInfo, NyaaConfig and RSSConfig

    :param torrent_info: TorrentInfo
    :param nyaa_config: NyaaConfig
    :param rss_config: RSSConfig
    :return: TaskInfo
    """
    if nyaa_config.script not in rss_config.scripts:
        raise ValueError(f"script not found: {nyaa_config.script}")
    if nyaa_config.param not in rss_config.params:
        raise ValueError(f"param not found: {nyaa_config.param}")

    script = rss_config.scripts[nyaa_config.script]
    param = rss_config.params[nyaa_config.param]

    return TaskInfo(
        **torrent_info.model_dump(),
        uploader=nyaa_config.uploader,
        script=script,
        param=param,
    )


class Loop:
    """
    Loop: main loop for animepipeline

    :param server_config: an instance of ServerConfig
    :param rss_config: an instance of RSSConfig
    :param json_store: an instance of AsyncJsonStore
    """

    def __init__(self, server_config: ServerConfig, rss_config: RSSConfig, json_store: AsyncJsonStore):
        self.stop_event = asyncio.Event()

        self.server_config = server_config
        self.rss_config = rss_config

        self.json_store = json_store

        self.task_executor = AsyncTaskExecutor()  # async task pool

        self.qbittorrent_manager = QBittorrentManager(config=self.server_config.qbittorrent)

        self.finalrip_client = FinalRipClient(config=self.server_config.finalrip)

        self.tg_channel_sender = (
            TGChannelSender(config=self.server_config.telegram) if self.server_config.telegram.enable else None
        )

    async def stop(self) -> None:
        """
        Stop the loop
        """
        self.stop_event.set()

    async def start(self) -> None:
        """
        Start the loop
        """
        while not self.stop_event.is_set():
            # refresh rss config
            self.rss_config.refresh_config()
            for cfg in self.rss_config.nyaa:
                torrent_info_list = parse_nyaa(cfg)

                for torrent_info in torrent_info_list:
                    task_info = build_task_info(torrent_info, cfg, self.rss_config)

                    await self.task_executor.submit_task(torrent_info.hash, self.pipeline, task_info)

            await asyncio.sleep(self.server_config.loop.interval)

    async def pipeline(self, task_info: TaskInfo) -> None:
        # init task status
        if not await self.json_store.check_task_exist(task_info.hash):
            await self.json_store.add_task(task_id=task_info.hash, status=TaskStatus())

        task_status = await self.json_store.get_task(task_info.hash)

        if task_status.done:
            return

        logger.info(f"Start pipeline for {task_info.name} EP {task_info.episode}")

        # check bt
        if task_status.bt_downloaded_path is None:
            logger.info(f"Start BT download for {task_info.name} EP {task_info.episode}")
            # download torrent file
            while not self.qbittorrent_manager.check_torrent_exist(task_info.hash):
                self.qbittorrent_manager.add_torrent(torrent_hash=task_info.hash, torrent_url=task_info.link)  # type: ignore
                await asyncio.sleep(10)

            # check download complete
            while not self.qbittorrent_manager.check_download_complete(task_info.hash):
                await asyncio.sleep(10)

            # get downloaded path
            bt_downloaded_path = self.qbittorrent_manager.get_downloaded_path(task_info.hash)

            # update task status
            task_status.bt_downloaded_path = str(bt_downloaded_path)
            await self.json_store.update_task(task_info.hash, task_status)

        assert task_status.bt_downloaded_path is not None

        # check finalrip
        if task_status.finalrip_downloaded_path is None:
            logger.info(f"Start FinalRip Encode for {task_info.name} EP {task_info.episode}")
            # start finalrip task

            bt_downloaded_path = Path(task_status.bt_downloaded_path)

            while not self.finalrip_client.check_task_exist(bt_downloaded_path.name):
                try:
                    self.finalrip_client.upload_and_new_task(bt_downloaded_path)
                except Exception as e:
                    logger.error(f"Failed to start finalrip task: {e}")
                    raise e
                await asyncio.sleep(10)

            try:
                self.finalrip_client.start_task(
                    video_key=bt_downloaded_path.name,
                    encode_param=task_info.param,
                    script=task_info.script,
                )
            except Exception as e:
                logger.error(f"Failed to start finalrip task: {e}")
                raise e

            # check task progress
            while not self.finalrip_client.check_task_completed(bt_downloaded_path.name):
                await asyncio.sleep(10)

            # download temp file to bt_downloaded_path's parent directory
            temp_saved_path: Path = bt_downloaded_path.parent / (bt_downloaded_path.name + "-encoded.mkv")
            self.finalrip_client.download_completed_task(video_key=bt_downloaded_path.name, save_path=temp_saved_path)

            # rename temp file
            gen_name = gen_file_name(
                FileNameInfo(
                    path=temp_saved_path, episode=task_info.episode, name=task_info.name, uploader=task_info.uploader
                )
            )
            finalrip_downloaded_path = bt_downloaded_path.parent / gen_name
            temp_saved_path.rename(finalrip_downloaded_path)

            # update task status
            task_status.finalrip_downloaded_path = str(finalrip_downloaded_path)
            await self.json_store.update_task(task_info.hash, task_status)

        assert task_status.finalrip_downloaded_path is not None

        # check tg
        if not task_status.tg_uploaded:
            logger.info(f"Start Telegram Channel Upload for {task_info.name} EP {task_info.episode}")

            finalrip_downloaded_path = Path(task_status.finalrip_downloaded_path)

            if self.tg_channel_sender is not None:
                await self.tg_channel_sender.send_video(
                    video_path=finalrip_downloaded_path,
                    caption=f"{task_info.translation} | EP {task_info.episode} | {finalrip_downloaded_path.name}",
                )

                task_status.tg_uploaded = True
                await self.json_store.update_task(task_info.hash, task_status)

        assert task_status.tg_uploaded

        # Done!
        task_status.done = True
        await self.json_store.update_task(task_info.hash, task_status)
        logger.info(f"Finish pipeline for {task_info.name} EP {task_info.episode}")
