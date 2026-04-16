from enum import Enum

from pydantic import BaseModel, Field

from app.domain.position_sizing.config import DEFAULT_POSITION_SIZING_CONFIG
from app.domain.trade_specs.models import TradeSpecInput


class PositionSizingStatus(str, Enum):
    READY = 'READY'
    BLOCKED = 'BLOCKED'
    NOT_FEASIBLE = 'NOT_FEASIBLE'


class PositionSizingRequest(BaseModel):
    trade: TradeSpecInput
    account_size_dollars: float = Field(..., gt=0)
    risk_percent_per_trade: float = Field(
        default=DEFAULT_POSITION_SIZING_CONFIG.default_risk_percent_per_trade,
        ge=DEFAULT_POSITION_SIZING_CONFIG.minimum_risk_percent_per_trade,
        le=DEFAULT_POSITION_SIZING_CONFIG.maximum_risk_percent_per_trade,
    )
    intended_entry_price: float = Field(..., gt=0)


class PositionSizingResult(BaseModel):
    approved_for_sizing: bool
    status: PositionSizingStatus
    account_size_dollars: float = Field(..., gt=0)
    risk_percent_per_trade: float = Field(..., gt=0)
    entry_price_used: float = Field(..., gt=0)
    risk_dollars: float = Field(..., ge=0)
    risk_per_share: float
    suggested_shares: int = Field(..., ge=0)
    capital_required: float = Field(..., ge=0)
    capital_utilization_percent: float = Field(..., ge=0)
    notes: list[str]
    warnings: list[str]
