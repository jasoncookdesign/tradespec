from dataclasses import dataclass
from datetime import UTC, datetime

from pydantic import BaseModel, Field

from app.domain.active_trades.config import DEFAULT_ACTIVE_TRADE_CONFIG, ActiveTradeConfig
from app.domain.active_trades.models import ActiveTrade, GuidanceStatus


@dataclass(slots=True)
class ExpectedBehaviorEnvelope:
    normal_pullback_min_pct: float
    normal_pullback_max_pct: float
    expected_time_to_move_min_days: int
    expected_time_to_move_max_days: int
    note: str


class ActiveTradeInput(BaseModel):
    trade_spec_id: str
    ticker: str
    entry_price_actual: float = Field(..., gt=0)
    stop_loss: float = Field(..., gt=0)
    target_price: float = Field(..., gt=0)
    time_horizon_days: int = Field(..., ge=1)
    entered_at: datetime
    current_price: float = Field(..., gt=0)


def derive_expected_behavior_envelope(
    trade: ActiveTradeInput,
    config: ActiveTradeConfig = DEFAULT_ACTIVE_TRADE_CONFIG,
) -> ExpectedBehaviorEnvelope:
    # Current pullback thresholds are static for MVP clarity.
    # A future refinement could scale them using volatility-aware sizing.
    expected_time_to_move_min_days = max(
        1,
        round(trade.time_horizon_days * config.expected_time_to_move_min_days_ratio),
    )
    expected_time_to_move_max_days = max(
        expected_time_to_move_min_days,
        round(trade.time_horizon_days * config.expected_time_to_move_max_days_ratio),
    )
    return ExpectedBehaviorEnvelope(
        normal_pullback_min_pct=config.default_expected_drawdown_min_percent,
        normal_pullback_max_pct=config.default_expected_drawdown_max_percent,
        expected_time_to_move_min_days=expected_time_to_move_min_days,
        expected_time_to_move_max_days=expected_time_to_move_max_days,
        note=(
            "This envelope estimates the normal pullback range and time window for "
            "a simple bullish swing setup."
        ),
    )


class ActiveTradeStabilizerService:
    def __init__(self, config: ActiveTradeConfig = DEFAULT_ACTIVE_TRADE_CONFIG):
        self._config = config

    def build_active_trade(self, trade: ActiveTradeInput) -> ActiveTrade:
        envelope = derive_expected_behavior_envelope(trade, self._config)
        elapsed_days = max(0, (datetime.now(UTC) - trade.entered_at).days)
        pnl_percent = round(
            ((trade.current_price - trade.entry_price_actual) / trade.entry_price_actual) * 100,
            2,
        )
        distance_to_stop_percent = round(
            ((trade.current_price - trade.stop_loss) / trade.entry_price_actual) * 100,
            2,
        )
        distance_to_target_percent = round(
            ((trade.target_price - trade.current_price) / trade.entry_price_actual) * 100,
            2,
        )

        thesis_intact = (
            trade.current_price > trade.stop_loss
            and elapsed_days <= trade.time_horizon_days
            and pnl_percent >= envelope.normal_pullback_min_pct
        )

        if trade.current_price <= trade.stop_loss:
            guidance_status = GuidanceStatus.EXIT
            guidance_message = 'Stop level breached. Exit immediately.'
        elif (
            elapsed_days > trade.time_horizon_days
            and pnl_percent < self._config.minimum_progress_pct_before_expiry
        ):
            guidance_status = GuidanceStatus.EXPIRED
            guidance_message = (
                'Trade has not progressed within planned time. Exit and redeploy capital.'
            )
        elif thesis_intact:
            guidance_status = GuidanceStatus.HOLD
            guidance_message = 'Pullback remains within expected range. Do not exit.'
        else:
            guidance_status = GuidanceStatus.EXIT
            guidance_message = 'Price behavior is outside the normal pullback range. Exit.'

        return ActiveTrade(
            id=f"active-{trade.ticker.lower()}-001",
            trade_spec_id=trade.trade_spec_id,
            entry_price_actual=trade.entry_price_actual,
            entered_at=trade.entered_at,
            current_price=trade.current_price,
            pnl_percent=pnl_percent,
            distance_to_stop_percent=distance_to_stop_percent,
            distance_to_target_percent=distance_to_target_percent,
            normal_pullback_min_pct=envelope.normal_pullback_min_pct,
            normal_pullback_max_pct=envelope.normal_pullback_max_pct,
            expected_time_to_move_min_days=envelope.expected_time_to_move_min_days,
            expected_time_to_move_max_days=envelope.expected_time_to_move_max_days,
            elapsed_days=elapsed_days,
            thesis_intact=thesis_intact,
            guidance_status=guidance_status,
            guidance_message=guidance_message,
        )

    def list_active_trades(self, trade_inputs: list[ActiveTradeInput]) -> list[ActiveTrade]:
        return [self.build_active_trade(trade) for trade in trade_inputs]
