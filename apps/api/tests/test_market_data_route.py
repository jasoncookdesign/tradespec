from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.core.dependencies import get_market_data_service
from app.domain.market_data.models import MarketSnapshot, NormalizedPriceBar
from app.main import app

client = TestClient(app)


class StubSnapshotService:
    def get_market_snapshot(self, symbol: str, lookback_days: int = 60) -> MarketSnapshot:
        return MarketSnapshot(
            ticker=symbol.upper(),
            asset_type="stock",
            currency="USD",
            exchange="NASDAQ",
            current_price=123.45,
            previous_close=122.0,
            historical_closes=[121.5, 122.0, 123.45],
            timestamps=[
                datetime(2025, 12, 30, tzinfo=UTC),
                datetime(2025, 12, 31, tzinfo=UTC),
                datetime(2026, 1, 1, tzinfo=UTC),
            ],
            volumes=[900000, 950000, 1000000],
            recent_bars=[
                NormalizedPriceBar(
                    timestamp=datetime(2026, 1, 1, tzinfo=UTC),
                    open=121.0,
                    high=124.0,
                    low=120.0,
                    close=123.45,
                    volume=1000000,
                )
            ],
            source="stub",
            fetched_at=datetime(2026, 1, 1, tzinfo=UTC),
        )


def test_market_snapshot_route_returns_normalized_shape() -> None:
    app.dependency_overrides[get_market_data_service] = lambda: StubSnapshotService()
    try:
        response = client.get('/api/market-snapshot/MSFT')
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body['ticker'] == 'MSFT'
    assert body['asset_type'] == 'stock'
    assert 'current_price' in body
    assert isinstance(body['historical_closes'], list)
