from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_validate_trade_flow_returns_score_and_state() -> None:
    response = client.post(
        '/api/validate-trade',
        json={
            'ticker': 'MSFT',
            'setup_type': 'pullback',
            'entry_zone_min': 100,
            'entry_zone_max': 102,
            'stop_loss': 95,
            'target_price': 114,
            'time_horizon_days': 10,
            'thesis': 'Trend pullback into support with defined risk.',
            'ticker_status': 'VALID',
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body['approved'] is True
    assert body['score'] >= 80


def test_create_trade_spec_flow_persists_trade() -> None:
    response = client.post(
        '/api/trade-specs',
        json={
            'ticker': 'MSFT',
            'setup_type': 'pullback',
            'entry_zone_min': 100,
            'entry_zone_max': 102,
            'stop_loss': 95,
            'target_price': 114,
            'time_horizon_days': 10,
            'thesis': 'Trend pullback into support with defined risk.',
            'ticker_status': 'VALID',
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body['ticker'] == 'MSFT'
    assert 'id' in body
