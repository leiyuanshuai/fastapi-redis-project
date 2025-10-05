import os
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# 在类定义之前加载环境变量
ENV = os.getenv("ENV", "production")
load_dotenv(f".env.{ENV}")

class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    """Redis配置项"""
    host: str = Field(default="115.190.18.222", validation_alias="REDIS_HOST")
    port: int = Field(default=23123, validation_alias="REDIS_PORT")
    password: str = Field(default="12345678", validation_alias="REDIS_PASSWORD")
    db: int = Field(default=0, validation_alias="REDIS_DB")
    decode_responses: bool = Field(default=True, validation_alias="REDIS_DECODE_RESPONSES")

    # 连接池配置
    max_connections: int = Field(default=10, validation_alias="REDIS_MAX_CONNECTIONS")
    socket_timeout: Optional[float] = Field(default=5.0, validation_alias="REDIS_SOCKET_TIMEOUT")
    retry_on_timeout: bool = Field(default=True, validation_alias="REDIS_RETRY_ON_TIMEOUT")

    # 重试配置
    retry_attempts: int = Field(default=3, validation_alias="REDIS_RETRY_ATTEMPTS")
    retry_delay: float = Field(default=0.1, validation_alias="REDIS_RETRY_DELAY")

    # 集群配置（如果使用Redis集群）
    is_cluster: bool = Field(default=False, validation_alias="REDIS_IS_CLUSTER")
    cluster_nodes: Optional[list] = Field(default=None, validation_alias="REDIS_CLUSTER_NODES")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    db_host: str = Field(..., validation_alias="DB_HOST")
    db_port: str = Field(..., validation_alias="DB_PORT")
    db_username: str = Field(..., validation_alias="DB_USERNAME")
    db_password: str = Field(..., validation_alias="DB_PASSWORD")
    db_database: str = Field(..., validation_alias="DB_DATABASE")

    pg_db_host: str = Field(..., validation_alias="PG_DB_HOST")
    pg_db_port: str = Field(..., validation_alias="PG_DB_PORT")
    pg_db_username: str = Field(..., validation_alias="PG_DB_USERNAME")
    pg_db_password: str = Field(..., validation_alias="PG_DB_PASSWORD")
    pg_db_database: str = Field(..., validation_alias="PG_DB_DATABASE")

    milvus_uri: str = Field(..., validation_alias="MILVUS_URI")
    milvus_username: str = Field(..., validation_alias="MILVUS_USERNAME")
    milvus_password: str = Field(..., validation_alias="MILVUS_PASSWORD")
    llama_index_database: str = Field(..., validation_alias="LLAMA_INDEX_DATABASE")
    llama_index_collection: str = Field(..., validation_alias="LLAMA_INDEX_COLLECTION")
    llama_index_dimension: str = Field(..., validation_alias="LLAMA_INDEX_DIMENSION")

    llm_key_local: str = Field(..., validation_alias="LLM_KEY_LOCAL")
    llm_key_huoshan: str = Field(..., validation_alias="LLM_KEY_HUOSHAN")
    llm_key_bailian: str = Field(..., validation_alias="LLM_KEY_BAILIAN")
    llm_key_deepseek: str = Field(..., validation_alias="LLM_KEY_DEEPSEEK")

    server_port: str = Field(..., validation_alias="SERVER_PORT")
    server_domain: str = Field(..., validation_alias="SERVER_DOMAIN")

    jwt_secret_key: str = Field(..., validation_alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(..., validation_alias="JWT_ALGORITHM")
    jwt_access_token_expire_seconds: int = Field(..., validation_alias="JWT_ACCESS_TOKEN_EXPIRE_SECONDS")
    jwt_refresh_token_expire_seconds: int = Field(..., validation_alias="JWT_REFRESH_TOKEN_EXPIRE_SECONDS")
    jwt_global_enable: bool = Field(..., validation_alias="JWT_GLOBAL_ENABLE")
    jwt_white_list: List[str] = Field(..., validation_alias="JWT_WHITE_LIST")

    file_save_path: str = Field(..., validation_alias='FILE_SAVE_PATH')
    file_public_path: str = Field(..., validation_alias='FILE_PUBLIC_PATH')

    app_version: str = Field(default="0.1.0", validation_alias="APP_VERSION")
    app_debug: bool = Field(default=False, validation_alias="APP_DEBUG")
    app_host: str = Field(default="0.0.0.0", validation_alias="APP_HOST")
    app_port: int = Field(default=7004, validation_alias="SERVER_PORT")


# 实例化配置对象
env = Settings()
settings = RedisSettings()

# 打印配置结果以验证
# print("=== Redis Settings ===")
# print(f"Host: {settings.host}")
# print(f"Port: {settings.port}")
# print(f"Password: {settings.password}")
# print(f"DB: {settings.db}")
# print("======================")