# SwasthyaAI Intake Service Tests
# Language detection, field extraction, follow-up selection

import pytest
from app.services.intake import (
    detect_language,
    extract_who,
    extract_symptoms,
    extract_duration,
    extract_age_group,
    extract_fields,
    select_follow_ups,
    build_editable_summary,
    process_intake,
    process_follow_up,
)
from app.schemas import IntakeRequest, ExtractedFields, Language


class TestLanguageDetection:
    """Test language detection."""

    def test_english(self):
        assert detect_language("I have a headache") == Language.EN
        assert detect_language("Chest pain for 2 days") == Language.EN
        assert detect_language("Help me") == Language.EN

    def test_hindi_devanagari(self):
        assert detect_language("मुझे बुखार है") == Language.HI
        assert detect_language("सीने में दर्द") == Language.HI
        assert detect_language("सर दर्द है") == Language.HI

    def test_hinglish(self):
        assert detect_language("mujhe bukhar hai") == Language.HINGLISH
        assert detect_language("chest pain hai do din se") == Language.HINGLISH
        assert detect_language("sir dard ho raha hai") == Language.HINGLISH
        assert detect_language("saans lene mein dikkat") == Language.HINGLISH

    def test_mixed_script_prefers_hindi(self):
        # Devanagari present -> Hindi
        assert detect_language("I have बुखार") == Language.HI

    def test_short_english(self):
        assert detect_language("OK") == Language.EN

    def test_empty(self):
        assert detect_language("") == Language.EN
        assert detect_language(None) == Language.EN


class TestWhoExtraction:
    """Test who extraction."""

    def test_self_english(self):
        assert extract_who("I have fever") == "self"
        assert extract_who("me and my headache") == "self"

    def test_self_hindi(self):
        assert extract_who("mujhe bukhar hai") == "self"
        assert extract_who("mere pet me dard") == "self"

    def test_mother(self):
        assert extract_who("mother has fever") == "mother"
        assert extract_who("maa ko bukhar") == "mother"
        assert extract_who("mummy ki tabiyat kharab") == "mother"

    def test_father(self):
        assert extract_who("father has chest pain") == "father"
        assert extract_who("papa ko dard") == "father"

    def test_child(self):
        assert extract_who("child has fever") == "child"
        assert extract_who("baccha bemar hai") == "child"
        assert extract_who("beti ko bukhar") == "child"

    def test_elderly(self):
        assert extract_who("elderly person fell") == "elderly"
        assert extract_who("dadi ko chot lagi") == "elderly"

    def test_spouse(self):
        assert extract_who("wife is unwell") == "spouse"
        assert extract_who("pati ko dard") == "spouse"

    def test_none(self):
        assert extract_who("fever for 2 days") is None
        assert extract_who("") is None


class TestSymptomExtraction:
    """Test symptom extraction."""

    def test_fever_variations(self):
        symptoms = extract_symptoms("I have fever")
        assert "fever" in symptoms
        symptoms = extract_symptoms("bukhar hai")
        assert "fever" in symptoms
        symptoms = extract_symptoms("temperature 102")
        assert "fever" in symptoms

    def test_cough(self):
        symptoms = extract_symptoms("cough for 3 days")
        assert "cough" in symptoms
        symptoms = extract_symptoms("khansi nahi ruk rahi")
        assert "cough" in symptoms

    def test_headache(self):
        symptoms = extract_symptoms("headache since morning")
        assert "headache" in symptoms
        symptoms = extract_symptoms("sir dard ho raha")
        assert "headache" in symptoms

    def test_multiple_symptoms(self):
        symptoms = extract_symptoms("fever and cough and headache")
        assert len(symptoms) >= 3
        assert "fever" in symptoms
        assert "cough" in symptoms
        assert "headache" in symptoms

    def test_chest_pain(self):
        symptoms = extract_symptoms("chest pain")
        assert "chest_pain" in symptoms
        symptoms = extract_symptoms("seene me dard")
        assert "chest_pain" in symptoms

    def test_breathing(self):
        symptoms = extract_symptoms("difficulty breathing")
        assert "difficulty_breathing" in symptoms
        symptoms = extract_symptoms("saans lene mein dikkat")
        assert "difficulty_breathing" in symptoms

    def test_no_symptoms(self):
        symptoms = extract_symptoms("I am fine")
        assert symptoms == []


class TestDurationExtraction:
    """Test duration extraction."""

    def test_days(self):
        assert extract_duration("fever for 2 days") == "2 days"
        assert extract_duration("2 din se bukhar") == "2 days"
        assert extract_duration("teen din se") is not None

    def test_hours(self):
        assert extract_duration("pain for 3 hours") == "3 hours"
        assert extract_duration("do ghante se dard") == "2 hours"

    def test_minutes(self):
        assert extract_duration("started 30 minutes ago") == "30 minutes"

    def test_weeks(self):
        assert extract_duration("1 week") == "1 weeks"

    def test_relative(self):
        assert extract_duration("since yesterday") == "1 day"
        assert extract_duration("kal se") == "1 day"
        assert extract_duration("last night") == "since last night"

    def test_vague(self):
        assert extract_duration("a few days") == "a few days"
        assert extract_duration("sudden onset") == "sudden onset"

    def test_none(self):
        assert extract_duration("I have fever") is None


