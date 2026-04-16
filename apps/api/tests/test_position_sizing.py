from app.domain.position_sizing.models import PositionSizingRequest, PositionSizingStatus
from app.domain.position_sizing.service import calculate_position_size
from app.domain.rules.models import EvaluationStatus
from app.domain.trade_specs.models import SetupType, TradeSpecInput


def _make_trade(**overrides) -> TradeSpecInput:
    payload = {
        'ticker': 'MSFT',
        'setup_type': SetupType.PULLBACK,
        'entry_zone_min': 100.0,
        'entry_zone_max': 102.0,
        'stop_loss': 95.0,
        'target_price': 119.0,
        'time_horizon_days': 10,
        'thesis': 'Trend pullback into support with defined risk.',
        'ticker_status': EvaluationStatus.VALID,
    }
    payload.update(overrides)
    return TradeSpecInput(**payload)


def test_position_sizing_happy_path() -> None:
    result = calculate_position_size(
        PositionSizingRequest(
            trade=_make_trade(),
            account_size_dollars=10_000,
            risk_percent_per_trade=1.0,
            intended_entry_price=101.0,
        )
    )

    assert result.approved_for_sizing is True
    assert result.status == PositionSizingStatus.READY
    assert result.entry_price_used == 101.0
    assert result.risk_dollars == 100.0
    assert result.risk_per_share == 6.0
    assert result.suggested_shares == 16
    assert result.capital_required == 1616.0


def test_non_approved_trade_cannot_be_sized() -> None:
    result = calculate_position_size(
        PositionSizingRequest(
            trade=_make_trade(ticker_status=EvaluationStatus.WAIT),
            account_size_dollars=10_000,
            risk_percent_per_trade=1.0,
            intended_entry_price=101.0,
        )
    )

    assert result.approved_for_sizing is False
    assert result.status == PositionSizingStatus.BLOCKED
    assert any('approved' in warning.lower() for warning in result.warnings)


def test_zero_or_negative_risk_per_share_fails() -> None:
    result = calculate_position_size(
        PositionSizingRequest(
            trade=_make_trade(),
            account_size_dollars=10_000,
            risk_percent_per_trade=1.0,
            intended_entry_price=95.0,
        )
    )

    assert result.approved_for_sizing is False
    assert result.status == PositionSizingStatus.BLOCKED
    assert any('risk per share' in warning.lower() for warning in result.warnings)


def test_insufficient_capital_returns_clear_warning() -> None:
    result = calculate_position_size(
        PositionSizingRequest(
            trade=_make_trade(stop_loss=99.0, target_price=108.0),
            account_size_dollars=1_000,
            risk_percent_per_trade=5.0,
            intended_entry_price=100.0,
        )
    )

    assert result.approved_for_sizing is False
    assert result.status == PositionSizingStatus.NOT_FEASIBLE
    assert result.capital_required > result.account_size_dollars
    assert any('not feasible' in warning.lower() for warning in result.warnings)


def test_share_count_rounds_down() -> None:
    result = calculate_position_size(
        PositionSizingRequest(
            trade=_make_trade(),
            account_size_dollars=10_000,
            risk_percent_per_trade=1.0,
            intended_entry_price=101.0,
        )
    )

    assert result.suggested_shares == 16
    assert any('floored' in note.lower() for note in result.notes)
