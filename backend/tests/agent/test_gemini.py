import asyncio
import json
from urllib.error import URLError

from backend.swasthyaai.agent.contracts import AgentResponse
from backend.swasthyaai.providers.gemini import GeminiWordingAdapter


def response():
    return AgentResponse(
        session_id="s1",
        status="decision",
        response="A clinician can help you choose an appropriate next step.",
        care_type="teleconsultation",
        urgency="scheduled",
        needs_human_review=True,
    )


def test_gemini_is_disabled_without_per_turn_consent_or_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    adapter = GeminiWordingAdapter()

    assert asyncio.run(adapter.rephrase(response(), consent=False)) is None
    assert asyncio.run(adapter.rephrase(response(), consent=True)) is None


def test_gemini_only_returns_wording_and_does_not_change_structured_fields(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "local-test-key")
    adapter = GeminiWordingAdapter()
    original = response()

    def fake_request(payload):
        return "Please contact a clinician for care guidance."

    monkeypatch.setattr(adapter, "_generate", fake_request)
    wording = asyncio.run(adapter.rephrase(original, consent=True))

    assert wording == "Please contact a clinician for care guidance."
    assert original.care_type == "teleconsultation"
    assert original.urgency == "scheduled"
    assert original.needs_human_review is True


def test_gemini_failure_returns_no_wording_for_template_fallback(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "local-test-key")
    adapter = GeminiWordingAdapter()
    monkeypatch.setattr(adapter, "_generate", lambda payload: (_ for _ in ()).throw(URLError("offline")))

    assert asyncio.run(adapter.rephrase(response(), consent=True)) is None
