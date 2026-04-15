from datetime import UTC, datetime, timedelta

import pytest

from app.domain.market_data.errors import InvalidTickerError, ProviderUnavailableError
from app.domain.market_data.models import (
    MarketSnapshot,
    NormalizedPriceBar,
    ProviderSecurityData,
    RawPriceBar,
)
from app.domain.market_data.service import NormalizedMarketDataService


class StubMarketProvider:
    def __init__(self, payload=None, error=None):
        self.payload = payload
        self.error = error
        self.calls = 0

    def fetch_security_data(self, symbol: str, lookback_days: int = 60) -> ProviderSecurityData:
        self.calls += 1
        if self.error is not None:
            raise self.error
        return self.payload


class StubNormalizer:
    def __init__(self, snapshot: MarketSnapshot):
        self.snapshot = snapshot
        self.calls = 0

    def normalize(self, raw_data: ProviderSecurityData) -> MarketSnapshot:
        self.calls += 1
        return self.snapshot.model_copy(update={"ticker": raw_data.symbol})


def _build_history(days: int = 60) -> list[RawPriceBar]:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    bars: list[RawPriceBar] = []
    for idx in range(days):
        close = 100 + idx
        bars.append(
            RawPriceBar(
                timestamp=start + timedelta(days=idx),
                open=close - 1,
                high=close + 1,
                low=close - 2,
                close=close,
                volume=1_000_000 + idx,
            )
        )
    return bars


def _build_snapshot() -> MarketSnapshot:
    history = _build_history(60)
    return MarketSnapshot(
        ticker="MSFT",
        asset_type="stock",
        currency="USD",
        exchange="NASDAQ",
        current_price=159.0,
        previous_close=158.0,
        historical_closes=[bar.close for bar in history],
        timestamps=[bar.timestamp for bar in history],
        volumes=[bar.volume for bar in history],
        recent_bars=[NormalizedPriceBar(**bar.model_dump()) for bar in history[-10:]],
        source="stub-yahoo",
        fetched_at=datetime.now(UTC),
    )


def test_service_uses_provider_and_normalizer_together() -> None:
    provider = StubMarketProvider(
        ProviderSecurityData(
            symbol="MSFT",
            asset_type="stock",
            currency="USD",
            exchange="NASDAQ",
            latest_price=159.0,
            previous_close=158.0,
            history=_build_history(60),
            source="stub-yahoo",
        )
    )
    normalizer = StubNormalizer(_build_snapshot())
    service = NormalizedMarketDataService(provider, normalizer=normalizer, cache_ttl_seconds=60)

    snapshot = service.get_market_snapshot("MSFT")

    assert snapshot.ticker == "MSFT"
    assert snapshot.current_price == 159.0
    assert provider.calls == 1
    assert normalizer.calls == 1


def test_invalid_ticker_handling_is_explicit() -> None:
    service = NormalizedMarketDataService(
        StubMarketProvider(error=InvalidTickerError("Ticker was not found")),
        normalizer=StubNormalizer(_build_snapshot()),
    )

    with pytest.raises(InvalidTickerError):
        service.get_market_snapshot("BAD")


def test_service_uses_cache_for_repeated_requests() -> None:
    provider = StubMarketProvider(
        ProviderSecurityData(
            symbol="MSFT",
            asset_type="stock",
            currency="USD",
            exchange="NASDAQ",
            latest_price=159.0,
            previous_close=158.0,
            history=_build_history(60),
            source="stub-yahoo",
        )
    )
    normalizer = StubNormalizer(_build_snapshot())
    service = NormalizedMarketDataService(provider, normalizer=normalizer, cache_ttl_seconds=300)

    first = service.get_market_snapshot("MSFT")
    second = service.get_market_snapshot("MSFT")

    assert first.ticker == second.ticker
    assert provider.calls == 1
    assert normalizer.calls == 1


def test_provider_failures_are_wrapped_cleanly() -> None:
    service = NormalizedMarketDataService(
        StubMarketProvider(error=RuntimeError("upstream timeout")),
        normalizer=StubNormalizer(_build_snapshot()),
    )

    with pytest.raises(ProviderUnavailableError):
        service.get_market_snapshot("MSFT")
