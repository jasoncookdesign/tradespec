from fastapi import APIRouter

from app.domain.position_sizing.models import PositionSizingRequest, PositionSizingResult
from app.domain.position_sizing.service import calculate_position_size

router = APIRouter(tags=['position-sizing'])


@router.post('/position-size', response_model=PositionSizingResult)
def position_size_route(payload: PositionSizingRequest) -> PositionSizingResult:
    return calculate_position_size(payload)
