"""Optional speech-to-text proxy for recorded mobile audio.
Requires a configured OpenAI-compatible provider that supports /audio/transcriptions.
The server never returns or exposes provider credentials.
"""
from fastapi import APIRouter, File, HTTPException, UploadFile
import httpx
from app.config import get_settings

router = APIRouter(prefix="/api/voice", tags=["voice"])

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    settings = get_settings()
    if not settings.llm_api_key.strip():
        raise HTTPException(status_code=503, detail="Voice transcription is not configured. Set LLM_API_KEY on the backend.")
    allowed = {"audio/mpeg", "audio/mp3", "audio/mp4", "audio/m4a", "audio/wav", "audio/x-wav", "audio/webm", "audio/ogg", "application/octet-stream"}
    if file.content_type and file.content_type not in allowed:
        raise HTTPException(status_code=415, detail="Unsupported audio format. Use a common audio recording format.")
    data = await file.read(20 * 1024 * 1024 + 1)
    if not data:
        raise HTTPException(status_code=400, detail="The uploaded recording is empty.")
    if len(data) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Recording exceeds the 20 MB limit.")
    endpoint = settings.llm_base_url.rstrip("/") + "/audio/transcriptions"
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=5.0)) as client:
            response = await client.post(
                endpoint,
                headers={"Authorization": f"Bearer {settings.llm_api_key}"},
                data={"model": "whisper-1"},
                files={"file": (file.filename or "recording.m4a", data, file.content_type or "application/octet-stream")},
            )
            response.raise_for_status()
            result = response.json()
            text = result.get("text")
            if not isinstance(text, str) or not text.strip():
                raise HTTPException(status_code=502, detail="The speech provider returned no transcript.")
            return {"text": text.strip()}
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail="Speech provider rejected the recording. Check the configured provider and transcription model.") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Speech provider could not be reached.") from exc
