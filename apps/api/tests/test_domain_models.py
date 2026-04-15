import pytest
from pydantic import ValidationError

from app.domain.rules.models import EvaluationStatus
from app.domain.trade_specs.models import TradeSpecInput


def test_evaluation_status_values_remain_stable() -> None:
    assert EvaluationStatus.VALID.value == "VALID"
    assert EvaluationStatus.WAIT.value == "WAIT"
    assert EvaluationStatus.INVALID.value == "INVALID"


def test_trade_spec_input_rejects_inverted_entry_zone() -> None:
    with pytest.raises(ValidationError):
        TradeSpecInput(
            ticker="MSFT",
            setup_type="breakout",
            entry_zone_min=110,
            entry_zone_max=100,
            stop_loss=95,
            target_price=130,
            time_horizon_days=10,
            thesis="Trend continuation above resistance.",
        )
