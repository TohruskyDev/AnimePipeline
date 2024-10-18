from datetime import datetime
from typing import Union

from pydantic import AnyHttpUrl, BaseModel


class RSSInfo(BaseModel):
    rss_link: Union[AnyHttpUrl, str]
    pattern: str


class TorrentInfo(BaseModel):
    episode: int
    title: str
    link: Union[AnyHttpUrl, str]
    hash: str
    pub_date: datetime
    size: str
