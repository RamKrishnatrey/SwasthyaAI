# Local text-model agent integration

This small module connects an optional locally saved scikit-learn text classifier to the existing SwasthyaAI agent registry.

## Configure it

Place a compatible saved scikit-learn pipeline at one of the default locations:

- `models/best_text_model.joblib`
- `models/medical_text_baseline.joblib`
- `artifacts/best_text_model.joblib`

Or set `SWASTHYAAI_TEXT_MODEL` to the exact path. Keep model artifacts and training datasets out of Git unless you have reviewed size, provenance, and license requirements.

Register the adapter in `backend/swasthyaai/agent/service.py` by initializing `MODEL_REGISTRY` with `LocalTextNavigationAdapter()`. The existing deterministic red-flag gate executes before model dispatch and must remain ahead of every model.

## Safety and limitations

The experimental classifier predicts six synthetic dataset labels (Dengue, Diarrhea, Influenza, Measles, Pneumonia, Typhoid). Those labels are not care-type or urgency labels. This adapter therefore records the classifier label only as a feature summary and returns conservative navigation to teleconsultation with same-day review; it does not present the disease label as a diagnosis, claim calibrated confidence, or change the existing emergency path. This is a prototype mapping for integration testing, not a clinically validated recommendation engine.

If the model is missing or cannot be loaded, the adapter returns an explicit `unavailable` result. The agent should not fabricate a result in that case.

## Test

From the repository root:

```powershell
python -m pytest backend/tests/agent/test_local_model.py
```
