from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_evaluate_ticker_contract_shape() -> None:
    response = client.post(
        "/api/evaluate-ticker",
        json={"ticker": "MSFT", "asset_type": "stock"},
    )

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
