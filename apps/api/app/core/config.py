from functools import lru_cache
from typing import Annotated, Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings for local development and future deployment."""

    app_name: str = "TradeSpec API"
    environment: str = "development"
    api_v1_prefix: str = "/api"
    allowed_origins: Annotated[list[str], NoDecode] = ["http://localhost:3000"]
    sqlite_url: str = "sqlite:///./tradespec.db"
    market_data_provider: Literal["yahoo-finance"] = "yahoo-finance"
    market_data_cache_ttl_seconds: int = 300
    ai_provider: Literal["stub"] = "stub"

    model_config = SettingsConfigDict(
        env_prefix="TRADESPEC_",
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        return [item.strip() for item in value.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
