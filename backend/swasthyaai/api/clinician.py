from fastapi import APIRouter, Depends

from backend.swasthyaai.models.auth import User
from backend.swasthyaai.services.auth import require_role

router = APIRouter(prefix="/clinician")


@router.get("/records")
def authorized_records_placeholder(
    _user: User = Depends(require_role("clinician")),
) -> list[dict]:
    return []
