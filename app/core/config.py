"""Typed configuration loaded only from environment variables or a local .env file."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings; secrets must be injected through the environment."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="EDUKNOWLEDGE_", extra="ignore"
    )

    app_name: str = "EduKnowledge AI"
    environment: Literal["development", "test", "staging", "production"] = "development"
    debug: bool = False
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1, le=65535)
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    database_url: PostgresDsn = "postgresql+asyncpg://eduknowledge:eduknowledge@localhost:5432/eduknowledge"  # type: ignore[assignment]
    redis_url: RedisDsn = RedisDsn("redis://localhost:6379/0")

    jwt_secret_key: SecretStr = SecretStr("change-me-in-development")
    jwt_algorithm: str = "HS256"
    jwt_access_token_minutes: int = Field(default=30, ge=1, le=1440)


@lru_cache
def get_settings() -> Settings:
    """Return a process-wide immutable settings instance."""
    return Settings()
