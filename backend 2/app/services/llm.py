"""Optional OpenAI-compatible conversational layer.

This service generates a supportive, multilingual explanation only. Deterministic
SafetyShield and rule-based prototype triage run independently and take precedence.
Never send API keys to the browser.
"""
from __future__ import annotations

import httpx

from app.config import get_settings

SYSTEM_PROMPT = """You are SwasthyaAI, a careful health-navigation assistant, not a doctor.
Respond in the user's language (English, Hindi, or Hinglish). Be calm, empathetic,
and concise. Do not diagnose, prescribe medicines, recommend dosages, or claim
certainty. Ask at most one focused follow-up question at a time. Do not repeat
questions already answered in the conversation. If symptoms may be severe or
worsening, advise prompt professional care. For immediate danger, tell the user
to contact local emergency services. Never claim you are a clinician. Clearly
say this is informational support, not a diagnosis. Do not invent patient facts.
"""

async def generate_reply(messages: list[dict[str, str]], language: str) -> str | None:
    """Return a provider reply, or None when provider is not configured/unavailable."""
    settings = get_settings()
    if not settings.llm_api_key.strip():
        return None

    base_url = settings.llm_base_url.rstrip("/")
    endpoint = f"{base_url}/chat/completions"
    payload = {
        "model": settings.llm_model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT + f" Preferred language: {language}."},
            *messages[-12:],
        ],
    }
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(25.0, connect=5.0)) as client:
            response = await client.post(
                endpoint,
                headers={"Authorization": f"Bearer {settings.llm_api_key}", "Content-Type": "application/json"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            text = data["choices"][0]["message"]["content"]
            if isinstance(text, str) and text.strip():
                return text.strip()[:4000]
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError):
        # Safe local fallback: a provider outage must not fabricate a model answer.
        return None
    return None
