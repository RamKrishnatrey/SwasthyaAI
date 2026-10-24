# SwasthyaAI AI-Agent Additions

This directory is intentionally additive. It does not replace or modify any existing application file.

## Current repository findings

The existing repository already has:
- FastAPI endpoints and Pydantic contracts
- A controlled agent dispatcher and experimental text adapter
- A red-flag safety matcher and conversation follow-up state
- Caregiver ranking logic
- Experimental urgency models and metric files
- React/Vite frontend and backend tests

## Important integration gaps to address separately

1. The existing local model adapter emits a fixed teleconsultation/same-day result when it predicts a class. Its comment correctly warns that the experimental disease-class output is not a validated care-routing label. Do not treat that mapping as a clinically grounded prediction.
2. The urgency training script must be aligned with the *actual CSV schema*. The local CSV shown in PowerShell has fields such as `row_searchable_text`, `severity`, `symptom_1`–`symptom_3`, and `urgency`; the existing `train_urgency_v2.py` currently reads a Hugging Face dataset with `patient_query`. Validate dataset schema before running either path.
3. Red-flag phrase matching is a conservative safety adjunct, not a complete clinical safety screen. Negative-context handling and Hindi/Hinglish variants require dedicated tests and clinical review.
4. The agent uses a fixed India emergency number in one response. For broader deployments, emergency instructions must be locale-configurable and validated; never infer a user's emergency number from language alone.
5. Do not perform caregiver matching after a red flag; preserve the existing emergency early-return design.
6. Do not commit dataset rows that include `patient_id`, raw health narratives, credentials, or API keys. `.gitignore` already excludes common data and environment paths; double-check before every push.

## Safe local validation

Run the project tests from PowerShell:

```powershell
py -m pip install -r backend/requirements.txt
py -m pip install pytest httpx
py -m pytest backend/tests -q
```

If optional model/provider dependencies are needed, install only the relevant documented requirements. Do not add secrets to tracked files.

## Safety and intended use

This is a development/demo platform, not a medical device. Model outputs are experimental and are not diagnoses, prescriptions, or a substitute for professional evaluation. A missed emergency red flag is possible; users experiencing a possible emergency should contact their local emergency services without waiting for this app. All model updates require held-out evaluation and review before demo use.