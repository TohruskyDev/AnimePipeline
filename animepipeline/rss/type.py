from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel


class TorrentInfo(BaseModel):
    episode: int
    title: str
    link: AnyHttpUrl
    hash: str
    pub_date: datetime
    size: str
