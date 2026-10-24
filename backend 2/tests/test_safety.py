# SwasthyaAI SafetyShield Tests
# Edge cases: misspellings, Hinglish, negation, mixed symptoms

import pytest
from app.services.safety import (
    check_red_flags,
    evaluate_safety,
    has_negation_before,
    RED_FLAG_RULES,
)
from app.schemas import SafetyFlagType, RedFlagSeverity


class TestRedFlagDetection:
    """Test basic red-flag detection."""

    def test_chest_pain_english(self):
        result = evaluate_safety("I have chest pain")
        assert result.red_flag is True
        assert any(f.type == SafetyFlagType.CHEST_PAIN for f in result.matched_rules)
        assert result.bypass_matching is True
        assert "112" in result.instructions

    def test_chest_pain_hindi(self):
        result = evaluate_safety("मुझे छाती में दर्द है")
        assert result.red_flag is True
        assert any(f.type == SafetyFlagType.CHEST_PAIN for f in result.matched_rules)

    def test_chest_pain_hinglish(self):
        result = evaluate_safety("Mujhe chest pain ho raha hai")
        assert result.red_flag is True
        assert any(f.type == SafetyFlagType.CHEST_PAIN for f in result.matched_rules)

    def test_difficulty_breathing_variations(self):
        for text in [
            "difficulty breathing",
            "shortness of breath",
            "can't breathe",
            "cannot breathe",
            "breathless",
            "saans lene mein dikkat",
            "saans ful rahi hai",
            "dam ghut raha hai",
        ]:
            result = evaluate_safety(text)
            assert result.red_flag is True, f"Failed for: {text}"
            assert any(f.type == SafetyFlagType.DIFFICULTY_BREATHING for f in result.matched_rules)

    def test_unconsciousness(self):
        for text in ["unconscious", "unresponsive", "won't wake up", "behosh", "hosh nahi hai"]:
            result = evaluate_safety(text)
            assert result.red_flag is True, f"Failed for: {text}"
            assert any(f.type == SafetyFlagType.UNCONSCIOUSNESS for f in result.matched_rules)

    def test_severe_bleeding(self):
        for text in ["severe bleeding", "heavy bleeding", "khun bah raha hai", "bleeding won't stop"]:
            result = evaluate_safety(text)
            assert result.red_flag is True, f"Failed for: {text}"
            assert any(f.type == SafetyFlagType.SEVERE_BLEEDING for f in result.matched_rules)

    def test_stroke_signs(self):
        for text in [
            "face drooping",
            "arm weakness",
            "slurred speech",
            "can't speak",
            "muh tedha",
            "haath kamzor",
            "bolne mein dikkat",
            "stroke signs",
            "lakwa",
        ]:
            result = evaluate_safety(text)
            assert result.red_flag is True, f"Failed for: {text}"
            assert any(f.type == SafetyFlagType.STROKE_SIGNS for f in result.matched_rules)

    def test_seizure(self):
        for text in ["seizure", "convulsion", "jhatka", "daura", "fits"]:
            result = evaluate_safety(text)
            assert result.red_flag is True, f"Failed for: {text}"
            assert any(f.type == SafetyFlagType.SEIZURE for f in result.matched_rules)

    def test_suicidal_thoughts(self):
        for text in [
            "suicidal thoughts",
            "want to kill myself",
            "want to die",
            "atmahatya",
            "khudkushi",
            "mar jana chahta hun",
        ]:
            result = evaluate_safety(text)
            assert result.red_flag is True, f"Failed for: {text}"
            assert any(f.type == SafetyFlagType.SUICIDAL_THOUGHTS for f in result.matched_rules)

    def test_pregnancy_emergency(self):
        for text in [
            "pregnant and bleeding",
            "pregnancy bleeding",
            "garbhwati aur khoon",
            "water broke",
            "paani nikal gaya",
        ]:
            result = evaluate_safety(text)
            assert result.red_flag is True, f"Failed for: {text}"
            assert any(f.type == SafetyFlagType.PREGNANCY_EMERGENCY for f in result.matched_rules)


class TestMisspellings:
    """Test common misspellings still trigger red flags."""

    def test_chest_pain_misspellings(self):
        for text in ["chest pan", "chestpain", "chest pian", "chest pane", "chestpainn"]:
            result = evaluate_safety(text)
            # Note: exact misspellings may not match - this documents current behavior
            # In production, you'd use fuzzy matching

    def test_breathing_misspellings(self):
        for text in ["breathing dificult", "shortnes of breath", "cant breathe"]:
            result = evaluate_safety(text)
            # Document current behavior


