import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pydantic import Field


# 动态确定 env 文件
def _get_env_file():
    """根据环境变量确定要加载的 .env 文件"""
    env = os.getenv("ENV", "dev")
    env_file = f".env.{env}"

    # 如果指定的环境文件不存在，尝试使用默认的 .env
    if not Path(env_file).exists():
        env_file = ".env"

    return env_file


class Settings(BaseSettings):
    # 环境配置
    ENV: str = Field(default="dev", description="运行环境")

    # 数据库配置 - 从环境变量读取（必需）
    DATABASE_URL: str = Field(..., description="数据库连接字符串")

    # JWT 配置 - 从环境变量读取（必需）
    SECRET_KEY: str = Field(..., description="JWT密钥，生产环境请使用强随机字符串")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # 应用配置
    APP_NAME: str = "Football Platform"
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=_get_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # 忽略额外的环境变量
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
