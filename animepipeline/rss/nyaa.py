import re
from datetime import datetime
from typing import List

import feedparser
import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, stop_after_delay, wait_random

from animepipeline.rss.type import TorrentInfo


@retry(wait=wait_random(min=3, max=5), stop=stop_after_delay(10) | stop_after_attempt(30))
def parse_nyaa(rss_link: str, pattern: str) -> List[TorrentInfo]:
    rss_content = httpx.get(rss_link).text

    # 使用feedparser解析XML
    feed = feedparser.parse(rss_content)

    res: List[TorrentInfo] = []

    # 遍历每个item
    for item in feed.entries:
        # 使用正则表达式搜索集数
        match = re.search(pattern, item.title)

        # 如果找到匹配项，则提取集数
        if match:
            episode_number = match.group(1)
        else:
            logger.warning(f"Found unmatched item: {item.title}")
            continue

        res.append(
            TorrentInfo(
                episode=episode_number,
                title=item.title,
                link=item.link,
                hash=item.nyaa_infohash,
                pub_date=datetime.strptime(item.published, "%a, %d %b %Y %H:%M:%S %z"),
                size=item.nyaa_size,
            )
        )

    return res
