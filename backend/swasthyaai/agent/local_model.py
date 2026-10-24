"""Local scikit-learn adapter for SwasthyaAI's care-navigation agent.

This adapter only maps the experimental six-class text classifier to a bounded,
non-clinical care-navigation result. It intentionally does not infer a disease,
urgency, or emergency status from the disease classifier.
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any

import joblib

from backend.swasthyaai.agent.contracts import CareType, ModelResult


class LocalTextNavigationAdapter:
    """Load a saved classifier lazily and emit a conservative agent result."""

    name = "local-text-classifier"
    version = "0.1.0"
    task = "care_triage"
    languages = {"English"}
    timeout_seconds = 2.0

    def __init__(self, model_path: str | Path | None = None) -> None:
        configured = model_path or os.getenv("SWASTHYAAI_TEXT_MODEL")
        self.model_path = Path(configured) if configured else None
        self._model: Any | None = None
        self._load_error: str | None = None

    def _resolve_model_path(self) -> Path | None:
        if self.model_path:
            return self.model_path
        # Typical repository/local training locations; model files are not
        # committed by this feature and can be provided by the developer.
        candidates = [
            Path("models/best_text_model.joblib"),
            Path("models/medical_text_baseline.joblib"),
            Path("artifacts/best_text_model.joblib"),
        ]
        return next((path for path in candidates if path.is_file()), None)

    def _load(self) -> Any | None:
        if self._model is not None:
            return self._model
        path = self._resolve_model_path()
        if path is None or not path.is_file():
            self._load_error = "model_file_not_found"
            return None
        try:
            self._model = joblib.load(path)
            return self._model
        except Exception:
            # Do not expose local paths or serialized object details to callers.
            self._load_error = "model_load_failed"
            return None

    async def predict(self, text: str, context: dict) -> ModelResult:
        model = await asyncio.to_thread(self._load)
        if model is None:
            return ModelResult(
                name=self.name,
                version=self.version,
                task=self.task,
                status="unavailable",
                feature_summary=[self._load_error or "model_unavailable"],
            )

        try:
            label = await asyncio.to_thread(lambda: str(model.predict([text])[0]))
        except Exception:
            return ModelResult(
                name=self.name,
                version=self.version,
                task=self.task,
                status="failed",
                feature_summary=["inference_failed"],
            )

        # Disease labels are not clinically validated care-routing labels. The
        # prediction is recorded only as a non-diagnostic feature summary.
        return ModelResult(
            name=self.name,
            version=self.version,
            task=self.task,
            status="used",
            care_type=CareType.TELECONSULTATION,
            urgency="same_day",
            confidence=None,
            safety_flags=[],
            feature_summary=[f"experimental_class_label:{label}"],
        )
