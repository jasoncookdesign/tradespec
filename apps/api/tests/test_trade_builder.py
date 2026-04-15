from pathlib import Path

import pytest
from pydantic import ValidationError

from app.domain.rules.models import EvaluationStatus
from app.domain.trade_specs.models import SetupType, TradeSpecInput
from app.domain.trade_specs.repository import SQLiteTradeSpecRepository
from app.domain.trade_specs.service import build_trade_spec, validate_trade


def _make_payload(**overrides) -> TradeSpecInput:
    payload = {
        "ticker": "MSFT",
        "setup_type": SetupType.PULLBACK,
        "entry_zone_min": 100.0,
        "entry_zone_max": 102.0,
        "stop_loss": 95.0,
        "target_price": 114.0,
        "time_horizon_days": 10,
        "thesis": "Trend pullback into support with defined risk.",
        "ticker_status": EvaluationStatus.VALID,
    }
    payload.update(overrides)
    return TradeSpecInput(**payload)


def test_risk_reward_calculation() -> None:
    trade = build_trade_spec(_make_payload())

    assert trade.risk_reward_ratio == 2.17


def test_validation_rules_block_weak_risk_reward() -> None:
    result = validate_trade(_make_payload(target_price=106.0))

    assert result.approved is False
    assert any("risk/reward" in reason.lower() for reason in result.reasons)


def test_time_horizon_input_is_limited_to_swing_window() -> None:
    with pytest.raises(ValidationError):
        _make_payload(time_horizon_days=45)


def test_wait_ticker_status_keeps_plan_visible_but_not_approved() -> None:
    result = validate_trade(_make_payload(ticker_status=EvaluationStatus.WAIT))

    assert result.status == EvaluationStatus.WAIT
    assert result.approved is False


def test_invalid_ticker_status_blocks_builder() -> None:
    result = validate_trade(_make_payload(ticker_status=EvaluationStatus.INVALID))

    assert result.status == EvaluationStatus.INVALID
    assert result.approved is False
    assert any("ticker evaluation" in reason.lower() for reason in result.reasons)


def test_risk_reward_tiers_raise_score_meaningfully() -> None:
    weak = validate_trade(_make_payload(target_price=114.0))
    good = validate_trade(_make_payload(target_price=119.0))
    strong = validate_trade(_make_payload(target_price=125.0))

    assert weak.approved is True
    assert good.approved is True
    assert strong.approved is True
    assert weak.score < good.score < strong.score


def test_hard_failures_override_other_positive_signals() -> None:
    result = validate_trade(
        _make_payload(
            ticker_status=EvaluationStatus.WAIT,
            target_price=125.0,
            time_horizon_days=10,
        )
    )

    assert result.approved is False
    assert result.status == EvaluationStatus.WAIT
    assert any(
        check.name == "evaluation_status" and check.passed is False
        for check in result.checks
    )
    assert any("must be valid" in reason.lower() for reason in result.reasons)


def test_persistence_happy_path(tmp_path: Path) -> None:
    db_path = tmp_path / 'tradespec.sqlite'
    repository = SQLiteTradeSpecRepository(db_path)
    trade = build_trade_spec(_make_payload())

    saved = repository.save(trade)
    loaded = repository.get_by_id(trade.id)

    assert saved.id == trade.id
    assert loaded is not None
    assert loaded.ticker == 'MSFT'


def test_required_fields_still_validate() -> None:
    with pytest.raises(ValidationError):
        TradeSpecInput(
            ticker='',
            setup_type=SetupType.PULLBACK,
            entry_zone_min=100,
            entry_zone_max=101,
            stop_loss=99,
            target_price=105,
            time_horizon_days=10,
            thesis='bad',
            ticker_status=EvaluationStatus.VALID,
        )
