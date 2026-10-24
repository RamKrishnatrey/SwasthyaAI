# SwasthyaAI Matching Router

from fastapi import APIRouter
from app.schemas import MatchRequest, MatchResponse
from app.services.matching import match_caregivers

router = APIRouter(prefix="/api", tags=["matching"])


@router.post("/match", response_model=MatchResponse)
async def match(request: MatchRequest) -> MatchResponse:
    """
    Match caregivers based on care type, urgency, location, and language.
    Returns ranked matches with score breakdown and explanations.
    """
    return match_caregivers(request)