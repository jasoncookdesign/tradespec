from datetime import UTC, datetime, timedelta

import pytest

from app.domain.market_data.errors import InsufficientDataError
from app.domain.market_data.models import ProviderSecurityData, RawPriceBar
from app.domain.market_data.normalizer import MarketSnapshotNormalizer


def _build_history(days: int = 60) -> list[RawPriceBar]:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    return [
        RawPriceBar(
            timestamp=start + timedelta(days=idx),
            open=100 + idx,
            high=101 + idx,
            low=99 + idx,
            close=100.5 + idx,
            volume=1_000_000 + idx,
        )
        for idx in range(days)
    ]


def test_normalizer_creates_provider_agnostic_market_snapshot() -> None:
    normalizer = MarketSnapshotNormalizer()
    raw_data = ProviderSecurityData(
        symbol="MSFT",
        asset_type="stock",
        currency="USD",
        exchange="NASDAQ",
        latest_price=159.0,
        previous_close=158.0,
        history=_build_history(60),
        source="stub-yahoo",
    )

    snapshot = normalizer.normalize(raw_data)

    assert snapshot.ticker == "MSFT"
    assert snapshot.current_price == 159.0
    assert len(snapshot.historical_closes) == 60
    assert len(snapshot.timestamps) == 60
    assert snapshot.volumes is not None


def test_normalizer_rejects_insufficient_history() -> None:
    normalizer = MarketSnapshotNormalizer()
    raw_data = ProviderSecurityData(
        symbol="MSFT",
        asset_type="stock",
        currency="USD",
        exchange="NASDAQ",
        latest_price=101.0,
        previous_close=100.0,
        history=_build_history(10),
        source="stub-yahoo",
    )

    with pytest.raises(InsufficientDataError):
        normalizer.normalize(raw_data)
