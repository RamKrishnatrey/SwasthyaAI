import pytest

from backend.swasthyaai.agent.safety import detect_red_flags


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("I have severe chest pain", "chest_pain"),
        ("सांस नहीं आ रही", "breathlessness"),
        ("saans lene mein dikkat ho rahi hai", "breathlessness"),
        ("Papa behosh ho gaye", "unconsciousness"),
        ("accident ke baad bleeding ruk nahi rahi", "severe_bleeding"),
    ],
)
def test_detects_red_flags_in_english_hindi_and_hinglish(message, expected):
    assert expected in detect_red_flags(message)


@pytest.mark.parametrize(
    "message",
    ["I have no chest pain", "There is no difficulty breathing"],
)
def test_does_not_flag_negated_symptoms(message):
    assert detect_red_flags(message) == []
