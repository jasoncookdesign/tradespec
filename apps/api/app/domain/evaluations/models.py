from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator

from app.domain.rules.models import EvaluationStatus


class AssetType(str, Enum):
    STOCK = "stock"
    ETF = "etf"
    UNKNOWN = "unknown"


class PriceZone(BaseModel):
    min_price: float = Field(..., gt=0)
    max_price: float = Field(..., gt=0)

    @model_validator(mode="after")
    def validate_range(self) -> "PriceZone":
        if self.max_price < self.min_price:
            raise ValueError("max_price must be greater than or equal to min_price")
        return self


class EvaluateTickerRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    asset_type: AssetType = AssetType.STOCK

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str) -> str:
        return value.strip().upper()


class TickerEvaluation(BaseModel):
    ticker: str
    asset_type: AssetType
    trend_summary: str
    momentum_summary: str
    structure_summary: str
    volatility_summary: str
    status: EvaluationStatus
    reasons: list[str]
    suggested_entry_zone: PriceZone
    suggested_support_zone: PriceZone
    generated_at: datetime
