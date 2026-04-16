from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_position_sizing_route_returns_expected_shape() -> None:
    response = client.post(
        '/api/position-size',
        json={
            'trade': {
                'ticker': 'MSFT',
                'setup_type': 'pullback',
                'entry_zone_min': 100,
                'entry_zone_max': 102,
                'stop_loss': 95,
                'target_price': 119,
                'time_horizon_days': 10,
                'thesis': 'Trend pullback into support with defined risk.',
                'ticker_status': 'VALID',
            },
            'account_size_dollars': 10000,
            'risk_percent_per_trade': 1.0,
            'intended_entry_price': 101,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert 'approved_for_sizing' in body
    assert 'risk_dollars' in body
    assert 'suggested_shares' in body
    assert 'warnings' in body
