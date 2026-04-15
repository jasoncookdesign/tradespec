from datetime import UTC, datetime
from typing import Protocol

from app.domain.market_data.config import MIN_HISTORY_BARS, RECENT_BARS_COUNT
from app.domain.market_data.errors import InsufficientDataError
from app.domain.market_data.models import MarketSnapshot, NormalizedPriceBar, ProviderSecurityData


class MarketDataNormalizer(Protocol):
    def normalize(self, raw_data: ProviderSecurityData) -> MarketSnapshot:
        """Convert provider-facing market data into the app-facing snapshot contract."""


class MarketSnapshotNormalizer:
    def normalize(self, raw_data: ProviderSecurityData) -> MarketSnapshot:
        if len(raw_data.history) < MIN_HISTORY_BARS:
            raise InsufficientDataError(
                "At least "
                f"{MIN_HISTORY_BARS} daily bars are required to build a market "
                f"snapshot for {raw_data.symbol}."
            )

        recent_bars = [
            NormalizedPriceBar(**bar.model_dump()) for bar in raw_data.history[-RECENT_BARS_COUNT:]
        ]

        return MarketSnapshot(
            ticker=raw_data.symbol,
            asset_type=raw_data.asset_type,
            currency=raw_data.currency,
            exchange=raw_data.exchange,
            current_price=raw_data.latest_price,
            previous_close=raw_data.previous_close,
            historical_closes=[bar.close for bar in raw_data.history],
            timestamps=[bar.timestamp for bar in raw_data.history],
            volumes=[bar.volume for bar in raw_data.history],
            recent_bars=recent_bars,
            source=raw_data.source,
            fetched_at=datetime.now(UTC),
        )
