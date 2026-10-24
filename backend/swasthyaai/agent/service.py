from backend.swasthyaai.agent.contracts import (
    AgentInput,
    AgentResponse,
    CareType,
    Language,
    Location,
)
from backend.swasthyaai.agent.dispatcher import aggregate_triage, run_relevant_models
from backend.swasthyaai.agent.local_model import LocalTextNavigationAdapter
from backend.swasthyaai.agent.models import ModelRegistry
from backend.swasthyaai.agent.safety import detect_language, detect_red_flags
from backend.swasthyaai.agent.state import ConversationState
from backend.swasthyaai.providers.gemini import GeminiWordingAdapter

# Keep model loading lazy. If the local artifact isn't present, the adapter
# reports unavailable and the agent safely falls back instead of inventing a result.
MODEL_REGISTRY = ModelRegistry([LocalTextNavigationAdapter()])
_GEMINI = GeminiWordingAdapter()
_SUPPORTED_LANGUAGES = {item.value for item in Language if item != Language.AUTO}


def _unavailable(session_id: str, flags: list[str] | None = None) -> AgentResponse:
    return AgentResponse(
        session_id=session_id,
        status="unavailable",
        response="I can’t determine a safe care option from the information available. Please contact a qualified healthcare professional for guidance.",
        safety_flags=flags or [],
        aggregation_status="fallback",
        needs_human_review=True,
    )


async def run_healthcare_agent(
    session_id: str,
    user_message: str,
    context: dict | None = None,
) -> AgentResponse:
    context = context or {}
    requested_language = str(context.get("language", "auto"))
    language = detect_language(user_message, requested_language)
    flags = detect_red_flags(user_message)
    if flags:
        return AgentResponse(
            session_id=session_id,
            status="emergency",
            response="This may be an emergency. Call 112 now in India, or your local emergency number. Do not wait for an online response.",
            care_type=CareType.EMERGENCY_112,
            urgency="emergency",
            safety_flags=flags,
            aggregation_status="fallback",
            needs_human_review=True,
        )

    if language not in _SUPPORTED_LANGUAGES:
        return _unavailable(session_id)

    try:
        state = ConversationState(
            follow_up_count=max(0, int(context.get("follow_up_count", 0))),
            max_follow_ups=2,
        )
    except (TypeError, ValueError):
        state = ConversationState(follow_up_count=2)

    underspecified = len(user_message.split()) < 5 or user_message.strip().casefold() in {
        "doctor chahiye", "need a doctor", "help me", "mujhe help chahiye"
    }
    if underspecified:
        if not state.can_ask_follow_up:
            return _unavailable(session_id)
        return AgentResponse(
            session_id=session_id,
            status="needs_follow_up",
            response="I need a little more information before I can suggest a care option.",
            follow_up_question="What symptoms or care do you need help with, and when did it start?",
            needs_human_review=True,
        )

    location_value = context.get("location")
    location = Location.model_validate(location_value) if location_value else None
    request = AgentInput(
        session_id=session_id,
        user_message=user_message,
        language=language,
        location=location,
        external_ai_consent=bool(context.get("external_ai_consent", False)),
        task=str(context.get("task", "care_triage")),
    )
    models = await run_relevant_models(MODEL_REGISTRY, request)
    aggregate = aggregate_triage(models)
    if aggregate.care_type is None or aggregate.urgency is None:
        response = _unavailable(session_id, aggregate.safety_flags)
        response.models = models
        response.aggregation_status = aggregate.status
        return response

    response = AgentResponse(
        session_id=session_id,
        status="decision",
        response="The experimental text model is not a diagnostic or validated triage tool. Please arrange a healthcare professional's review; seek urgent help for severe or worsening symptoms.",
        care_type=aggregate.care_type,
        urgency=aggregate.urgency,
        safety_flags=aggregate.safety_flags,
        models=models,
        aggregation_status=aggregate.status,
        needs_human_review=True,
    )
    # Optional provider may only rephrase the already-reviewed text when the user
    # consents; emergency responses return before this point.
    wording = await _GEMINI.rephrase(response, request.external_ai_consent)
    if wording:
        response.response = wording
    return response
