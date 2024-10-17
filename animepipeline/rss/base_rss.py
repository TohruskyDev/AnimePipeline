from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel


class BaseRSS(BaseModel):
    title: str
    link: AnyHttpUrl
    hash: str
    pub_date: datetime
    size: str
