"""Compatibility bridge for the current web frontend.

This endpoint adapts the frontend's /api/agent/message contract to backend 2's
intake, safety, and triage services. It deliberately reports prototype triage as
such; it does not claim that unconfigured trained models were loaded.
"""
from typing import Literal, Optional
import re

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
    latest_user_text = request.message.strip()
    if not user_turns or user_turns[-1] != latest_user_text:
        user_turns.append(latest_user_text)

    # A bare number is a valid answer when the previous assistant turn asked for age.
    last_assistant_prompt = next(
        (m.content.lower() for m in reversed(request.history) if m.role == "assistant"),
        "",
    )
    if (
        re.fullmatch(r"\d{1,3}", latest_user_text)
        and any(token in last_assistant_prompt for token in ("age", "how old", "age group", "exact age"))
    ):
        age = int(latest_user_text)
        if 0 <= age <= 120:
            user_turns[-1] = f"I am {age} years old"
    elif (
        latest_user_text.lower().strip(" .,!") in {"adult", "child", "infant", "elderly", "teenager"}
        and any(token in last_assistant_prompt for token in ("age", "how old", "age group", "exact age"))
    ):
        user_turns[-1] = latest_user_text

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

    # General-purpose questions should not be forced through medical intake.
    # Only messages that look symptom/health related continue into triage.
    health_terms = (
        "pain", "ache", "fever", "cough", "breath", "symptom", "sick", "injury",
        "hurt", "headache", "dizzy", "nausea", "vomit", "bleeding", "rash",
        "medicine", "medication", "health", "doctor", "medical", "pregnan",
        "chest", "stomach", "blood pressure", "diabetes", "sleep", "anxiety",
        "depress", "suicid", "दर्द", "बुखार", "खांसी", "सांस", "बीमार", "चक्कर",
        "दवा", "स्वास्थ्य", "सिरदर्द", "उल्टी", "सीने", "पेट दर्द",
    )
    latest_lower = latest_user_text.lower()
    is_health_question = any(term in latest_lower for term in health_terms)

    conversation = [{"role": m.role, "content": m.content} for m in request.history]
    if not conversation or conversation[-1]["role"] != "user" or conversation[-1]["content"].strip() != latest_user_text:
        conversation.append({"role": "user", "content": latest_user_text})

    if not is_health_question:
        chat_reply = await generate_reply(conversation, language.value)
        if chat_reply:
            return {
                "status": "routed",
                "response": chat_reply,
                "follow_up_question": None,
                "safety": {"flagged": False, "level": "unknown"},
                "triage": None,
                "caregiver_matches": [],
                "explanation": ["General-purpose response from the configured language model; no medical triage was performed."],
                "session_id": request.session_id,
            }
        return {
            "status": "unavailable",
            "response": "I can answer general questions once a local language model is running. This setup is configured for free Ollama at http://localhost:11434. Install Ollama, download the qwen2.5:3b model, then restart this backend. No paid API credits are required.",
            "follow_up_question": None,
            "safety": {"flagged": False, "level": "unknown"},
            "triage": None,
            "caregiver_matches": [],
            "explanation": ["No language model responded; no answer was fabricated."],
            "session_id": request.session_id,
        }

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
    conversation = [{"role": m.role, "content": m.content} for m in request.history]
    if not conversation or conversation[-1]["role"] != "user" or conversation[-1]["content"].strip() != request.message.strip():
        conversation.append({"role": "user", "content": request.message.strip()})
    llm_reply = await generate_reply(conversation, language.value)
    response_text = llm_reply or f"{reason}\n\nPrototype decision support only — not a medical diagnosis. If symptoms are severe or worsening, seek professional care."
    response_text += "\n\nSwasthyaAI is informational support, not a diagnosis. The care-routing category below is produced by a rule-based prototype."
    return {
        "status": "routed",
        "response": response_text,
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
