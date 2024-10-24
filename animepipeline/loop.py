import asyncio

from animepipeline.bt import QBittorrentManager
from animepipeline.config import NyaaConfig, RSSConfig, ServerConfig
from animepipeline.pool import AsyncTaskExecutor
from animepipeline.post import TGChannelSender
from animepipeline.rss import TorrentInfo, parse_nyaa


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
    def __init__(self, server_config: ServerConfig, rss_config: RSSConfig):
        self.server_config = server_config
        self.rss_config = rss_config

        self.task_executor = AsyncTaskExecutor()  # async task pool

        self.qbittorrent_manager = QBittorrentManager(config=self.server_config.qbittorrent)

        self.tg_channel_sender = (
            TGChannelSender(config=self.server_config.telegram) if self.server_config.telegram.enable else None
        )

    async def start(self) -> None:
        while True:
            # refresh rss config
            self.rss_config.refresh_config()
            for cfg in self.rss_config.nyaa:
                torrent_info_list = parse_nyaa(cfg)

                for torrent_info in torrent_info_list:
                    task_info = build_task_info(torrent_info, cfg, self.rss_config)

                    await self.task_executor.submit_task(torrent_info.hash, self.pipeline, task_info)

            await asyncio.sleep(self.server_config.loop.interval)

    async def pipeline(self, task_info: TaskInfo) -> None:
        pass
