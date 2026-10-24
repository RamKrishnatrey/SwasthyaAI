import asyncio
import json
import os
from urllib.request import Request, urlopen

from backend.swasthyaai.agent.contracts import AgentResponse


class GeminiWordingAdapter:
    def __init__(self, timeout_seconds: float = 8.0):
        self.timeout_seconds = timeout_seconds

    async def rephrase(self, response: AgentResponse, consent: bool) -> str | None:
        if not consent or not os.environ.get("GEMINI_API_KEY"):
            return None
        payload = {
            "contents": [{"parts": [{
                "text": "Rewrite the supplied healthcare coordination message clearly and empathetically. "
                        "Do not add medical advice, diagnosis, urgency, or actions. Return only wording.\n"
                        + response.response[:2000]
            }]}],
            "generationConfig": {"temperature": 0, "maxOutputTokens": 256},
        }
        try:
            wording = await asyncio.wait_for(
                asyncio.to_thread(self._generate, payload),
                timeout=self.timeout_seconds,
            )
            return wording.strip()[:2000] or None
        except Exception:
            return None

    def _generate(self, payload: dict) -> str:
        key = os.environ["GEMINI_API_KEY"]
        request = Request(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + key,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=self.timeout_seconds) as result:
            body = json.loads(result.read(65536))
        return body["candidates"][0]["content"]["parts"][0]["text"]
