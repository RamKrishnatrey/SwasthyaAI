from types import SimpleNamespace

import pytest

from app.services import llm


@pytest.mark.asyncio
async def test_generate_reply_uses_safe_fallback_without_api_key(monkeypatch):
    monkeypatch.setattr(
        llm,
        "get_settings",
        lambda: SimpleNamespace(llm_api_key="", llm_base_url="https://example.invalid/v1", llm_model="test"),
    )

    reply = await llm.generate_reply([{"role": "user", "content": "I have a headache"}], "en")

    assert reply is None
