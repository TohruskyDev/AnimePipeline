import pytest

from animepipeline.config import ServerConfig
from animepipeline.post.tg import TGChannelVideoSender

from .util import ASSETS_PATH, CONFIG_PATH

video_key = "test_144p.mp4"


@pytest.mark.asyncio
async def test_tg_bot() -> None:
    server_config: ServerConfig = ServerConfig.from_yaml(CONFIG_PATH / "server.yml")

    video_sender = TGChannelVideoSender(server_config.telegram)

    await video_sender.send_video(video_path=ASSETS_PATH / video_key, caption="114514 哼哼啊啊啊 | test mp4")
