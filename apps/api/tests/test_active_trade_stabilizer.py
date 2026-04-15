from datetime import UTC, datetime, timedelta

from app.domain.active_trades.models import GuidanceStatus
from app.domain.active_trades.service import (
    ActiveTradeInput,
    ActiveTradeStabilizerService,
    derive_expected_behavior_envelope,
)


def _make_trade(**overrides) -> ActiveTradeInput:
    payload = {
        'trade_spec_id': 'trade-msft-001',
        'ticker': 'MSFT',
        'entry_price_actual': 100.0,
        'stop_loss': 95.0,
        'target_price': 115.0,
        'time_horizon_days': 10,
        'entered_at': datetime.now(UTC) - timedelta(days=3),
        'current_price': 103.0,
    }
    payload.update(overrides)
    return ActiveTradeInput(**payload)


def test_envelope_generation_is_deterministic() -> None:
    envelope = derive_expected_behavior_envelope(_make_trade())

    assert envelope.expected_drawdown_min_percent <= envelope.expected_drawdown_max_percent
    assert envelope.expected_time_to_move_min_days >= 1
    assert envelope.expected_time_to_move_max_days >= envelope.expected_time_to_move_min_days


def test_pnl_calculations_are_correct() -> None:
    service = ActiveTradeStabilizerService()
    trade = service.build_active_trade(_make_trade(current_price=103.0))

    assert trade.pnl_percent == 3.0
    assert trade.distance_to_stop_percent == 8.0
    assert trade.distance_to_target_percent == 12.0


def test_stop_hit_logic_returns_exit_guidance() -> None:
    service = ActiveTradeStabilizerService()
    trade = service.build_active_trade(_make_trade(current_price=94.5))

    assert trade.guidance_status == GuidanceStatus.EXIT


def test_time_expiry_logic_returns_expired_guidance() -> None:
    service = ActiveTradeStabilizerService()
    trade = service.build_active_trade(
        _make_trade(
            entered_at=datetime.now(UTC) - timedelta(days=12),
            current_price=100.5,
            time_horizon_days=8,
        )
    )

    assert trade.guidance_status == GuidanceStatus.EXPIRED


def test_guidance_message_generation_for_normal_behavior() -> None:
    service = ActiveTradeStabilizerService()
    trade = service.build_active_trade(_make_trade(current_price=101.5))

    assert trade.guidance_status == GuidanceStatus.NORMAL
    assert 'expected behavior envelope' in trade.guidance_message.lower()


def test_deeper_pullback_above_stop_returns_hold_guidance() -> None:
    service = ActiveTradeStabilizerService()
    trade = service.build_active_trade(_make_trade(current_price=97.5))

    assert trade.guidance_status == GuidanceStatus.HOLD
    assert 'thesis remains intact' in trade.guidance_message.lower()
