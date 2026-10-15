
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "codexblitz-backend"
    app_env: str = "development"

    database_url: str

    openrouter_api_key: str
    openrouter_model: str

    cors_origins: list[str] = ["http://localhost:3000"]
    analyze_rate_limit_per_minute: int = Field(default=5, ge=1)
    rate_limit_storage_uri: str = "memory://"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
