from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.dependencies import get_market_data_service
from app.domain.market_data.config import DEFAULT_LOOKBACK_DAYS
from app.domain.market_data.errors import (
    InsufficientDataError,
    InvalidTickerError,
    ProviderUnavailableError,
)
from app.domain.market_data.models import MarketSnapshot
from app.domain.market_data.service import MarketDataService

router = APIRouter(tags=["market-data"])


@router.get("/market-snapshot/{ticker}", response_model=MarketSnapshot)
def get_market_snapshot_route(
    ticker: str,
    market_data_service: Annotated[MarketDataService, Depends(get_market_data_service)],
    lookback_days: int = Query(default=DEFAULT_LOOKBACK_DAYS, ge=20, le=365),
) -> MarketSnapshot:
    try:
        return market_data_service.get_market_snapshot(ticker, lookback_days=lookback_days)
    except InvalidTickerError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InsufficientDataError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ProviderUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