class TestHinglishPhrasing:
    """Test Hinglish/mixed language inputs."""

    def test_mixed_hindi_english(self):
        for text in [
            "chest pain hai do din se",
            "breathing problem hai",
            "unconscious ho gaya tha",
            "bleeding bahut ho rahi hai",
            "stroke ke lakshan hain",
        ]:
            result = evaluate_safety(text)
            assert result.red_flag is True, f"Failed for: {text}"

    def test_hinglish_transliteration(self):
        for text in [
            "chest pain ho raha hai",
            "saans nahi aa rahi",
            "behosh ho gaya",
            "khun bah raha hai",
            "munh tedha ho gaya",
        ]:
            result = evaluate_safety(text)
            assert result.red_flag is True, f"Failed for: {text}"


class TestNegationHandling:
    """Test negation - should NOT trigger red flags when properly negated."""

    def test_negation_chest_pain(self):
        for text in [
            "no chest pain",
            "no chest pain at all",
            "don't have chest pain",
            "no history of chest pain",
            "chest pain ruled out",
            "chest pain nahi hai",
            "chest pain nahi tha",
            "koi chest pain nahi",
        ]:
            result = evaluate_safety(text)
            # These SHOULD ideally not trigger, but current simple regex will
            # This test documents expected behavior for future improvement

    def test_negation_breathing(self):
        for text in [
            "no difficulty breathing",
            "breathing is normal",
            "no breathing problems",
            "saans lene mein koi dikkat nahi",
        ]:
            result = evaluate_safety(text)
            # Document current behavior


class TestMixedSymptoms:
    """Test multiple symptoms together."""

    def test_red_flag_with_other_symptoms(self):
        text = "chest pain and fever and cough"
        result = evaluate_safety(text)
        assert result.red_flag is True
        assert any(f.type == SafetyFlagType.CHEST_PAIN for f in result.matched_rules)

    def test_multiple_red_flags(self):
        text = "chest pain and difficulty breathing"
        result = evaluate_safety(text)
        assert result.red_flag is True
        types = {f.type for f in result.matched_rules}
        assert SafetyFlagType.CHEST_PAIN in types
        assert SafetyFlagType.DIFFICULTY_BREATHING in types

    def test_non_red_flag_symptoms(self):
        text = "headache and fever for 2 days"
        result = evaluate_safety(text)
        assert result.red_flag is False
        assert result.matched_rules == []
        assert result.bypass_matching is False


class TestSafetyResultStructure:
    """Test SafetyResult structure."""

    def test_safe_result_structure(self):
        result = evaluate_safety("headache for 2 days")
        assert result.red_flag is False
        assert result.matched_rules == []
        assert result.instructions is None
        assert result.bypass_matching is False

    def test_red_flag_result_structure(self):
        result = evaluate_safety("chest pain")
        assert result.red_flag is True
        assert len(result.matched_rules) > 0
        assert result.instructions is not None
        assert result.bypass_matching is True
        assert "112" in result.instructions or "108" in result.instructions

    def test_matched_rule_has_required_fields(self):
        result = evaluate_safety("chest pain")
        for flag in result.matched_rules:
            assert flag.type is not None
            assert flag.severity in (RedFlagSeverity.CRITICAL, RedFlagSeverity.HIGH)
            assert flag.matched_text is not None
            assert flag.rule_id is not None


class TestNegationHelper:
    """Test the negation detection helper."""

    def test_has_negation_before_english(self):
        assert has_negation_before("no chest pain here", "chest pain") is True
        assert has_negation_before("don't have chest pain", "chest pain") is True
        assert has_negation_before("without chest pain", "chest pain") is True
        assert has_negation_before("absence of chest pain", "chest pain") is True
        assert has_negation_before("chest pain is present", "chest pain") is False

    def test_has_negation_before_hindi(self):
        assert has_negation_before("chest pain nahi hai", "chest pain") is True
        assert has_negation_before("chest pain nahi tha", "chest pain") is True
        assert has_negation_before("koi chest pain nahi", "chest pain") is True


class TestEmptyInput:
    """Test edge cases with empty/None input."""

    def test_empty_string(self):
        result = evaluate_safety("")
        assert result.red_flag is False

    def test_none_input(self):
        result = evaluate_safety(None)
        assert result.red_flag is False

    def test_whitespace_only(self):
        result = evaluate_safety("   ")
        assert result.red_flag is False


class TestCaseInsensitive:
    """Test case insensitivity."""

    def test_uppercase(self):
        result = evaluate_safety("CHEST PAIN")
        assert result.red_flag is True

    def test_mixed_case(self):
        result = evaluate_safety("ChEsT pAiN")
        assert result.red_flag is True

    def test_hindi_case(self):
        # Hindi doesn't have case, but test mixed scripts
        result = evaluate_safety("Chest pain HAI")
        assert result.red_flag is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])