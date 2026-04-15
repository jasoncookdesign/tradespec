from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class RawPriceBar(BaseModel):
    timestamp: datetime
    open: float = Field(..., ge=0)
    high: float = Field(..., ge=0)
    low: float = Field(..., ge=0)
    close: float = Field(..., ge=0)
    volume: int = Field(..., ge=0)


class ProviderSecurityData(BaseModel):
    symbol: str
    asset_type: str = "unknown"
    currency: str = "USD"
    exchange: str = "UNKNOWN"
    latest_price: float = Field(..., gt=0)
    previous_close: float = Field(..., gt=0)
    history: list[RawPriceBar]
    source: str

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        return value.strip().upper()


class NormalizedPriceBar(RawPriceBar):
    """Application-facing OHLCV bar."""


class MarketSnapshot(BaseModel):
    ticker: str
    asset_type: str
    currency: str
    exchange: str
    current_price: float = Field(..., gt=0)
    previous_close: float = Field(..., gt=0)
    historical_closes: list[float]
    timestamps: list[datetime]
    volumes: list[int] | None = None
    recent_bars: list[NormalizedPriceBar]
    source: str
    fetched_at: datetime
