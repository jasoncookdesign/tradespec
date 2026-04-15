from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.domain.active_trades.models import ActiveTrade, GuidanceStatus


@dataclass(slots=True)
class ExpectedBehaviorEnvelope:
    """Represents the normal price behavior range after a trade is opened."""

    thesis_holds: bool
    note: str


class ActiveTradeStabilizerService:
    def evaluate_behavior(self) -> ExpectedBehaviorEnvelope:
        return ExpectedBehaviorEnvelope(
            thesis_holds=True,
            note="Price action remains inside the expected swing-trade envelope.",
        )

    def list_active_trades(self) -> list[ActiveTrade]:
        entered_at = datetime.now(UTC) - timedelta(days=3)
        return [
            ActiveTrade(
                id="active-msft-001",
                trade_spec_id="trade-msft-001",
                entry_price_actual=101.2,
                entered_at=entered_at,
                current_price=104.8,
                pnl_percent=3.56,
                distance_to_stop_percent=5.14,
                distance_to_target_percent=6.87,
                expected_drawdown_min_percent=-1.5,
                expected_drawdown_max_percent=-4.0,
                expected_time_to_move_min_days=2,
                expected_time_to_move_max_days=7,
                guidance_status=GuidanceStatus.ON_PLAN,
                guidance_message="Trade is behaving normally relative to the original plan.",
            )
        ]
