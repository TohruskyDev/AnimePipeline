from animepipeline.config.server import ServerConfig

from .util import CONFIG_PATH


def test_load_server_config() -> None:
    # 使用 from_yaml 加载配置
    server_config = ServerConfig.from_yaml(CONFIG_PATH / "server.yml")
    print("Server configuration loaded successfully.")
    print(server_config.db)
    print(server_config.qbittorrent)
    print(server_config.finalrip)

    # 使用 refresh_config 刷新配置
    server_config.refresh_config(CONFIG_PATH / "server.yml")
    print("Server configuration refreshed successfully.")
    print(server_config.db)
    print(server_config.qbittorrent)
    print(server_config.finalrip)
