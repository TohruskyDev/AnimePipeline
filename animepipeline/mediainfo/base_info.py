from pydantic import BaseModel


class BaseInfo(BaseModel):
    episode: int
    name: str
    uploader: str
