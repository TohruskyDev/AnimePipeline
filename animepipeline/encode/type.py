from typing import Optional

from pydantic import BaseModel


class Error(BaseModel):
    message: str


class PingResponse(BaseModel):
    error: Optional[Error] = None
    success: bool


class NewTaskRequest(BaseModel):
    video_key: str


class NewTaskResponse(BaseModel):
    error: Optional[Error] = None
    success: bool


class StartTaskRequest(BaseModel):
    encode_param: str
    script: str
    video_key: str


class StartTaskResponse(BaseModel):
    error: Optional[Error] = None
    success: bool


class GetTaskProgressRequest(BaseModel):
    video_key: str


class GetTaskProgressResponse(BaseModel):
    data: Optional[dict] = None
    error: Optional[Error] = None
    success: bool


class OSSPresignedURLRequest(BaseModel):
    video_key: str


class OSSPresignedURLResponse(BaseModel):
    class Data(BaseModel):
        exist: bool
        url: str

    data: Optional[Data] = None
    error: Optional[Error] = None
    success: bool
