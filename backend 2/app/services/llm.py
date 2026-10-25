"""General-purpose chat via an OpenAI-compatible API or a local Ollama server.

No paid API key is required when Ollama is running locally. Keys stay server-side.
"""
from __future__ import annotations

import httpx
from app.config import get_settings

SYSTEM_PROMPT = """You are SwasthyaAI, a helpful general-purpose assistant.
Answer the user's actual question directly and naturally. You can discuss coding,
technology, science, studies, writing, planning, everyday topics, and general health
information. Use the conversation history for context, and answer in the user's
language (English, Hindi, or Hinglish). Be clear, useful, and honest about uncertainty.
For medical topics, provide general information only: do not claim to diagnose, do not
prescribe medication or dosages, and recommend a qualified professional for personal
medical decisions. For possible immediate danger, advise contacting local emergency
services. Never invent facts or claim a model/tool was used when it was not.
"""

async def generate_reply(messages: list[dict[str, str]], language: str) -> str | None:
    """Return a model reply, or None if no provider is configured/reachable."""
    settings = get_settings()
    base_url = settings.llm_base_url.rstrip("/")
    local_ollama = "localhost:11434" in base_url or "127.0.0.1:11434" in base_url
    if not settings.llm_api_key.strip() and not local_ollama:
        return None

    payload = {
        "model": settings.llm_model,
        "temperature": 0.4,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT + f" Preferred language: {language}."},
            *messages[-16:],
        ],
    }
    headers = {"Content-Type": "application/json"}
    if settings.llm_api_key.strip():
        headers["Authorization"] = f"Bearer {settings.llm_api_key}"
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(90.0, connect=5.0)) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            if isinstance(answer, str) and answer.strip():
                return answer.strip()[:6000]
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError):
        return None
    return None
