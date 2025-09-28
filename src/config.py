from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class RedisSettings(BaseSettings):
    """Redis配置项"""
    host: str = Field(default="115.190.18.222", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    password: str = Field(default="12345678", env="REDIS_PASSWORD")
    db: int = Field(default=0, env="REDIS_DB")
    decode_responses: bool = Field(default=True, env="REDIS_DECODE_RESPONSES")

    # 连接池配置
    max_connections: int = Field(default=10, env="REDIS_MAX_CONNECTIONS")
    socket_timeout: Optional[float] = Field(default=5.0, env="REDIS_SOCKET_TIMEOUT")
    retry_on_timeout: bool = Field(default=True, env="REDIS_RETRY_ON_TIMEOUT")

    # 重试配置
    retry_attempts: int = Field(default=3, env="REDIS_RETRY_ATTEMPTS")
    retry_delay: float = Field(default=0.1, env="REDIS_RETRY_DELAY")

    # 集群配置（如果使用Redis集群）
    is_cluster: bool = Field(default=False, env="REDIS_IS_CLUSTER")
    cluster_nodes: Optional[list] = Field(default=None, env="REDIS_CLUSTER_NODES")


class AppSettings(BaseSettings):
    """应用配置项"""
    name: str = Field(default="FastAPI Redis Service", env="APP_NAME")
    version: str = Field(default="0.1.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="APP_DEBUG")
    host: str = Field(default="0.0.0.0", env="APP_HOST")
    port: int = Field(default=8000, env="APP_PORT")

    # 缓存配置
    default_cache_ttl: int = Field(default=3600, env="DEFAULT_CACHE_TTL")  # 默认缓存时间（秒）


class Settings(BaseSettings):
    """总配置类"""
    app: AppSettings = AppSettings()
    redis: RedisSettings = RedisSettings()


# 创建配置实例
settings = Settings()