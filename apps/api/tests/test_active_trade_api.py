from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_active_trades_route_returns_guidance_metrics() -> None:
    response = client.get('/api/active-trades')

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert 'guidance_status' in body[0]
    assert 'expected_time_to_move_max_days' in body[0]
    assert 'elapsed_days' in body[0]
