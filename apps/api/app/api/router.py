from fastapi import APIRouter

from app.api.routes.active_trades import router as active_trades_router
from app.api.routes.evaluations import router as evaluations_router
from app.api.routes.health import router as health_router
from app.api.routes.journal import router as journal_router
from app.api.routes.market_snapshot import router as market_snapshot_router
from app.api.routes.trade_specs import router as trade_specs_router
from app.api.routes.trade_validation import router as trade_validation_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(evaluations_router)
api_router.include_router(trade_validation_router)
api_router.include_router(trade_specs_router)
api_router.include_router(active_trades_router)
api_router.include_router(journal_router)
api_router.include_router(market_snapshot_router)
