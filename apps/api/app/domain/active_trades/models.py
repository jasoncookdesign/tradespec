from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class GuidanceStatus(str, Enum):
    HOLD = "HOLD"
    EXIT = "EXIT"
    EXPIRED = "EXPIRED"


class ActiveTrade(BaseModel):
    id: str
    trade_spec_id: str
    entry_price_actual: float = Field(..., gt=0)
    entered_at: datetime
    current_price: float = Field(..., gt=0)
    pnl_percent: float
    distance_to_stop_percent: float
    distance_to_target_percent: float
    normal_pullback_min_pct: float
    normal_pullback_max_pct: float
    expected_time_to_move_min_days: int = Field(..., ge=1)
    expected_time_to_move_max_days: int = Field(..., ge=1)
    elapsed_days: int = Field(..., ge=0)
    thesis_intact: bool
    guidance_status: GuidanceStatus
    guidance_message: str
