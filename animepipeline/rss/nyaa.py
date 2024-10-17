from datetime import datetime
from typing import List

import feedparser
import httpx
from tenacity import retry, stop_after_attempt, stop_after_delay, wait_random

from animepipeline.rss.base_rss import BaseRSS


@retry(wait=wait_random(min=3, max=5), stop=stop_after_delay(10) | stop_after_attempt(30))
def parse_nyaa(rss_link: str) -> List[BaseRSS]:
    rss_content = httpx.get(rss_link).text

    # 使用feedparser解析XML
    feed = feedparser.parse(rss_content)

    res: List[BaseRSS] = []

    # 遍历每个item
    for item in feed.entries:
        res.append(
            BaseRSS(
                title=item.title,
                link=item.link,
                hash=item.nyaa_infohash,
                pub_date=datetime.strptime(item.published, "%a, %d %b %Y %H:%M:%S %z"),
                size=item.nyaa_size,
            )
        )

    return res
