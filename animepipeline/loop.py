import asyncio

from animepipeline.bt import QBittorrentManager
from animepipeline.config import RSSConfig, ServerConfig
from animepipeline.pool import AsyncTaskExecutor


class Loop:
    def __init__(self, server_config: ServerConfig, rss_config: RSSConfig):
        self.server_config = server_config
        self.rss_config = rss_config

        self.task_executor = AsyncTaskExecutor()  # async task pool

        self.qbittorrent_manager = QBittorrentManager(config=self.server_config.qbittorrent)

    async def start(self) -> None:
        while True:
            # refresh rss config
            self.rss_config.refresh_config()
            await self.task_executor.submit_task("rss file hash", self.pipeline, 1, "ed")

            await asyncio.sleep(self.server_config.loop.interval)

    async def pipeline(self) -> None:
        pass
