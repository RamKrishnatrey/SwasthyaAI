import asyncio

from backend.swasthyaai.agent import service
from backend.swasthyaai.agent.contracts import AgentInput, ModelResult
from backend.swasthyaai.agent.models import ModelRegistry


class CountingAdapter:
    name = "counting"
    version = "1"
    task = "care_triage"
    languages = {"English", "Hindi", "Hinglish"}
    timeout_seconds = 0.1

    def __init__(self, result=None):
        self.calls = 0
        self.result = result

    async def predict(self, text, context):
        self.calls += 1
        return self.result or ModelResult(
            name=self.name,
            version=self.version,
            task=self.task,
            care_type="teleconsultation",
            urgency="scheduled",
            confidence=0.9,
        )


def test_emergency_override_returns_112_without_calling_models(monkeypatch):
    adapter = CountingAdapter()
    monkeypatch.setattr(service, "MODEL_REGISTRY", ModelRegistry([adapter]))

    response = asyncio.run(
        service.run_healthcare_agent("session", "papa ko chest pain ho raha hai")
    )

    assert response.status == "emergency"
    assert response.care_type == "emergency_112"
    assert response.urgency == "emergency"
    assert response.matched_caregivers == []
    assert "112" in response.response
    assert adapter.calls == 0


def test_underspecified_non_emergency_requests_one_follow_up():
    response = asyncio.run(
        service.run_healthcare_agent("session", "doctor chahiye")
    )

    assert response.status == "needs_follow_up"
    assert response.follow_up_question
    assert response.care_type is None


def test_follow_up_limit_returns_human_review_fallback():
    response = asyncio.run(
        service.run_healthcare_agent(
            "session", "still not sure", {"follow_up_count": 2}
        )
    )

    assert response.status == "unavailable"
    assert response.follow_up_question is None
    assert response.needs_human_review is True


def test_language_without_registered_model_uses_explicit_fallback():
    response = asyncio.run(
        service.run_healthcare_agent("session", "me duele mucho", {"language": "Spanish"})
    )

    assert response.status == "unavailable"
    assert response.needs_human_review is True
    assert response.models == []


def test_service_does_not_report_a_diagnosis():
    response = asyncio.run(
        service.run_healthcare_agent("session", "I have a mild headache")
    )

    assert "diagnos" not in response.response.lower()
    assert response.disclaimer
