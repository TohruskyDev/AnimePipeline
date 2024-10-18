import json
import os
import pathlib

import pymediainfo
from loguru import logger

from animepipeline.mediainfo.base_info import BaseInfo


def gen_file_name(input_path: str, anime_info: BaseInfo) -> str:
    """
    Auto generate the file name

    input_path: Fate.Kaleid.Liner.Prisma.Ilya.01.1080p.HEVC-10bit.FLAC.mkv
    anime_info: BaseRSS (episode: 1, name: Fate/Kaleid Liner Prisma Illya, uploader: TensoRaws)

    -> [TensoRaws] Fate/Kaleid Liner Prisma Illya [01] [1080p HEVC-10bit FLAC].mkv

    :param input_path: str
    :param anime_info: BaseInfo
    :return:
    """
    resolution_heigh = "2160p"
    bit_depth = "10bit"
    video_format = "HEVC"
    audio_format = "FLAC"

    write_path = os.path.abspath(input_path)
    encode_media_info = pymediainfo.MediaInfo.parse(write_path, output="JSON")
    encode_tracks = json.loads(encode_media_info)["media"]["track"]

    # video track
    video_track_id = 0
    try:
        for video_track_index, video_track in enumerate(encode_tracks):
            if video_track["@type"] == "Video":
                resolution_heigh = encode_tracks[video_track_index]["Height"] + "p"
                bit_depth = encode_tracks[video_track_index]["BitDepth"] + "bit"
                video_format = encode_tracks[video_track_index]["Format"]

                video_track_id += 1

    except Exception as e:
        logger.warning(e)
        logger.warning("Exceptional video track")
    if video_track_id != 1:
        logger.warning("There may be multiple video tracks or no video tracks, please check")

    # audio track
    audio_track_id = 1
    audio_format_list = []
    try:
        for audio_track_index, audio_track in enumerate(encode_tracks):
            if audio_track["@type"] == "Audio":
                audio_format_list.append(encode_tracks[audio_track_index]["Format"])
                audio_track_id += 1

        if "FLAC" in audio_format_list:
            audio_format = "FLAC"
        else:
            audio_format = audio_format_list[0]

    except Exception as e:
        logger.warning(e)
        logger.warning("Exceptional audio track")

    file_format = pathlib.Path(input_path).suffix

    return f"[{anime_info.uploader}] {anime_info.name} [{str(anime_info.episode).zfill(2)}] [{resolution_heigh} {video_format}-{bit_depth} {audio_format}]{file_format}"
