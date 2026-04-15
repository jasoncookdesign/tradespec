from datetime import UTC, datetime, timedelta

from app.domain.active_trades.service import ActiveTradeInput


class InMemoryActiveTradeRepository:
    """Simple MVP repository seam for locally tracked active trades."""

    def list_active_trade_inputs(self) -> list[ActiveTradeInput]:
        entered_at = datetime.now(UTC) - timedelta(days=3)
        return [
            ActiveTradeInput(
                trade_spec_id="trade-msft-001",
                ticker="MSFT",
                entry_price_actual=101.2,
                stop_loss=96.0,
                target_price=112.0,
                time_horizon_days=10,
                entered_at=entered_at,
                current_price=104.8,
            )
        ]
