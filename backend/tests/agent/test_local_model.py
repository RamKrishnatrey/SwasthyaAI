import asyncio

from backend.swasthyaai.agent.local_model import LocalTextNavigationAdapter


class FakeClassifier:
    def predict(self, texts):
        return ["Dengue"]


def test_adapter_maps_label_to_non_diagnostic_navigation(monkeypatch):
    adapter = LocalTextNavigationAdapter(model_path="unused.joblib")
    monkeypatch.setattr(adapter, "_load", lambda: FakeClassifier())

    result = asyncio.run(adapter.predict("fever and headache", {}))

    assert result.status == "used"
    assert result.care_type == "teleconsultation"
    assert result.urgency == "same_day"
    assert result.confidence is None
    assert result.feature_summary == ["experimental_class_label:Dengue"]


def test_missing_model_is_explicitly_unavailable(monkeypatch):
    adapter = LocalTextNavigationAdapter(model_path="missing.joblib")
    def no_model():
        adapter._load_error = "model_file_not_found"
        return None

    monkeypatch.setattr(adapter, "_load", no_model)

    result = asyncio.run(adapter.predict("test symptom description", {}))

    assert result.status == "unavailable"
    assert result.care_type is None
    assert result.urgency is None
