from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.domain.rules.models import EvaluationStatus
from app.domain.trade_specs.config import DEFAULT_TRADE_VALIDATION_CONFIG, TradeValidationConfig
from app.domain.trade_specs.models import (
    TradeSpec,
    TradeSpecInput,
    TradeValidationCheck,
    TradeValidationResult,
)
from app.domain.trade_specs.repository import SQLiteTradeSpecRepository


def _calculate_risk_reward_ratio(payload: TradeSpecInput) -> float:
    midpoint = (payload.entry_zone_min + payload.entry_zone_max) / 2
    risk = midpoint - payload.stop_loss
    reward = payload.target_price - midpoint
    return round(reward / risk, 2)


def build_trade_spec(payload: TradeSpecInput) -> TradeSpec:
    ratio = _calculate_risk_reward_ratio(payload)

    if payload.ticker_status == EvaluationStatus.INVALID:
        status = EvaluationStatus.INVALID
    elif payload.ticker_status == EvaluationStatus.WAIT or ratio < 2.0:
        status = EvaluationStatus.WAIT if ratio >= 1.2 else EvaluationStatus.INVALID
        if payload.ticker_status == EvaluationStatus.WAIT:
            status = EvaluationStatus.WAIT
    else:
        status = EvaluationStatus.VALID

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


def validate_trade(
    payload: TradeSpecInput,
    config: TradeValidationConfig = DEFAULT_TRADE_VALIDATION_CONFIG,
) -> TradeValidationResult:
    trade_spec = build_trade_spec(payload)

    checks = [
        TradeValidationCheck(
            name="ticker_status",
            passed=payload.ticker_status != EvaluationStatus.INVALID,
            message=(
                "Ticker evaluation must not be INVALID before entering the trade builder."
            ),
        ),
        TradeValidationCheck(
            name="entry_zone_order",
            passed=payload.entry_zone_max >= payload.entry_zone_min,
            message="Entry zone bounds are logically ordered.",
        ),
        TradeValidationCheck(
            name="risk_reward",
            passed=trade_spec.risk_reward_ratio >= config.minimum_risk_reward_ratio,
            message=f"Risk/reward ratio is {trade_spec.risk_reward_ratio}.",
        ),
        TradeValidationCheck(
            name="time_horizon",
            passed=(
                config.preferred_time_horizon_min_days
                <= payload.time_horizon_days
                <= config.preferred_time_horizon_max_days
            ),
            message="Time horizon fits the intended swing-trade window.",
        ),
    ]

    passed_checks = sum(1 for check in checks if check.passed)
    score = int(round((passed_checks / len(checks)) * 100))

    reasons = [check.message for check in checks if not check.passed]
    warnings = []
    if payload.ticker_status == EvaluationStatus.WAIT:
        warnings.append(
            "Ticker status is WAIT, so the plan can be reviewed but should not be entered yet."
        )
    if trade_spec.risk_reward_ratio < config.minimum_risk_reward_ratio:
        warnings.append("Risk/reward is below the preferred 2.0 threshold.")
    if payload.time_horizon_days > 20:
        warnings.append("Longer holds may require more patience and wider normal swings.")

    approved = (
        payload.ticker_status == EvaluationStatus.VALID
        and trade_spec.risk_reward_ratio >= config.minimum_risk_reward_ratio
        and config.preferred_time_horizon_min_days
        <= payload.time_horizon_days
        <= config.preferred_time_horizon_max_days
    )

    if payload.ticker_status == EvaluationStatus.INVALID:
        status = EvaluationStatus.INVALID
    elif approved:
        status = EvaluationStatus.VALID
    else:
        status = EvaluationStatus.WAIT

    return TradeValidationResult(
        approved=approved,
        score=score,
        status=status,
        checks=checks,
        reasons=reasons,
        warnings=warnings,
    )


def create_trade_spec(payload: TradeSpecInput) -> TradeSpec:
    trade_spec = build_trade_spec(payload)
    repository = SQLiteTradeSpecRepository(Path("tradespec.db"))
    return repository.save(trade_spec)
