from functools import lru_cache
from typing import Literal

from pydantic import Field, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Analytics API"
    app_version: str = "0.1.0"
    environment: Literal["development", "staging", "production"] = "development"
    api_v1_prefix: str = "/api/v1"
    secret_key: str = Field(..., min_length=32)
    log_level: str = "INFO"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    # Comma-separated origins (env: CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000)
    cors_origins: str = "http://localhost:3000"

    # Database
    database_url: str = Field(
        ...,
        description="Async PostgreSQL URL (postgresql+asyncpg://...)",
    )

    # Redis
    redis_url: RedisDsn = "redis://localhost:6379/0"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Event ingestion
    ingestion_rate_limit_per_minute: int = 10_000
    ingestion_max_batch_size: int = 500
    ingestion_csv_max_bytes: int = 10 * 1024 * 1024

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def database_url_sync(self) -> str:
        """Sync URL for Alembic migrations."""
        return self.database_url.replace("+asyncpg", "")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
