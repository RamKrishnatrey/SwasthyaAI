from typing import Protocol

from backend.swasthyaai.agent.contracts import AgentInput, ModelResult


class ModelAdapter(Protocol):
    name: str
    version: str
    task: str
    languages: set[str]
    timeout_seconds: float

    async def predict(self, text: str, context: dict) -> ModelResult: ...


class ModelRegistry:
    def __init__(self, adapters: list[ModelAdapter] | None = None):
        self.adapters = list(adapters or [])

    def relevant(self, request: AgentInput) -> list[ModelAdapter]:
        request_language = request.language
        return [
            adapter for adapter in self.adapters
            if adapter.task == request.task
            and (request_language == "auto" or request_language in adapter.languages)
        ]

    def status(self) -> list[dict]:
        return [
            {
                "name": adapter.name,
                "version": adapter.version,
                "task": adapter.task,
                "languages": sorted(adapter.languages),
                "status": "available",
            }
            for adapter in self.adapters
        ]
