"""Compatibility bridge for the current web frontend.

This endpoint adapts the frontend's /api/agent/message contract to backend 2's
intake, safety, and triage services. It deliberately reports prototype triage as
such; it does not claim that unconfigured trained models were loaded.
"""
from typing import Literal, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.schemas import IntakeRequest, Language, TriageRequest
from app.services.intake import detect_language, process_intake
from app.services.llm import generate_reply
from app.services.safety import evaluate_safety
from app.services.triage import triage_request

router = APIRouter(prefix="/api", tags=["agent-bridge"])


class HistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class AgentMessageRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=128)
    message: str = Field(..., min_length=1, max_length=2000)
    language: Literal["en", "hi", "hinglish"] = "en"
    history: list[HistoryMessage] = Field(default_factory=list)


def _urgency(value: Optional[str]) -> str:
    return {
        "critical": "emergency",
        "high": "urgent",
        "moderate": "same_day",
        "low": "routine",
    }.get(str(value), "unknown")


@router.post("/agent/message")
async def agent_message(request: AgentMessageRequest):
    # The frontend includes the current turn in history. Avoid appending it twice.
    user_turns = [m.content.strip() for m in request.history if m.role == "user" and m.content.strip()]
    if not user_turns or user_turns[-1] != request.message.strip():
        user_turns.append(request.message.strip())
    combined_text = "\n".join(user_turns)[-8000:]

    safety = evaluate_safety(combined_text)
    if safety.red_flag:
        first_flag = safety.matched_rules[0] if safety.matched_rules else None
        instruction = "A possible emergency warning was detected. Call local emergency services (112/108 in India) now if someone may be in immediate danger. Follow the dispatcher’s instructions; do not wait for this app."
        return {
            "status": "possible_emergency",
            "response": f"Safety warning: {instruction}",
            "follow_up_question": None,
            "safety": {
                "flagged": True,
                "level": "possible_emergency",
                "rule_id": first_flag.rule_id if first_flag else "SAFETY_SHIELD",
                "message": instruction,
            },
            "triage": None,
            "caregiver_matches": [],
            "explanation": ["Backend 2 SafetyShield rule matched; ordinary care matching was bypassed."],
            "session_id": request.session_id,
        }

    # The UI defaults to English; infer Hindi/Hinglish when the user writes it,
    # unless they explicitly selected a non-English language in the UI.
    try:
        selected_language = Language(request.language)
    except ValueError:
        selected_language = Language.EN
    detected_language = detect_language(combined_text)
    language = (
        detected_language
        if selected_language == Language.EN and detected_language in (Language.HI, Language.HINGLISH)
        else selected_language
    )

    intake = process_intake(
        IntakeRequest(
            text=combined_text[:2000],
            session_id=request.session_id,
            language_hint=language,
        )
    )

    if intake.follow_up_questions:
        question = intake.follow_up_questions[0]
        return {
            "status": "needs_followup",
            "response": "I need one more detail to understand the concern before showing a care-navigation summary. This prototype is not a diagnosis.",
            "follow_up_question": {
                "id": question.id,
                "text": question.question,
            },
            "safety": {"flagged": False, "level": "none"},
            "triage": None,
            "caregiver_matches": [],
            "explanation": ["Follow-up selected by backend 2 intake service."],
            "session_id": request.session_id,
        }

    result = triage_request(
        TriageRequest(
            session_id=request.session_id,
            confirmed_summary=intake.editable_summary,
            language=intake.language,
        )
    )
    care_type = result.care_type.value if result.care_type else "primary_care"
    urgency = _urgency(result.urgency.value if result.urgency else None)
    reason = result.reason or "The prototype could not produce a detailed explanation."
    return {
        "status": "routed",
        "response": f"{reason}\n\nPrototype decision support only — not a medical diagnosis. If symptoms are severe or worsening, seek professional care.",
        "follow_up_question": None,
        "safety": {"flagged": False, "level": "none"},
        "triage": {
            "care_type": care_type,
            "urgency": urgency,
            "explanation": reason,
            "next_steps": ["Review this information with a qualified healthcare professional."],
            "model_name": "backend-2-rule-based-prototype",
            "model_version": "0.1.0",
            "confidence": result.confidence,
        },
        "caregiver_matches": [],
        "explanation": [
            "Intake and follow-up questions came from backend 2.",
            "Triage currently uses the repository's explicitly marked prototype baseline; trained-model status is not implied.",
        ],
        "session_id": request.session_id,
    }
