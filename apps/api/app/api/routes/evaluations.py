from fastapi import APIRouter

from app.domain.evaluations.models import EvaluateTickerRequest, TickerEvaluation
from app.domain.evaluations.service import evaluate_ticker

router = APIRouter(tags=["evaluation"])


@router.post("/evaluate-ticker", response_model=TickerEvaluation)
def evaluate_ticker_route(payload: EvaluateTickerRequest) -> TickerEvaluation:
    return evaluate_ticker(payload)
