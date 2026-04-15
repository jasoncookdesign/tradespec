from fastapi import APIRouter

from app.domain.active_trades.models import ActiveTrade
from app.domain.active_trades.service import ActiveTradeStabilizerService

router = APIRouter(tags=["active-trades"])
service = ActiveTradeStabilizerService()


@router.get("/active-trades", response_model=list[ActiveTrade])
def list_active_trades_route() -> list[ActiveTrade]:
    return service.list_active_trades()
