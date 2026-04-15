from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.core.dependencies import get_market_data_service
from app.domain.market_data.models import MarketSnapshot, NormalizedPriceBar
from app.main import app

client = TestClient(app)


class StubEvaluationMarketDataService:
    def get_market_snapshot(self, symbol: str, lookback_days: int = 60) -> MarketSnapshot:
        start = datetime(2026, 1, 1, tzinfo=UTC)
        closes = [100 + index for index in range(60)]
        return MarketSnapshot(
            ticker=symbol.upper(),
            asset_type="stock",
            currency="USD",
            exchange="NASDAQ",
            current_price=160.0,
            previous_close=159.0,
            historical_closes=closes,
            timestamps=[start + timedelta(days=index) for index in range(60)],
            volumes=[2_000_000 for _ in closes],
            recent_bars=[
                NormalizedPriceBar(
                    timestamp=start + timedelta(days=index),
                    open=149 + index,
                    high=151 + index,
                    low=148 + index,
                    close=150 + index,
                    volume=2_000_000,
                )
                for index in range(10)
            ],
            source="stub",
            fetched_at=datetime.now(UTC),
        )


def test_evaluate_ticker_route_uses_market_data_and_rules() -> None:
    app.dependency_overrides[get_market_data_service] = lambda: StubEvaluationMarketDataService()
    try:
        response = client.post('/api/evaluate-ticker', json={'ticker': 'MSFT'})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body['ticker'] == 'MSFT'
    assert body['status'] in {'VALID', 'WAIT', 'INVALID'}
    assert isinstance(body['reasons'], list)
