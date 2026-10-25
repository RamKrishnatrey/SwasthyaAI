# SwasthyaAI jury demo — Backend 2 + latest frontend

This path uses the `backend 2` FastAPI application and the latest React/Vite frontend. It connects the web care-check chat to backend 2's intake, follow-up, SafetyShield, and prototype triage services through `POST /api/agent/message`.

## 1. Start backend 2 (PowerShell)

Open PowerShell in the repository root:

```powershell
cd "backend 2"
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
Copy-Item .env.example .env -ErrorAction SilentlyContinue
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Leave this terminal running. Check the backend at:

- Health: http://127.0.0.1:8001/health
- API docs: http://127.0.0.1:8001/docs

If `py -3.11` is unavailable, use an installed Python 3.11+ interpreter.

## 2. Start the latest frontend

Open a second PowerShell in the repository root:

```powershell
cd frontend
npm install
Copy-Item .env.example .env.local -ErrorAction SilentlyContinue
npm run dev
```

Open the Vite URL printed in the terminal (usually http://localhost:5173). The frontend is configured for live backend mode by default. To explicitly run the clearly labeled demo fixtures instead, set `VITE_DEMO_MODE=true` in `frontend/.env.local` and restart Vite.

## Optional LLM conversation replies

The backend can use an OpenAI-compatible Chat Completions API for multilingual conversational replies. Without a key, it safely falls back to the local rule-based prototype response. The LLM key stays on the backend and is never sent to the frontend.

In `backend 2/.env`, set these values (never commit the real key):

```dotenv
LLM_API_KEY=your_provider_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

For an OpenAI-compatible provider, use its documented API base URL and model ID. Restart the backend after editing `.env`. API usage may incur charges depending on the provider. The LLM is for conversation only; triage is still rule-based and is not clinically validated.

## 3. Quick API check

With backend 2 running, open:

```powershell
Invoke-RestMethod http://127.0.0.1:8001/health
```

The live frontend agent route is `POST http://127.0.0.1:8001/api/agent/message`. The backend bridge asks follow-up questions from backend 2 intake, applies its SafetyShield rules, then returns the current prototype triage response.

## Dataset download and data-quality review (PowerShell)

Run from the repository root after activating the backend virtual environment:

```powershell
cd "backend 2"
pip install -e ".[data]"
python scripts/download_datasets.py --dataset intelmedica/nursing-sentences-1 --dataset intelmedica/medical-tts-parquet-1
python scripts/evaluate_dataset.py data/raw/intelmedica__nursing-sentences-1 --output nursing-profile.json
```

The downloader records repository metadata and only downloads common data/audio file types. If a dataset is gated, use the normal Hugging Face login and access process; do not bypass permissions. Review each dataset card, license, schema, privacy implications, and suitability before use. The profile script reports data quality only. **Neither script trains or clinically evaluates a model.**

## Optional labeled-data baseline training (research only)

The selected nursing-sentence and medical-TTS repositories may be useful for language/voice work, but they are not automatically labeled symptom-to-urgency examples. Do not train a triage model on them as if they were clinical labels. If you obtain a properly licensed, de-identified, reviewed dataset with explicit text and target-label columns, you can train a generic research baseline:

```powershell
cd "backend 2"
pip install -e ".[ml]"
python scripts/train_baseline.py path\to\labeled.csv --text-column text --label-column label
```

The script makes a reproducible train/test split and writes a model plus accuracy, per-class metrics, and confusion matrix under `artifacts/research_baseline`. This is **not clinical validation** and is not wired into the live triage path. Do not use the resulting model for diagnosis or care decisions. Training has not been run because no suitable labeled dataset has been confirmed in the repository.

## Mobile voice

The mobile chat screen now supports recording a short audio message, sending it to the optional backend transcription endpoint, inserting the transcript into the composer, and reading assistant messages aloud. Transcription requires a provider that supports the configured OpenAI-compatible `/audio/transcriptions` endpoint and the `whisper-1` model ID; providers may differ. The recording is sent to that configured provider. Do not send sensitive medical audio unless you have appropriate consent and understand the provider's privacy terms.

## Important limitations for the jury

- The current `backend 2/app/services/triage.py` explicitly uses a rule-based mock/prototype model. This bridge does **not** claim that all saved/trained models are integrated or clinically validated.
- DDXPlus requires its own compatible files under `models/ddxplus`; saved urgency artifacts under `artifacts/` are not automatically loaded by backend 2.
- TinyFish requires a valid server-side `TINYFISH_API_KEY`; without it, live TinyFish calls cannot be verified.
- The mobile app exists in the repository, but its current chat screen imports a service module that is not present in the checked-in tree, and its voice-input handler is a placeholder. Mobile should be presented as a separate incomplete workstream until those gaps are fixed and Expo Go is tested.
- This is a prototype for demonstration only, not a diagnosis or a clinical decision tool. Use synthetic data only.

## Changes in this integration branch

- Adds a frontend-compatible `/api/agent/message` bridge to backend 2.
- Routes the latest frontend to the live backend by default; demo fixtures remain opt-in.
- Leaves the original `backend/`, model artifacts, mobile source, and `main` branch unchanged.
