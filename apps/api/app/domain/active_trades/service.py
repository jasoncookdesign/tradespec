from dataclasses import dataclass
from datetime import UTC, datetime

from pydantic import BaseModel, Field

from app.domain.active_trades.config import DEFAULT_ACTIVE_TRADE_CONFIG, ActiveTradeConfig
from app.domain.active_trades.models import ActiveTrade, GuidanceStatus


@dataclass(slots=True)
class ExpectedBehaviorEnvelope:
    expected_drawdown_min_percent: float
    expected_drawdown_max_percent: float
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
    expected_time_to_move_min_days = max(
        1,
        round(trade.time_horizon_days * config.expected_time_to_move_min_days_ratio),
    )
    expected_time_to_move_max_days = max(
        expected_time_to_move_min_days,
        round(trade.time_horizon_days * config.expected_time_to_move_max_days_ratio),
    )
    return ExpectedBehaviorEnvelope(
        expected_drawdown_min_percent=config.default_expected_drawdown_min_percent,
        expected_drawdown_max_percent=config.default_expected_drawdown_max_percent,
        expected_time_to_move_min_days=expected_time_to_move_min_days,
        expected_time_to_move_max_days=expected_time_to_move_max_days,
        note="Expected behavior is based on a simple swing-trade envelope for the MVP.",
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

        if trade.current_price <= trade.stop_loss:
            guidance_status = GuidanceStatus.EXIT
            guidance_message = "Stop loss has been reached. Exit and protect capital."
        elif (
            elapsed_days > trade.time_horizon_days
            and pnl_percent < self._config.minimum_progress_pct_before_expiry
        ):
            guidance_status = GuidanceStatus.EXPIRED
            guidance_message = (
                "The trade has exceeded its time horizon without enough progress."
            )
        elif pnl_percent >= envelope.expected_drawdown_max_percent:
            guidance_status = GuidanceStatus.HOLD
            guidance_message = (
                "The trade is behaving normally and remains within its expected envelope."
            )
        else:
            guidance_status = GuidanceStatus.NORMAL
            guidance_message = "Price action is still acceptable, but monitor the thesis closely."

        return ActiveTrade(
            id=f"active-{trade.ticker.lower()}-001",
            trade_spec_id=trade.trade_spec_id,
            entry_price_actual=trade.entry_price_actual,
            entered_at=trade.entered_at,
            current_price=trade.current_price,
            pnl_percent=pnl_percent,
            distance_to_stop_percent=distance_to_stop_percent,
            distance_to_target_percent=distance_to_target_percent,
            expected_drawdown_min_percent=envelope.expected_drawdown_min_percent,
            expected_drawdown_max_percent=envelope.expected_drawdown_max_percent,
            expected_time_to_move_min_days=envelope.expected_time_to_move_min_days,
            expected_time_to_move_max_days=envelope.expected_time_to_move_max_days,
            elapsed_days=elapsed_days,
            guidance_status=guidance_status,
            guidance_message=guidance_message,
        )

    def list_active_trades(self, trade_inputs: list[ActiveTradeInput]) -> list[ActiveTrade]:
        return [self.build_active_trade(trade) for trade in trade_inputs]
