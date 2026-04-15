class MarketDataError(Exception):
    """Base error for market data failures."""


class InvalidTickerError(MarketDataError):
    """Raised when a symbol cannot be resolved by the provider."""


class ProviderUnavailableError(MarketDataError):
    """Raised when the provider cannot be reached or returns an upstream error."""


class InsufficientDataError(MarketDataError):
    """Raised when the returned history is too sparse for downstream rules."""
