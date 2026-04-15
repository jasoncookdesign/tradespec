from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator

from app.domain.rules.models import EvaluationStatus


class SetupType(str, Enum):
    BREAKOUT = "breakout"
    PULLBACK = "pullback"
    REVERSAL = "reversal"
    TREND_CONTINUATION = "trend-continuation"


class TradeSpecInput(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    setup_type: SetupType
    entry_zone_min: float = Field(..., gt=0)
    entry_zone_max: float = Field(..., gt=0)
    stop_loss: float = Field(..., gt=0)
    target_price: float = Field(..., gt=0)
    # TODO: Input currently allows 1..90 days while validation logic prefers 3..30.
    # Unify these constraints when the real trade-builder rules are finalized.
    time_horizon_days: int = Field(..., ge=1, le=90)
    thesis: str = Field(..., min_length=5, max_length=500)

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str) -> str:
        return value.strip().upper()

    @model_validator(mode="after")
    def validate_long_setup_levels(self) -> "TradeSpecInput":
        if self.entry_zone_max < self.entry_zone_min:
            raise ValueError("entry_zone_max must be greater than or equal to entry_zone_min")
        if self.stop_loss >= self.entry_zone_min:
            raise ValueError("stop_loss must stay below the entry zone for long setups")
        if self.target_price <= self.entry_zone_max:
            raise ValueError("target_price must sit above the entry zone for long setups")
        return self


class TradeSpec(TradeSpecInput):
    id: str
    risk_reward_ratio: float = Field(..., ge=0)
    status: EvaluationStatus
    created_at: datetime


class TradeValidationCheck(BaseModel):
    name: str
    passed: bool
    message: str


class TradeValidationResult(BaseModel):
    approved: bool
    score: int = Field(..., ge=0, le=100)
    status: EvaluationStatus
    checks: list[TradeValidationCheck]
    reasons: list[str]
    warnings: list[str]
