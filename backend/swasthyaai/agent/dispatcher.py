import asyncio

from backend.swasthyaai.agent.contracts import AggregatedTriage, AgentInput, ModelResult
from backend.swasthyaai.agent.models import ModelAdapter, ModelRegistry


def _failure(adapter: ModelAdapter, task: str, status: str = "failed") -> ModelResult:
    return ModelResult(
        name=adapter.name,
        version=getattr(adapter, "version", "unknown"),
        task=task,
        status=status,
    )


async def _run_adapter(adapter: ModelAdapter, request: AgentInput) -> ModelResult:
    try:
        result = await asyncio.wait_for(
            adapter.predict(request.user_message, {"session_id": request.session_id}),
            timeout=adapter.timeout_seconds,
        )
        if result.task != request.task:
            return _failure(adapter, request.task)
        return result
    except Exception:
        return _failure(adapter, request.task)


async def run_relevant_models(registry: ModelRegistry, request: AgentInput) -> list[ModelResult]:
    adapters = registry.relevant(request)
    return list(await asyncio.gather(*(_run_adapter(adapter, request) for adapter in adapters)))


def aggregate_triage(results: list[ModelResult]) -> AggregatedTriage:
    usable = [result for result in results if result.status == "used"]
    if not usable:
        return AggregatedTriage(status="fallback")
    if len(usable) == 1:
        result = usable[0]
        return AggregatedTriage(
            status="single_model",
            care_type=result.care_type,
            urgency=result.urgency,
            confidence=result.confidence,
            safety_flags=result.safety_flags,
            needs_human_review=True,
        )

    decisions = {(result.care_type, result.urgency) for result in usable}
    if len(decisions) != 1:
        return AggregatedTriage(
            status="disagreement",
            safety_flags=sorted({flag for result in usable for flag in result.safety_flags}),
            needs_human_review=True,
        )
    care_type, urgency = next(iter(decisions))
    confidence_values = [result.confidence for result in usable if result.confidence is not None]
    return AggregatedTriage(
        status="agreed",
        care_type=care_type,
        urgency=urgency,
        confidence=min(confidence_values) if confidence_values else None,
        safety_flags=sorted({flag for result in usable for flag in result.safety_flags}),
        needs_human_review=True,
    )
