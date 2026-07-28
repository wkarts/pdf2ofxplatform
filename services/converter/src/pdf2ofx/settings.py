from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PDF2OFX_",
        case_sensitive=False,
        extra="ignore",
    )

    env: str = "production"
    api_key: str = Field(min_length=16)
    redis_url: str = "redis://redis:6379/0"
    data_dir: Path = Path("/data/jobs")
    max_file_size: int = 52_428_800
    max_pages: int = Field(default=200, ge=1, le=1000)
    job_ttl_hours: int = Field(default=24, ge=1, le=168)
    ocr_enabled: bool = True
    ocr_language: str = "por"
    ocr_dpi: int = Field(default=180, ge=150, le=400)
    ocr_psm: int = Field(default=6, ge=3, le=13)
    ocr_workers: int = Field(default=1, ge=1, le=8)
    ocr_page_timeout_seconds: int = Field(default=180, ge=30, le=600)
    celery_eager: bool = False
    cors_origins: list[str] = []

    @field_validator("data_dir")
    @classmethod
    def create_data_dir(cls, value: Path) -> Path:
        value.mkdir(parents=True, exist_ok=True)
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
