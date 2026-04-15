from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class GuidanceStatus(str, Enum):
    # TODO: These active-trade guidance states are provisional and will likely be
    # refined when the stabilizer logic is expanded in Step 6.
    ON_PLAN = "ON_PLAN"
    CAUTION = "CAUTION"
    REVIEW_EXIT = "REVIEW_EXIT"


class ActiveTrade(BaseModel):
    id: str
    trade_spec_id: str
    entry_price_actual: float = Field(..., gt=0)
    entered_at: datetime
    current_price: float = Field(..., gt=0)
    pnl_percent: float
    distance_to_stop_percent: float
    distance_to_target_percent: float
    expected_drawdown_min_percent: float
    expected_drawdown_max_percent: float
    expected_time_to_move_min_days: int = Field(..., ge=1)
    expected_time_to_move_max_days: int = Field(..., ge=1)
    guidance_status: GuidanceStatus
    guidance_message: str
