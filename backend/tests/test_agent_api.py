import asyncio

import httpx

from backend.app import assess_request
from backend.swasthyaai.main import create_app


def test_agent_turn_returns_the_stable_emergency_contract():
    async def request():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=create_app()),
            base_url="http://test",
        ) as client:
            return await client.post(
                "/api/v1/agent/turn",
                json={
                    "session_id": "demo-session",
                    "user_message": "chest pain ho raha hai",
                    "language": "Hinglish",
                    "external_ai_consent": False,
                },
            )

    response = asyncio.run(request())

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "emergency"
    assert body["care_type"] == "emergency_112"
    assert body["urgency"] == "emergency"
    assert body["matched_caregivers"] == []
    assert body["aggregation_status"] == "fallback"
    assert "112" in body["response"]


def test_agent_turn_rejects_oversized_messages():
    async def request():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=create_app()),
            base_url="http://test",
        ) as client:
            return await client.post(
                "/api/v1/agent/turn",
                json={"session_id": "s1", "user_message": "x" * 5000},
            )

    assert asyncio.run(request()).status_code == 422


def test_legacy_assess_response_keeps_compatible_keys_and_112_guidance():
    result = assess_request("severe chest pain")

    assert result["route"] == "EMERGENCY_HELP"
    assert result["urgency"] == "emergency"
    assert result["needs_human_review"] is True
    assert "112" in result["message"]
