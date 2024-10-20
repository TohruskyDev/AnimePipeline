import os
import time

import pytest

from animepipeline.config import FinalRipConfig, RSSConfig
from animepipeline.encode.finalrip import FinalRipClient
from animepipeline.encode.type import StartTaskRequest, TaskNotCompletedError

from .util import ASSETS_PATH, CONFIG_PATH


@pytest.mark.skipif(os.environ.get("GITHUB_ACTIONS") == "true", reason="Only test locally")
def test_finalrip() -> None:
    finalrip = FinalRipClient(FinalRipConfig(url="http://10.132.217.11:8848", token="114514"))
    ping_response = finalrip.ping()
    print(ping_response)

    video_key = "test_144p.mp4"

    try:
        finalrip.upload_and_new_task(ASSETS_PATH / video_key)
    except Exception as e:
        print(e)

    rss_config: RSSConfig = RSSConfig.from_yaml(CONFIG_PATH / "rss.yml")

    p: str = ""
    for _, v in rss_config.params.items():
        p = v
    print(repr(p))
    s: str = ""
    for _, v in rss_config.scripts.items():
        s = v
    print(repr(s))
    start_task_response = finalrip.start_task(StartTaskRequest(encode_param=p, script=s, video_key=video_key))
    print(start_task_response)

    while True:
        try:
            finalrip.download_completed_task(video_key=video_key, save_path=ASSETS_PATH / video_key)
            break
        except TaskNotCompletedError:
            print("Task not completed yet")
        finally:
            time.sleep(5)
