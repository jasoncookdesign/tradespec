from datetime import UTC, datetime
from uuid import uuid4

from app.domain.rules.models import EvaluationStatus
from app.domain.trade_specs.models import (
    TradeSpec,
    TradeSpecInput,
    TradeValidationCheck,
    TradeValidationResult,
)


def build_trade_spec(payload: TradeSpecInput) -> TradeSpec:
    midpoint = (payload.entry_zone_min + payload.entry_zone_max) / 2
    risk = midpoint - payload.stop_loss
    reward = payload.target_price - midpoint
    ratio = round(reward / risk, 2)

    if ratio >= 2.0:
        status = EvaluationStatus.VALID
    elif ratio >= 1.2:
        status = EvaluationStatus.WAIT
    else:
        status = EvaluationStatus.INVALID

    return TradeSpec(
        id=f"trade-{payload.ticker.lower()}-{str(uuid4())[:8]}",
        ticker=payload.ticker,
        setup_type=payload.setup_type,
        entry_zone_min=payload.entry_zone_min,
        entry_zone_max=payload.entry_zone_max,
        stop_loss=payload.stop_loss,
        target_price=payload.target_price,
        time_horizon_days=payload.time_horizon_days,
        thesis=payload.thesis,
        risk_reward_ratio=ratio,
        status=status,
        created_at=datetime.now(UTC),
    )


def validate_trade(payload: TradeSpecInput) -> TradeValidationResult:
    trade_spec = build_trade_spec(payload)

    checks = [
        TradeValidationCheck(
            name="entry_zone_order",
            passed=payload.entry_zone_max >= payload.entry_zone_min,
            message="Entry zone bounds are logically ordered.",
        ),
        TradeValidationCheck(
            name="risk_reward",
            passed=trade_spec.risk_reward_ratio >= 2.0,
            message=f"Risk/reward ratio is {trade_spec.risk_reward_ratio}.",
        ),
        TradeValidationCheck(
            name="time_horizon",
            passed=3 <= payload.time_horizon_days <= 30,
            message="Time horizon fits the intended swing-trade window.",
        ),
    ]

    score = sum(34 for check in checks if check.passed)
    score = min(score, 100)

    reasons = [check.message for check in checks if not check.passed]
    warnings = []
    if trade_spec.risk_reward_ratio < 2.0:
        warnings.append("Risk/reward is below the preferred 2.0 threshold.")
    if payload.time_horizon_days > 20:
        warnings.append("Longer holds may require more patience and wider normal swings.")

    approved = trade_spec.status == EvaluationStatus.VALID

    return TradeValidationResult(
        approved=approved,
        score=score,
        status=trade_spec.status,
        checks=checks,
        reasons=reasons,
        warnings=warnings,
    )
