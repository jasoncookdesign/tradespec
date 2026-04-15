from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class QuoteSnapshot:
    symbol: str
    last_price: float
    source: str


class MarketDataService(Protocol):
    def get_quote(self, symbol: str) -> QuoteSnapshot:
        """Return the latest tradable market snapshot for a symbol."""


class YahooFinanceMarketDataService:
    """Initial adapter seam for a future Yahoo Finance implementation."""

    def get_quote(self, symbol: str) -> QuoteSnapshot:
        cleaned = symbol.upper().strip()
        return QuoteSnapshot(symbol=cleaned, last_price=0.0, source="yahoo-finance-stub")
