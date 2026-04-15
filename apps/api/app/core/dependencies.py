from app.core.config import Settings, get_settings
from app.domain.ai_services.service import AIService, StubAIService
from app.domain.market_data.service import MarketDataService, YahooFinanceMarketDataService


def get_app_settings() -> Settings:
    return get_settings()


def get_market_data_service() -> MarketDataService:
    """Dependency seam for future provider swapping and testing."""

    settings = get_settings()

    if settings.market_data_provider == "yahoo-finance":
        return YahooFinanceMarketDataService()

    raise ValueError(f"Unsupported market data provider: {settings.market_data_provider}")


def get_ai_service() -> AIService:
    """Dependency seam for pluggable advisory services."""

    settings = get_settings()

    if settings.ai_provider == "stub":
        return StubAIService()

    raise ValueError(f"Unsupported AI provider: {settings.ai_provider}")
