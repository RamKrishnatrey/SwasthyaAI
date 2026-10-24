from fastapi import APIRouter, Depends

from backend.swasthyaai.agent.contracts import CareType, Language
from backend.swasthyaai.models.auth import User
from backend.swasthyaai.services.auth import require_role
from backend.swasthyaai.services.discovery import find_caregivers

router = APIRouter(prefix="/caregivers")


@router.get("")
def caregivers(
    care_type: CareType,
    language: Language | None = None,
    _user: User = Depends(require_role("patient", "clinician")),
) -> list[dict]:
    return find_caregivers(care_type, language)