class TestAgeGroupExtraction:
    """Test age group extraction."""

    def test_explicit_age_groups(self):
        assert extract_age_group("infant has fever") == "infant"
        assert extract_age_group("child is sick") == "child"
        assert extract_age_group("elderly patient") == "elderly"

    def test_age_numbers(self):
        assert extract_age_group("3 month old baby") == "infant"
        assert extract_age_group("5 year old child") == "child"
        assert extract_age_group("25 year old man") == "adult"
        assert extract_age_group("70 year old") == "elderly"

    def test_none(self):
        assert extract_age_group("I have fever") is None


class TestFullExtraction:
    """Test full field extraction."""

    def test_complete_extraction(self):
        extracted = extract_fields("mujhe bukhar hai do din se", Language.HINGLISH)
        assert extracted.who == "self"
        assert "fever" in extracted.symptoms
        assert extracted.duration == "2 days"
        assert extracted.language == Language.HINGLISH

    def test_partial_extraction(self):
        extracted = extract_fields("chest pain", Language.EN)
        assert "chest_pain" in extracted.symptoms
        assert extracted.who is None
        assert extracted.duration is None


class TestFollowUpSelection:
    """Test follow-up question selection."""

    def test_all_missing(self):
        extracted = ExtractedFields(
            who=None, symptoms=[], duration=None, age_group=None, language=Language.EN
        )
        follow_ups = select_follow_ups(extracted)
        # Should have questions for all 4 required fields
        assert len(follow_ups) >= 4
        fields = {f.field for f in follow_ups}
        assert "who" in fields
        assert "symptoms" in fields
        assert "duration" in fields
        assert "age_group" in fields

    def test_some_missing(self):
        extracted = ExtractedFields(
            who="self", symptoms=["fever"], duration=None, age_group=None, language=Language.EN
        )
        follow_ups = select_follow_ups(extracted)
        fields = {f.field for f in follow_ups}
        assert "who" not in fields
        assert "symptoms" not in fields
        assert "duration" in fields
        assert "age_group" in fields

    def test_complete(self):
        extracted = ExtractedFields(
            who="self", symptoms=["fever"], duration="2 days", age_group="adult", language=Language.EN
        )
        follow_ups = select_follow_ups(extracted)
        assert follow_ups == []


class TestEditableSummary:
    """Test editable summary building."""

    def test_build_summary(self):
        extracted = ExtractedFields(
            who="self", symptoms=["fever", "cough"], duration="2 days", age_group="adult", language=Language.EN
        )
        summary = build_editable_summary(extracted, "original text")
        assert summary.who == "self"
        assert summary.symptoms == ["fever", "cough"]
        assert summary.duration == "2 days"
        assert summary.age_group == "adult"
        assert summary.language == Language.EN
        assert summary.original_text == "original text"


class TestProcessIntake:
    """Test main intake processing."""

    def test_english_intake(self):
        request = IntakeRequest(text="I have fever for 2 days", language_hint=Language.EN)
        response = process_intake(request)
        assert response.session_id is not None
        assert response.language == Language.EN
        assert "fever" in response.extracted.symptoms
        assert response.extracted.duration == "2 days"

    def test_hindi_intake(self):
        request = IntakeRequest(text="मुझे बुखार है दो दिन से", language_hint=Language.HI)
        response = process_intake(request)
        assert response.language == Language.HI
        assert "fever" in response.extracted.symptoms

    def test_hinglish_intake(self):
        request = IntakeRequest(text="mujhe bukhar hai do din se")
        response = process_intake(request)
        assert response.language == Language.HINGLISH
        assert "fever" in response.extracted.symptoms

    def test_generates_session_id(self):
        request = IntakeRequest(text="test")
        response = process_intake(request)
        assert response.session_id is not None
        assert len(response.session_id) == 8


class TestProcessFollowUp:
    """Test follow-up processing."""

    def test_follow_up_updates_fields(self):
        previous = ExtractedFields(
            who="self", symptoms=["fever"], duration=None, age_group=None, language=Language.EN
        )
        response = process_follow_up("sess123", {"duration": "3 days", "age_group": "adult"}, previous)
        assert response.extracted.duration == "3 days"
        assert response.extracted.age_group == "adult"
        assert response.extracted.who == "self"
        assert response.extracted.symptoms == ["fever"]

    def test_follow_up_completes(self):
        previous = ExtractedFields(
            who="self", symptoms=["fever"], duration="2 days", age_group="adult", language=Language.EN
        )
        response = process_follow_up("sess123", {}, previous)
        assert response.is_complete is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])