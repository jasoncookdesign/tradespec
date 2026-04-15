from functools import lru_cache

from app.core.config import Settings, get_settings
from app.domain.ai_services.service import AIService, StubAIService
from app.domain.market_data.service import MarketDataService, NormalizedMarketDataService
from app.domain.market_data.yahoo_adapter import YahooFinanceMarketDataProvider


def get_app_settings() -> Settings:
    return get_settings()


@lru_cache
def _build_market_data_service(provider_name: str, cache_ttl_seconds: int) -> MarketDataService:
    if provider_name == "yahoo-finance":
        return NormalizedMarketDataService(
            YahooFinanceMarketDataProvider(),
            cache_ttl_seconds=cache_ttl_seconds,
        )

    raise ValueError(f"Unsupported market data provider: {provider_name}")


def get_market_data_service() -> MarketDataService:
    """Dependency seam for future provider swapping and testing."""

    settings = get_settings()
    return _build_market_data_service(
        settings.market_data_provider,
        settings.market_data_cache_ttl_seconds,
    )


def get_ai_service() -> AIService:
    """Dependency seam for pluggable advisory services."""

    settings = get_settings()

    if settings.ai_provider == "stub":
        return StubAIService()

    raise ValueError(f"Unsupported AI provider: {settings.ai_provider}")
