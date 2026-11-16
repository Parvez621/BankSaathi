
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "BankSaathi"
    app_env: Literal["development", "production"] = "development"

    allowed_hosts: list[str] = ["localhost", "127.0.0.1", "testserver"]
    cors_origins: list[str] = []

    speech_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
