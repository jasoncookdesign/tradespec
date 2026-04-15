from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_market_data_service
from app.domain.evaluations.models import EvaluateTickerRequest, TickerEvaluation
from app.domain.evaluations.service import evaluate_ticker
from app.domain.market_data.errors import (
    InsufficientDataError,
    InvalidTickerError,
    ProviderUnavailableError,
)
from app.domain.market_data.service import MarketDataService

router = APIRouter(tags=["evaluation"])


@router.post("/evaluate-ticker", response_model=TickerEvaluation)
def evaluate_ticker_route(
    payload: EvaluateTickerRequest,
    market_data_service: Annotated[MarketDataService, Depends(get_market_data_service)],
) -> TickerEvaluation:
    try:
        return evaluate_ticker(payload, market_data_service)
    except InvalidTickerError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InsufficientDataError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ProviderUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
