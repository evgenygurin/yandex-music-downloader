"""Application configuration using Pydantic Settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "DJ AI Studio API"
    debug: bool = False

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/dj_ai_studio.db"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    # Yandex Music
    yandex_token: str | None = None
    yandex_timeout: int = 20
    yandex_max_retries: int = 3


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
