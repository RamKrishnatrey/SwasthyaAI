from app.schemas import IntakeRequest, Language
from app.services.intake import extract_age_group, process_intake


def test_extract_age_from_conversational_answer():
    assert extract_age_group("I am 22") == "adult"
    assert extract_age_group("age is 70") == "elderly"
    assert extract_age_group("child") == "child"


def test_intake_keeps_fields_when_user_answers_in_separate_turns():
    response = process_intake(
        IntakeRequest(
            text="I have a headache. Me. For 2 days. I am 22.",
            session_id="test-session",
            language_hint=Language.EN,
        )
    )
    assert response.extracted.who == "self"
    assert "headache" in response.extracted.symptoms
    assert response.extracted.duration == "2 days"
    assert response.extracted.age_group == "adult"
    assert response.is_complete is True
