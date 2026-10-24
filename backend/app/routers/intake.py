# SwasthyaAI Intake Router

from fastapi import APIRouter
from app.schemas import IntakeRequest, IntakeResponse
from app.services.intake import process_intake, process_follow_up

router = APIRouter(prefix="/api", tags=["intake"])


@router.post("/intake", response_model=IntakeResponse)
async def intake(request: IntakeRequest) -> IntakeResponse:
    """
    Process initial intake: detect language, extract fields, select follow-ups,
    return editable summary for user confirmation.
    """
    return process_intake(request)


@router.post("/intake/followup", response_model=IntakeResponse)
async def intake_followup(
    session_id: str,
    answers: dict[str, str],
    previous_who: str = "",
    previous_symptoms: str = "",
    previous_duration: str = "",
    previous_age_group: str = "",
    previous_language: str = "en",
) -> IntakeResponse:
    """
    Process follow-up answers and return updated intake response.
    """
    from app.services.intake import ExtractedFields
    from app.schemas import Language

    previous = ExtractedFields(
        who=previous_who or None,
        symptoms=previous_symptoms.split(",") if previous_symptoms else [],
        duration=previous_duration or None,
        age_group=previous_age_group or None,
        language=Language(previous_language),
    )
    return process_follow_up(session_id, answers, previous)