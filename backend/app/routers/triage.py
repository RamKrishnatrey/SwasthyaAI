# SwasthyaAI Triage Router

from fastapi import APIRouter
from app.schemas import TriageRequest, TriageResponse
from app.services.triage import triage_request

router = APIRouter(prefix="/api", tags=["triage"])


@router.post("/triage", response_model=TriageResponse)
async def triage(request: TriageRequest) -> TriageResponse:
    """
    Process triage: run ML model on intake results, return care type, urgency, confidence.
    Includes model_source field to track which model version made the prediction.
    """
    return triage_request(request)