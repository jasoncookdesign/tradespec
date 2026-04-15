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


def test_evaluate_ticker_contract_shape() -> None:
    app.dependency_overrides[get_market_data_service] = lambda: StubEvaluationMarketDataService()
    try:
        response = client.post(
            "/api/evaluate-ticker",
            json={"ticker": "MSFT", "asset_type": "stock"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["ticker"] == "MSFT"
    assert body["status"] in {"VALID", "WAIT", "INVALID"}
    assert "suggested_entry_zone" in body
    assert "reasons" in body


def test_validate_trade_contract_shape() -> None:
    response = client.post(
        "/api/validate-trade",
        json={
            "ticker": "MSFT",
            "setup_type": "breakout",
            "entry_zone_min": 100,
            "entry_zone_max": 102,
            "stop_loss": 96,
            "target_price": 112,
            "time_horizon_days": 10,
            "thesis": "Continuation after a clean breakout.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["approved"], bool)
    assert 0 <= body["score"] <= 100
    assert isinstance(body["checks"], list)


def test_active_trades_and_journal_entry_contract_shapes() -> None:
    active_response = client.get("/api/active-trades")
    journal_response = client.post(
        "/api/journal-entry",
        json={
            "trade_spec_id": "trade-msft-001",
            "exit_price": 111.5,
            "outcome_summary": "Closed into strength.",
            "lesson_summary": "Partial profits improved discipline.",
        },
    )

    assert active_response.status_code == 200
    assert isinstance(active_response.json(), list)
    assert journal_response.status_code == 200
    assert "ai_observation" in journal_response.json()
