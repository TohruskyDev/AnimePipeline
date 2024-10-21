import mimetypes
from pathlib import Path
from typing import Union

import httpx
from httpx import Client

from animepipeline.config import FinalRipConfig
from animepipeline.encode.type import (
    GetTaskProgressRequest,
    GetTaskProgressResponse,
    NewTaskRequest,
    NewTaskResponse,
    OSSPresignedURLRequest,
    OSSPresignedURLResponse,
    PingResponse,
    StartTaskRequest,
    StartTaskResponse,
    TaskNotCompletedError,
)
from animepipeline.util.video import VIDEO_EXTENSIONS


class FinalRipClient:
    def __init__(self, config: FinalRipConfig):
        self.client = Client(base_url=str(config.url), headers={"token": str(config.token)})

    def ping(self) -> PingResponse:
        try:
            response = self.client.get("/")
            return PingResponse(**response.json())
        except Exception as e:
            print(f"Error ping: {e}")
            raise

    def new_task(self, data: NewTaskRequest) -> NewTaskResponse:
        try:
            response = self.client.post("/api/v1/task/new", params=data.model_dump())
            return NewTaskResponse(**response.json())
        except Exception as e:
            print(f"Error creating task: {e}")
            raise

    def start_task(self, data: StartTaskRequest) -> StartTaskResponse:
        try:
            response = self.client.post("/api/v1/task/start", params=data.model_dump())
            return StartTaskResponse(**response.json())
        except Exception as e:
            print(f"Error starting task: {e}")
            raise

    def get_task_progress(self, data: GetTaskProgressRequest) -> GetTaskProgressResponse:
        try:
            response = self.client.get("/api/v1/task/progress", params=data.model_dump())
            return GetTaskProgressResponse(**response.json())
        except Exception as e:
            print(f"Error getting task progress: {e}")
            raise

    def get_oss_presigned_url(self, data: OSSPresignedURLRequest) -> OSSPresignedURLResponse:
        try:
            response = self.client.get("/api/v1/task/oss/presigned", params=data.model_dump())
            return OSSPresignedURLResponse(**response.json())
        except Exception as e:
            print(f"Error getting presigned URL: {e}")
            raise

    def upload_and_new_task(self, video_path: Union[str, Path]) -> None:
        """
        use file name as video_key, gen oss presigned url, upload file, and new_task, all in one function

        :param video_path: local video file path
        """
        if not Path(video_path).exists():
            raise FileNotFoundError(f"File not found: {video_path}")

        if Path(video_path).suffix not in VIDEO_EXTENSIONS:
            raise ValueError("Only support these video extensions: " + ", ".join(VIDEO_EXTENSIONS))

        # gen oss presigned url
        video_key = Path(video_path).name
        oss_presigned_url_response = self.get_oss_presigned_url(OSSPresignedURLRequest(video_key=video_key))
        if not oss_presigned_url_response.success:
            raise ValueError(f"Error getting presigned URL: {oss_presigned_url_response.error.message}")  # type: ignore

        content_type = mimetypes.guess_type(video_path)[0] or "application/octet-stream"

        # upload file
        with open(video_path, "rb") as file:
            response = httpx.put(
                url=oss_presigned_url_response.data.url,  # type: ignore
                content=file,
                headers={"Content-Type": content_type},
            )
            if response.status_code != 200:
                raise IOError(f"Error uploading file: {response.text}")

        # new task
        new_task_response = self.new_task(NewTaskRequest(video_key=video_key))
        if not new_task_response.success:
            raise ValueError(f"Error creating task: {new_task_response.error.message}")  # type: ignore

    def download_completed_task(self, video_key: str, save_path: Union[str, Path]) -> None:
        """
        download completed task to local

        :param video_key: video_key of the task
        :param save_path: local save path
        """

        get_task_progress_response = self.get_task_progress(GetTaskProgressRequest(video_key=video_key))
        if not get_task_progress_response.success:
            raise ValueError(f"Error getting task progress: {get_task_progress_response.error.message}")  # type: ignore

        if get_task_progress_response.data.encode_url == "":  # type: ignore
            raise TaskNotCompletedError()

        response = self.client.get(get_task_progress_response.data.encode_url)  # type: ignore
        if response.status_code != 200:
            raise IOError(f"Error downloading file: {response.text}")

        with open(save_path, "wb") as file:
            file.write(response.content)
