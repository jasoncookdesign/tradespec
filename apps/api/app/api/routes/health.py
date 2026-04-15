from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings
from app.core.dependencies import get_app_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(settings: Annotated[Settings, Depends(get_app_settings)]) -> dict[str, str]:
    return {
        "status": "ok",
        "application": settings.app_name,
        "environment": settings.environment,
    }
