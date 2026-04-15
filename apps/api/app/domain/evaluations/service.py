from datetime import UTC, datetime

from app.domain.evaluations.models import (
    AssetType,
    EvaluateTickerRequest,
    PriceZone,
    TickerEvaluation,
)
from app.domain.rules.models import EvaluationStatus


def evaluate_ticker(payload: EvaluateTickerRequest) -> TickerEvaluation:
    """Return a deterministic ticker evaluation for the current scaffold."""

    base_price = float(90 + (sum(ord(char) for char in payload.ticker) % 40))

    if payload.ticker.startswith("X"):
        status = EvaluationStatus.INVALID
        reasons = [
            "Current structure quality does not meet the minimum swing-trade standard.",
            "Momentum confirmation is missing for a new entry.",
        ]
    elif payload.ticker.endswith("Q"):
        status = EvaluationStatus.WAIT
        reasons = [
            "Trend is constructive, but confirmation is still incomplete.",
            "Waiting for a cleaner entry near support improves the setup.",
        ]
    else:
        status = EvaluationStatus.VALID
        reasons = [
            "Trend and structure are aligned for a swing-trade review.",
            "Risk can be defined cleanly against nearby support.",
        ]

    asset_label = "ETF" if payload.asset_type == AssetType.ETF else "stock"

    return TickerEvaluation(
        ticker=payload.ticker,
        asset_type=payload.asset_type,
        trend_summary=f"The {asset_label} is trading above its recent trend baseline.",
        momentum_summary="Momentum is steady but should still be confirmed at entry.",
        structure_summary="Price structure remains orderly with a definable pivot.",
        volatility_summary="Volatility is moderate enough for swing-trade planning.",
        status=status,
        reasons=reasons,
        suggested_entry_zone=PriceZone(min_price=base_price, max_price=base_price + 2),
        suggested_support_zone=PriceZone(min_price=base_price - 4, max_price=base_price - 2),
        generated_at=datetime.now(UTC),
    )
