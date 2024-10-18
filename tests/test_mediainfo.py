from animepipeline.mediainfo.base_info import BaseInfo
from animepipeline.mediainfo.gen_file_name import gen_file_name

from .util import TEST_VIDEO_PATH


def test_gen_file_name() -> None:
    anime_info = BaseInfo(
        episode=1,
        name="test 114",
        uploader="TensoRaws",
    )

    name = gen_file_name(input_path=str(TEST_VIDEO_PATH), anime_info=anime_info)
    assert name == "[TensoRaws] test 114 [01] [144p AVC-8bit AAC].mp4"
