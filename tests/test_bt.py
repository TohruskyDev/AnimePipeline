import os
import time
from pathlib import Path

import pytest

from animepipeline.bt.qb import QBittorrentManager
from animepipeline.config import QBitTorrentConfig


@pytest.mark.skipif(
    os.environ.get("GITHUB_ACTIONS") == "true", reason="Only test locally cuz BT may not suitable for CI"
)
def test_qbittorrent() -> None:
    torrent_hash = "2f3605cbe42e1af71f417586b1d790b8c9274cd4"
    torrent_url = "https://nyaa.si/download/1877758.torrent"

    if Path("../deploy/docker/downloads").exists():
        download_path = Path("../deploy/docker/downloads")
    else:
        download_path = Path("./deploy/docker/downloads")

    cfg = QBitTorrentConfig(
        host="localhost",
        port=8080,
        username="admin",
        password="adminadmin",
        download_path=download_path,
    )
    qb_manager = QBittorrentManager(config=cfg)

    qb_manager.add_torrent(torrent_hash=torrent_hash, torrent_url=torrent_url)

    # Check if the download is complete
    while True:
        if qb_manager.check_download_complete(torrent_hash):
            print("Download is complete.")
            break
        else:
            print("Download is not complete.")
            time.sleep(5)

    # Get the downloaded filename
    file_path = qb_manager.get_downloaded_path(torrent_hash)
    if file_path is not None:
        print(f"Downloaded file: {file_path}")
    else:
        print("Download is not complete or failed.")
