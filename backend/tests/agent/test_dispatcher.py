import asyncio

from backend.swasthyaai.agent.contracts import AgentInput, ModelResult
from backend.swasthyaai.agent.dispatcher import aggregate_triage, run_relevant_models
from backend.swasthyaai.agent.models import ModelRegistry


class Adapter:
    task = "care_triage"
    languages = {"English"}
    timeout_seconds = 0.05

    def __init__(self, name, result=None, delay=0, error=None):
        self.name = name
        self.result = result or ModelResult(
            name=name,
            version="1",
            task=self.task,
            care_type="teleconsultation",
            urgency="scheduled",
            confidence=0.9,
        )
        self.delay = delay
        self.error = error
        self.started = False

    async def predict(self, text, context):
        self.started = True
        await asyncio.sleep(self.delay)
        if self.error:
            raise self.error
        return self.result


def test_dispatches_relevant_models_concurrently_and_skips_other_tasks():
    async def run():
        first = Adapter("first", delay=0.02)
        second = Adapter("second", delay=0.02)
        unrelated = Adapter("image", delay=0.02)
        unrelated.task = "image_analysis"
        registry = ModelRegistry([first, second, unrelated])

        results = await run_relevant_models(
            registry, AgentInput(session_id="s1", user_message="need a doctor")
        )

        return first, second, unrelated, results

    first, second, unrelated, results = asyncio.run(run())

    assert first.started and second.started
    assert not unrelated.started
    assert {result.name for result in results} == {"first", "second"}


def test_isolates_model_failure_and_timeout():
    async def run():
        good = Adapter("good")
        failing = Adapter("failing", error=RuntimeError("provider down"))
        slow = Adapter("slow", delay=0.2)
        return await run_relevant_models(
            ModelRegistry([good, failing, slow]),
            AgentInput(session_id="s1", user_message="need a doctor"),
        )

    results = asyncio.run(run())

    assert {result.name: result.status for result in results} == {
        "good": "used",
        "failing": "failed",
        "slow": "failed",
    }


def test_rejects_adapter_result_for_wrong_task():
    async def run():
        wrong_task = ModelResult(
            name="bad",
            version="1",
            task="image_analysis",
            care_type="teleconsultation",
            urgency="scheduled",
            confidence=0.9,
        )
        return await run_relevant_models(
            ModelRegistry([Adapter("bad", result=wrong_task)]),
            AgentInput(session_id="s1", user_message="need a doctor"),
        )

    results = asyncio.run(run())

    assert results[0].status == "failed"


def test_disagreement_requires_human_review_instead_of_averaging():
    results = [
        ModelResult(name="a", version="1", task="care_triage", care_type="home_nursing", urgency="same_day", confidence=0.9),
        ModelResult(name="b", version="1", task="care_triage", care_type="teleconsultation", urgency="scheduled", confidence=0.9),
    ]

    aggregate = aggregate_triage(results)

    assert aggregate.status == "disagreement"
    assert aggregate.care_type is None
    assert aggregate.needs_human_review is True
