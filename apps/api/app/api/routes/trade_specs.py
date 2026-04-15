from fastapi import APIRouter, Response, status

from app.domain.trade_specs.models import TradeSpec, TradeSpecInput
from app.domain.trade_specs.service import create_trade_spec

router = APIRouter(tags=["trade-specs"])


@router.post("/trade-specs", response_model=TradeSpec, status_code=status.HTTP_201_CREATED)
def create_trade_spec_route(payload: TradeSpecInput, response: Response) -> TradeSpec:
    return create_trade_spec(payload)
