from datetime import UTC, datetime, timedelta

from app.domain.evaluations.models import PriceZone
from app.domain.market_data.models import MarketSnapshot, NormalizedPriceBar
from app.domain.rules.engine import evaluate_market_snapshot
from app.domain.rules.models import EvaluationStatus


def _build_snapshot(
    *,
    current_price: float,
    closes: list[float],
    asset_type: str = "stock",
    volumes: list[int] | None = None,
) -> MarketSnapshot:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    volumes = volumes or [2_000_000 for _ in closes]

    recent_bars = [
        NormalizedPriceBar(
            timestamp=start + timedelta(days=index),
            open=close - 1,
            high=close + 1,
            low=close - 2,
            close=close,
            volume=volumes[index],
        )
        for index, close in enumerate(closes[-10:])
    ]

    return MarketSnapshot(
        ticker="MSFT",
        asset_type=asset_type,
        currency="USD",
        exchange="NASDAQ",
        current_price=current_price,
        previous_close=closes[-1],
        historical_closes=closes,
        timestamps=[start + timedelta(days=index) for index in range(len(closes))],
        volumes=volumes,
        recent_bars=recent_bars,
        source="test",
        fetched_at=datetime.now(UTC),
    )


def test_valid_uptrend_case() -> None:
    closes = [100 + index for index in range(60)]
    snapshot = _build_snapshot(current_price=160, closes=closes)

    result = evaluate_market_snapshot(snapshot)

    assert result.status == EvaluationStatus.VALID
    assert isinstance(result.suggested_entry_zone, PriceZone)


def test_wait_overextended_case() -> None:
    closes = [100 + (index * 0.5) for index in range(60)]
    snapshot = _build_snapshot(current_price=145, closes=closes)

    result = evaluate_market_snapshot(snapshot)

    assert result.status == EvaluationStatus.WAIT
    assert any(
        "extended" in reason.lower() or "chasing" in reason.lower()
        for reason in result.reasons
    )


def test_price_within_pullback_zone_can_return_valid() -> None:
    closes = [100 + (index * 0.5) for index in range(60)]
    snapshot = _build_snapshot(current_price=128.5, closes=closes)

    result = evaluate_market_snapshot(snapshot)

    assert result.status == EvaluationStatus.VALID


def test_price_materially_below_support_zone_is_not_valid() -> None:
    closes = [100 + (index * 0.5) for index in range(60)]
    snapshot = _build_snapshot(current_price=125.0, closes=closes)

    result = evaluate_market_snapshot(snapshot)

    assert result.status in {EvaluationStatus.WAIT, EvaluationStatus.INVALID}
    assert result.status != EvaluationStatus.VALID


def test_invalid_downtrend_case() -> None:
    closes = [160 - index for index in range(60)]
    snapshot = _build_snapshot(current_price=90, closes=closes)

    result = evaluate_market_snapshot(snapshot)

    assert result.status == EvaluationStatus.INVALID


def test_unsupported_asset_case() -> None:
    closes = [100 + index for index in range(60)]
    snapshot = _build_snapshot(current_price=160, closes=closes, asset_type="crypto")

    result = evaluate_market_snapshot(snapshot)

    assert result.status == EvaluationStatus.INVALID
    assert any("unsupported" in reason.lower() for reason in result.reasons)


def test_boundary_near_extension_threshold_stays_non_invalid() -> None:
    closes = [100 + (index * 0.5) for index in range(60)]
    snapshot = _build_snapshot(current_price=137.7, closes=closes)

    result = evaluate_market_snapshot(snapshot)

    assert result.status in {EvaluationStatus.VALID, EvaluationStatus.WAIT}
    assert result.status != EvaluationStatus.INVALID
