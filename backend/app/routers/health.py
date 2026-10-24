# SwasthyaAI Health Check Router

from fastapi import APIRouter
from app.schemas import HealthResponse

router = APIRouter(prefix="", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse()