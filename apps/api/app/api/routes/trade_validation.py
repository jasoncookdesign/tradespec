from fastapi import APIRouter

from app.domain.trade_specs.models import TradeSpecInput, TradeValidationResult
from app.domain.trade_specs.service import validate_trade

router = APIRouter(tags=["trade-validation"])


@router.post("/validate-trade", response_model=TradeValidationResult)
def validate_trade_route(payload: TradeSpecInput) -> TradeValidationResult:
    return validate_trade(payload)
