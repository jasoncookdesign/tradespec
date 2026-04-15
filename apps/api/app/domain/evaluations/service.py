from app.domain.evaluations.models import EvaluateTickerRequest, TickerEvaluation
from app.domain.market_data.service import MarketDataService
from app.domain.rules.engine import evaluate_market_snapshot


def evaluate_ticker(
    payload: EvaluateTickerRequest,
    market_data_service: MarketDataService,
) -> TickerEvaluation:
    """Evaluate a ticker using the real market data layer and deterministic rule engine."""

    snapshot = market_data_service.get_market_snapshot(payload.ticker)
    return evaluate_market_snapshot(snapshot)
