import os
import time

import pytest

from animepipeline.config import FinalRipConfig, RSSConfig
from animepipeline.encode.finalrip import FinalRipClient
from animepipeline.encode.type import GetTaskProgressRequest, StartTaskRequest, TaskNotCompletedError

from .util import ASSETS_PATH, CONFIG_PATH

video_key = "test_144p.mp4"


@pytest.mark.skipif(os.environ.get("GITHUB_ACTIONS") == "true", reason="Only test locally")
class Test_FinalRip:
    def setup_method(self) -> None:
        self.finalrip = FinalRipClient(FinalRipConfig(url="http://10.132.217.11:8848", token="114514"))

    def test_ping(self) -> None:
        ping_response = self.finalrip.ping()
        print(ping_response)

    def test_new_task(self) -> None:
        try:
            self.finalrip.upload_and_new_task(ASSETS_PATH / video_key)
        except Exception as e:
            print(e)

    def test_start_task(self) -> None:
        rss_config: RSSConfig = RSSConfig.from_yaml(CONFIG_PATH / "rss.yml")

        p: str = ""
        for _, v in rss_config.params.items():
            p = v
        print(repr(p))
        s: str = ""
        for _, v in rss_config.scripts.items():
            s = v
        print(repr(s))
        start_task_response = self.finalrip.start_task(StartTaskRequest(encode_param=p, script=s, video_key=video_key))
        print(start_task_response)

    def test_task_progress(self) -> None:
        task_progress = self.finalrip.get_task_progress(GetTaskProgressRequest(video_key=video_key))
        print(task_progress)

    def test_download_completed_task(self) -> None:
        while True:
            try:
                self.finalrip.download_completed_task(video_key=video_key, save_path=ASSETS_PATH / "new.mkv")
                break
            except TaskNotCompletedError:
                print("Task not completed yet")
                time.sleep(5)
            except Exception as e:
                print(e)
                time.sleep(5)
