# SwasthyaAI Agent v2 (additive)

This is a separate, self-contained prototype under `ai_agent_v2/`. It does not replace existing app files.

## What works
- FastAPI API at `/api/agent`, health check at `/api/health`, and interactive UI at `/`
- Emergency red-flag phrase checks run before inference or caregiver matching
- Follow-up question for very short intake
- Word/character TF-IDF + LinearSVC experimental urgency classifier with held-out metrics
- Fictional caregiver examples for UI demonstration
- Tests for API behavior and emergency bypass

## Run locally (PowerShell)
From `ai_agent_v2`:
```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe train.py --data .\data\multilingual_medical_symptom_triage.csv
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn app:app --reload --host 127.0.0.1 --port 8010
```
Open `http://127.0.0.1:8010`; API docs: `http://127.0.0.1:8010/docs`.

Place your downloaded CSV at `ai_agent_v2/data/multilingual_medical_symptom_triage.csv` locally. Raw data and trained model binaries are ignored by Git. The trainer expects an `urgency`/label column and prefers `symptom_1`, `symptom_2`, `symptom_3`; it intentionally does not use the `severity` column as that may directly encode the target. If the schema differs, inspect it and adapt the loader instead of guessing.

## Safety and limitations
This is a hackathon prototype, not a medical device. Public dataset labels may be synthetic, rule-generated, biased, or clinically unverified; held-out scores measure agreement with these labels, not clinical safety. Phrase-based safety checks are incomplete and may miss emergencies. Users with possible emergencies should contact their local emergency number immediately. No diagnosis or prescriptions. Caregiver profiles are fictional, not real provider availability. Do not enter real patient information.
