from pathlib import Path
from typing import Optional, Union

import telegram.error
from telegram import Bot
from tenacity import retry, stop_after_attempt, wait_random

from animepipeline.config import TelegramConfig


class TGChannelVideoSender:
    """
    TG Channel Video Sender.

    :param config: The telegram configuration.
    """

    def __init__(self, config: TelegramConfig) -> None:
        if config.local_mode:
            self.bot = Bot(
                token=config.bot_token,
                base_url=str(config.base_url),
                base_file_url=str(config.base_file_url),
                local_mode=True,
            )
        else:
            self.bot = Bot(token=config.bot_token)

        self.channel_id = config.channel_id

    @retry(wait=wait_random(min=3, max=5), stop=stop_after_attempt(10))
    async def send_video(self, video_path: Union[Path, str], caption: Optional[str] = None) -> None:
        """
        Send video to the channel.

        :param video_path:
        :param caption: the caption of the video
        """
        video_path = Path(video_path)
        video_name = video_path.name
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        if caption is None:
            caption = video_name

        with open(video_path, "rb") as f:
            video_file = f.read()

        try:
            await self.bot.send_video(
                chat_id=self.channel_id,
                video=video_file,
                filename=video_name,
                caption=caption,
                read_timeout=6000,
                write_timeout=6000,
            )
        except telegram.error.NetworkError as e:
            print(f"Network error: {e}, video path: {video_path}, video_caption: {caption}, retrying...")
            raise e
        except Exception as e:
            print(f"Unknown Error sending video: {e}, video path: {video_path}, video_caption: {caption}")
