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
    ValidationSeverity,
)
from app.domain.trade_specs.repository import SQLiteTradeSpecRepository


def _entry_midpoint(payload: TradeSpecInput) -> float:
    return (payload.entry_zone_min + payload.entry_zone_max) / 2


def _calculate_risk_reward_ratio(payload: TradeSpecInput) -> float:
    midpoint = _entry_midpoint(payload)
    risk = midpoint - payload.stop_loss
    reward = payload.target_price - midpoint
    if risk <= 0:
        return 0.0
    return round(reward / risk, 2)


def _calculate_stop_distance_percent(payload: TradeSpecInput) -> float:
    midpoint = _entry_midpoint(payload)
    return round(((midpoint - payload.stop_loss) / midpoint) * 100, 2)


def _calculate_entry_zone_width_percent(payload: TradeSpecInput) -> float:
    midpoint = _entry_midpoint(payload)
    return round(((payload.entry_zone_max - payload.entry_zone_min) / midpoint) * 100, 2)


def build_trade_spec(payload: TradeSpecInput) -> TradeSpec:
    ratio = _calculate_risk_reward_ratio(payload)

    if payload.ticker_status == EvaluationStatus.INVALID:
        status = EvaluationStatus.INVALID
    elif payload.ticker_status != EvaluationStatus.VALID or ratio < 2.0:
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
    stop_distance_percent = _calculate_stop_distance_percent(payload)
    entry_zone_width_percent = _calculate_entry_zone_width_percent(payload)

    checks = [
        TradeValidationCheck(
            name="evaluation_status",
            passed=payload.ticker_status == EvaluationStatus.VALID,
            severity=ValidationSeverity.HARD,
            message=(
                "Ticker evaluation must be VALID before this plan can be approved."
                if payload.ticker_status != EvaluationStatus.VALID
                else "Pre-trade evaluation is aligned with approval gating."
            ),
        ),
        TradeValidationCheck(
            name="price_structure",
            passed=(
                payload.entry_zone_max >= payload.entry_zone_min
                and payload.stop_loss < payload.entry_zone_min
                and payload.target_price > payload.entry_zone_max
            ),
            severity=ValidationSeverity.HARD,
            message="Entry, stop, and target levels must form a valid long setup.",
        ),
        TradeValidationCheck(
            name="risk_reward_floor",
            passed=trade_spec.risk_reward_ratio >= config.minimum_risk_reward_ratio,
            severity=ValidationSeverity.HARD,
            message=(
                f"Risk/reward is {trade_spec.risk_reward_ratio}, below the 2.0 minimum."
                if trade_spec.risk_reward_ratio < config.minimum_risk_reward_ratio
                else f"Risk/reward clears the minimum floor at {trade_spec.risk_reward_ratio}."
            ),
        ),
        TradeValidationCheck(
            name="time_horizon",
            passed=(
                config.accepted_time_horizon_min_days
                <= payload.time_horizon_days
                <= config.accepted_time_horizon_max_days
            ),
            severity=ValidationSeverity.HARD,
            message=(
                "Time horizon must stay between "
                f"{config.accepted_time_horizon_min_days} and "
                f"{config.accepted_time_horizon_max_days} days."
            ),
        ),
    ]

    if trade_spec.risk_reward_ratio <= config.weak_risk_reward_ratio_ceiling:
        checks.append(
            TradeValidationCheck(
                name="risk_reward_quality",
                passed=False,
                severity=ValidationSeverity.SOFT,
                message=(
                    "Risk/reward is only marginal at "
                    f"{trade_spec.risk_reward_ratio}; stronger setups are "
                    f"usually above {config.weak_risk_reward_ratio_ceiling}."
                ),
            )
        )
    else:
        checks.append(
            TradeValidationCheck(
                name="risk_reward_quality",
                passed=True,
                severity=ValidationSeverity.SOFT,
                message="Risk/reward quality is comfortably above the marginal tier.",
            )
        )

    checks.append(
        TradeValidationCheck(
            name="stop_width",
            passed=stop_distance_percent <= config.max_stop_distance_percent,
            severity=ValidationSeverity.SOFT,
            message=(
                (
                    f"Stop distance is {stop_distance_percent}% from the "
                    "entry midpoint, which is wider than preferred."
                )
                if stop_distance_percent > config.max_stop_distance_percent
                else "Stop distance is reasonably contained for a swing entry."
            ),
        )
    )
    checks.append(
        TradeValidationCheck(
            name="entry_zone_precision",
            passed=entry_zone_width_percent <= config.max_entry_zone_width_percent,
            severity=ValidationSeverity.SOFT,
            message=(
                f"Entry zone spans {entry_zone_width_percent}% of price, which weakens precision."
                if entry_zone_width_percent > config.max_entry_zone_width_percent
                else "Entry zone is tight enough to support disciplined execution."
            ),
        )
    )

    hard_failures = [
        check for check in checks if check.severity == ValidationSeverity.HARD and not check.passed
    ]
    soft_failures = [
        check for check in checks if check.severity == ValidationSeverity.SOFT and not check.passed
    ]

    score = 0
    if not hard_failures:
        score += 60
    else:
        hard_passes = sum(
            1 for check in checks if check.severity == ValidationSeverity.HARD and check.passed
        )
        score += hard_passes * 15

    if trade_spec.risk_reward_ratio > config.strong_risk_reward_ratio_floor:
        score += 30
    elif trade_spec.risk_reward_ratio > config.weak_risk_reward_ratio_ceiling:
        score += 22
    elif trade_spec.risk_reward_ratio >= config.minimum_risk_reward_ratio:
        score += 10

    if stop_distance_percent <= config.max_stop_distance_percent:
        score += 5
    if entry_zone_width_percent <= config.max_entry_zone_width_percent:
        score += 5

    score = max(0, min(100, score))

    reasons = [check.message for check in hard_failures][:3]
    warnings = [check.message for check in soft_failures][:3]
    approved = len(hard_failures) == 0

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
