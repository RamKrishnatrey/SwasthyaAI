# SwasthyaAI Triage Service Tests
# Mock ML integration with predict(text, lang) contract
# Tests emergency, urgent, specialist, and general routing

import pytest
from app.services.triage import (
    predict_mock,
    triage_request,
    EMERGENCY_KEYWORDS,
    URGENT_KEYWORDS,
    SPECIALIST_KEYWORDS,
)
from app.schemas import TriageRequest, TriageResponse, CareType, Urgency, ModelSource, EditableSummary, Language


class TestPredictMock:
    """Test mock ML prediction function."""

    def test_emergency_chest_pain(self):
        result = predict_mock("chest pain for 2 hours", "en")
        assert result["care_type"] == CareType.EMERGENCY
        assert result["urgency"] == Urgency.CRITICAL
        assert result["confidence"] >= 0.9
        assert result["model_source"] == ModelSource.MOCK

    def test_emergency_hindi(self):
        result = predict_mock("छाती में दर्द है", "hi")
        assert result["care_type"] == CareType.EMERGENCY
        assert result["urgency"] == Urgency.CRITICAL

    def test_emergency_hinglish(self):
        result = predict_mock("chest pain hai do ghante se", "hinglish")
        assert result["care_type"] == CareType.EMERGENCY
        assert result["urgency"] == Urgency.CRITICAL

    def test_emergency_difficulty_breathing(self):
        result = predict_mock("difficulty breathing", "en")
        assert result["care_type"] == CareType.EMERGENCY
        assert result["urgency"] == Urgency.CRITICAL

    def test_emergency_unconscious(self):
        result = predict_mock("patient unconscious", "en")
        assert result["care_type"] == CareType.EMERGENCY

    def test_emergency_stroke(self):
        result = predict_mock("face drooping arm weakness", "en")
        assert result["care_type"] == CareType.EMERGENCY

    def test_emergency_seizure(self):
        result = predict_mock("seizure convulsion", "en")
        assert result["care_type"] == CareType.EMERGENCY

    def test_emergency_suicidal(self):
        result = predict_mock("want to kill myself", "en")
        assert result["care_type"] == CareType.EMERGENCY

    def test_emergency_bleeding(self):
        result = predict_mock("severe bleeding won't stop", "en")
        assert result["care_type"] == CareType.EMERGENCY

    def test_emergency_pregnancy(self):
        result = predict_mock("pregnant and bleeding", "en")
        assert result["care_type"] == CareType.EMERGENCY

    def test_urgent_high_fever(self):
        result = predict_mock("high fever severe pain", "en")
        assert result["care_type"] == CareType.URGENT_CARE
        assert result["urgency"] == Urgency.HIGH
        assert result["confidence"] >= 0.8

    def test_urgent_vomiting_blood(self):
        result = predict_mock("vomiting blood", "en")
        assert result["care_type"] == CareType.URGENT_CARE
        assert result["urgency"] == Urgency.HIGH

    def test_specialist_cardiology(self):
        result = predict_mock("heart palpitations chest discomfort", "en")
        assert result["care_type"] == CareType.PRIMARY_CARE
        assert result.get("suggested_specialty") == "cardiology"

    def test_specialty_neurology(self):
        result = predict_mock("severe headache migraine dizziness", "en")
        assert result["care_type"] == CareType.PRIMARY_CARE
        assert result.get("suggested_specialty") == "neurology"

    def test_specialty_pulmonology(self):
        result = predict_mock("cough asthma wheezing", "en")
        assert result["care_type"] == CareType.PRIMARY_CARE
        assert result.get("suggested_specialty") == "pulmonology"

    def test_specialty_gastroenterology(self):
        result = predict_mock("stomach pain diarrhea vomiting", "en")
        assert result["care_type"] == CareType.PRIMARY_CARE
        assert result.get("suggested_specialty") == "gastroenterology"

    def test_specialty_orthopedics(self):
        result = predict_mock("joint pain back pain arthritis", "en")
        assert result["care_type"] == CareType.PRIMARY_CARE
        assert result.get("suggested_specialty") == "orthopedics"

    def test_specialty_dermatology(self):
        result = predict_mock("skin rash itching", "en")
        assert result["care_type"] == CareType.PRIMARY_CARE
        assert result.get("suggested_specialty") == "dermatology"

    def test_specialty_gynecology(self):
        result = predict_mock("menstrual problems pregnancy", "en")
        assert result["care_type"] == CareType.PRIMARY_CARE
        assert result.get("suggested_specialty") == "gynecology"

    def test_specialty_pediatrics(self):
        result = predict_mock("child fever vaccination", "en")
        assert result["care_type"] == CareType.PRIMARY_CARE
        assert result.get("suggested_specialty") == "pediatrics"

    def test_specialty_psychiatry(self):
        result = predict_mock("anxiety depression insomnia", "en")
        assert result["care_type"] == CareType.PRIMARY_CARE
        assert result.get("suggested_specialty") == "psychiatry"

    def test_specialty_ent(self):
        result = predict_mock("ear pain throat infection", "en")
        assert result["care_type"] == CareType.PRIMARY_CARE
        assert result.get("suggested_specialty") == "ent"

    def test_specialty_ophthalmology(self):
        result = predict_mock("eye pain blurred vision", "en")
        assert result["care_type"] == CareType.PRIMARY_CARE
        assert result.get("suggested_specialty") == "ophthalmology"

    def test_specialty_urology(self):
        result = predict_mock("burning urination kidney pain", "en")
        assert result["care_type"] == CareType.PRIMARY_CARE
        assert result.get("suggested_specialty") == "urology"

    def test_general_routine(self):
        result = predict_mock("mild headache for a day", "en")
        assert result["care_type"] == CareType.SELF_CARE
        assert result["urgency"] == Urgency.LOW
        assert result["confidence"] >= 0.6

    def test_model_source_present(self):
        result = predict_mock("any symptom", "en")
        assert "model_source" in result
        assert result["model_source"] == ModelSource.MOCK


