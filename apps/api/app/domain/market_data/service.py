from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Protocol

from app.domain.market_data.config import DEFAULT_LOOKBACK_DAYS
from app.domain.market_data.errors import (
    InsufficientDataError,
    InvalidTickerError,
    ProviderUnavailableError,
)
from app.domain.market_data.models import MarketSnapshot, ProviderSecurityData
from app.domain.market_data.normalizer import MarketDataNormalizer, MarketSnapshotNormalizer


class MarketDataProvider(Protocol):
    def fetch_security_data(
        self,
        symbol: str,
        lookback_days: int = DEFAULT_LOOKBACK_DAYS,
    ) -> ProviderSecurityData:
        """Return provider-native market data as a raw transport object."""


class MarketDataService(Protocol):
    def get_market_snapshot(
        self,
        symbol: str,
        lookback_days: int = DEFAULT_LOOKBACK_DAYS,
    ) -> MarketSnapshot:
        """Return the application-facing market snapshot for a ticker."""


@dataclass(slots=True)
class _CacheEntry:
    snapshot: MarketSnapshot
    cached_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class NormalizedMarketDataService:
    def __init__(
        self,
        provider: MarketDataProvider,
        normalizer: MarketDataNormalizer | None = None,
        cache_ttl_seconds: int = 300,
    ):
        self._provider = provider
        self._normalizer = normalizer or MarketSnapshotNormalizer()
        self._cache_ttl = max(cache_ttl_seconds, 0)
        self._cache: dict[str, _CacheEntry] = {}

    def get_market_snapshot(
        self,
        symbol: str,
        lookback_days: int = DEFAULT_LOOKBACK_DAYS,
    ) -> MarketSnapshot:
        cleaned = symbol.strip().upper()
        if not cleaned:
            raise InvalidTickerError("Ticker symbol cannot be empty.")

        cache_key = f"{cleaned}:{lookback_days}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        try:
            raw_data = self._provider.fetch_security_data(cleaned, lookback_days=lookback_days)
            snapshot = self._normalizer.normalize(raw_data)
        except (InvalidTickerError, InsufficientDataError, ProviderUnavailableError):
            raise
        except Exception as exc:
            raise ProviderUnavailableError("Market data provider failed unexpectedly.") from exc

        self._store_cached(cache_key, snapshot)
        return snapshot

    def _get_cached(self, cache_key: str) -> MarketSnapshot | None:
        if self._cache_ttl == 0:
            return None

        entry = self._cache.get(cache_key)
        if entry is None:
            return None

        if datetime.now(UTC) - entry.cached_at > timedelta(seconds=self._cache_ttl):
            self._cache.pop(cache_key, None)
            return None

        return entry.snapshot

    def _store_cached(self, cache_key: str, snapshot: MarketSnapshot) -> None:
        if self._cache_ttl == 0:
            return
        self._cache[cache_key] = _CacheEntry(snapshot=snapshot)
