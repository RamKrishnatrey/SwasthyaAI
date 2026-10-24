# SwasthyaAI jury demo — Backend 2 + latest frontend

This path uses the `backend 2` FastAPI application and the latest React/Vite frontend. It connects the web care-check chat to backend 2's intake, follow-up, SafetyShield, and prototype triage services through `POST /api/agent/message`.

## 1. Start backend 2 (PowerShell)

Open PowerShell in the repository root:

```powershell
cd "backend 2"
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env -ErrorAction SilentlyContinue
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Leave this terminal running. Check the backend at:

- Health: http://127.0.0.1:8000/health
- API docs: http://127.0.0.1:8000/docs

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

## 3. Quick API check

With backend 2 running, open:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

The live frontend agent route is `POST http://127.0.0.1:8000/api/agent/message`. The backend bridge asks follow-up questions from backend 2 intake, applies its SafetyShield rules, then returns the current prototype triage response.

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
