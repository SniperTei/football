from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pydantic import Field


class Settings(BaseSettings):
    # 数据库配置 - 必须从环境变量读取
    DATABASE_URL: str = Field(..., description="数据库连接字符串")

    # JWT 配置 - 必须从环境变量读取
    SECRET_KEY: str = Field(..., description="JWT密钥，生产环境请使用强随机字符串")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # 应用配置
    APP_NAME: str = "Football Platform"
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
