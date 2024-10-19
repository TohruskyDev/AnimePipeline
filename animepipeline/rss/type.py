from datetime import datetime
from typing import Union

from pydantic import AnyHttpUrl, BaseModel


class TorrentInfo(BaseModel):
    name: str
    episode: int
    title: str
    link: Union[AnyHttpUrl, str]
    hash: str
    pub_date: datetime
    size: str
