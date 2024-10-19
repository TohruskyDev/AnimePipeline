import os
from pathlib import Path
from typing import Any, Literal, Union

import yaml
from pydantic import AnyUrl, BaseModel, Field, ValidationError


class DBConfig(BaseModel):
    type: Literal["mongodb"]  # 限定数据库类型为mongodb
    host: str
    port: int = Field(..., ge=1, le=65535)  # 端口号，限制在1-65535之间
    username: Union[str, int]
    password: Union[str, int]
    database: Union[str, int]
    ssl: bool


class QBitTorrentConfig(BaseModel):
    host: str
    port: int = Field(..., ge=1, le=65535)
    username: Union[str, int]
    password: Union[str, int]


class FinalRipConfig(BaseModel):
    url: AnyUrl
    token: Union[str, int]


class ServerConfig(BaseModel):
    db: DBConfig  # 嵌套的配置
    qbittorrent: QBitTorrentConfig
    finalrip: FinalRipConfig

    @classmethod
    def from_yaml(cls, path: Union[Path, str]) -> Any:
        """
        Load configuration from a YAML file.

        :param path: The path to the yaml file.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file {path} not found")
        with open(path, "r", encoding="utf-8") as file:
            try:
                config_data = yaml.safe_load(file)
                return cls(**config_data)
            except yaml.YAMLError as e:
                raise ValueError(f"Error loading YAML: {e}")
            except ValidationError as e:
                raise ValueError(f"Config validation error: {e}")
            except Exception as e:
                raise ValueError(f"Error loading config: {e}")

    def refresh_config(self, path: Union[Path, str]) -> None:
        """
        Refresh configuration from the yaml file.

        :param path: The path to the yaml file.
        """
        try:
            new_config = ServerConfig.from_yaml(path)
        except Exception as e:
            print(f"Failed to load new configuration: {e}")
            return
        self.db = new_config.db