class TestTriageRequest:
    """Test main triage processing function."""

    def test_emergency_triage(self):
        request = TriageRequest(
            session_id="sess123",
            confirmed_summary=EditableSummary(
                who="self",
                symptoms=["chest_pain", "difficulty_breathing"],
                duration="2 hours",
                age_group="adult",
                language=Language.EN,
                original_text="chest pain and difficulty breathing",
            ),
            language=Language.EN,
        )
        response = triage_request(request)
        assert response.session_id == "sess123"
        assert response.care_type == CareType.EMERGENCY
        assert response.urgency == Urgency.CRITICAL
        assert response.confidence >= 0.9
        assert response.model_source == ModelSource.MOCK
        assert response.reason is not None

    def test_specialist_triage(self):
        request = TriageRequest(
            session_id="sess456",
            confirmed_summary=EditableSummary(
                who="self",
                symptoms=["cough", "difficulty_breathing"],
                duration="3 days",
                age_group="adult",
                language=Language.EN,
                original_text="cough and wheezing for 3 days",
            ),
            language=Language.EN,
        )
        response = triage_request(request)
        assert response.care_type == CareType.PRIMARY_CARE
        assert response.urgency in (Urgency.MODERATE, Urgency.LOW)
        # Note: TriageResponse doesn't have suggested_specialty field (it's internal to prediction)
        # The specialty is used for matching caregivers

    def test_general_triage(self):
        request = TriageRequest(
            session_id="sess789",
            confirmed_summary=EditableSummary(
                who="self",
                symptoms=["headache"],
                duration="1 day",
                age_group="adult",
                language=Language.EN,
                original_text="mild headache since morning",
            ),
            language=Language.EN,
        )
        response = triage_request(request)
        assert response.care_type == CareType.SELF_CARE
        assert response.urgency == Urgency.LOW

    def test_hindi_triage(self):
        request = TriageRequest(
            session_id="sess_hindi",
            confirmed_summary=EditableSummary(
                who="self",
                symptoms=["fever"],
                duration="2 days",
                age_group="adult",
                language=Language.HI,
                original_text="मुझे बुखार है दो दिन से",
            ),
            language=Language.HI,
        )
        response = triage_request(request)
        assert response.care_type in (CareType.SELF_CARE, CareType.PRIMARY_CARE, CareType.URGENT_CARE)
        assert response.model_source == ModelSource.MOCK

    def test_reasoning_generated(self):
        request = TriageRequest(
            session_id="sess_reason",
            confirmed_summary=EditableSummary(
                who="self",
                symptoms=["chest_pain"],
                duration="1 hour",
                age_group="adult",
                language=Language.EN,
                original_text="chest pain",
            ),
            language=Language.EN,
        )
        response = triage_request(request)
        assert response.reason is not None
        assert len(response.reason) > 0
        assert "emergency" in response.reason.lower()


class TestKeywordLists:
    """Test that keyword lists are properly defined."""

    def test_emergency_keywords_not_empty(self):
        assert len(EMERGENCY_KEYWORDS) > 0
        assert "chest pain" in EMERGENCY_KEYWORDS
        assert "दौरा" in EMERGENCY_KEYWORDS  # Hindi seizure

    def test_urgent_keywords_not_empty(self):
        assert len(URGENT_KEYWORDS) > 0
        assert "high fever" in URGENT_KEYWORDS

    def test_specialist_keywords_complete(self):
        expected_specialties = [
            "cardiology", "neurology", "pulmonology", "gastroenterology",
            "orthopedics", "dermatology", "gynecology", "pediatrics",
            "psychiatry", "ent", "ophthalmology", "urology",
        ]
        for spec in expected_specialties:
            assert spec in SPECIALIST_KEYWORDS
            assert len(SPECIALIST_KEYWORDS[spec]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])