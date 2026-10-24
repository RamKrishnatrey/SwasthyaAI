# SwasthyaAI Matching Service Tests
# Weighted ranking: S = 0.35*K + 0.25*D + 0.20*A + 0.10*L + 0.10*R

import pytest
from app.services.matching import (
    haversine_distance,
    calculate_skill_fit,
    calculate_distance_score,
    calculate_availability_score,
    calculate_language_score,
    calculate_rating_score,
    calculate_total_score,
    WEIGHTS,
)
from app.schemas import Caregiver, CaregiverAvailability, CareType, Urgency, Language
from app.models.caregiver import CaregiverModel


class TestHaversineDistance:
    """Test distance calculation."""

    def test_same_point(self):
        dist = haversine_distance(28.6139, 77.2090, 28.6139, 77.2090)
        assert dist == 0.0

    def test_known_distance(self):
        # Delhi to Mumbai approx 1150 km
        dist = haversine_distance(28.6139, 77.2090, 19.0760, 72.8777)
        assert 1100 < dist < 1200

    def test_short_distance(self):
        # Two points in Delhi
        dist = haversine_distance(28.6139, 77.2090, 28.6500, 77.2500)
        assert 0 < dist < 10


class TestCalculateSkillFit:
    """Test skill fit calculation."""

    def test_emergency_skills_match(self):
        caregiver = CaregiverModel(
            id="c1", name="Dr. A", qualification_verified=True,
            skills=["emergency_care", "cpr", "trauma", "first_aid"],
            service_areas=["Delhi"], languages=[Language.EN], rating=4.5,
            availability=[], lat=28.6139, lng=77.2090
        )
        score = calculate_skill_fit(caregiver, CareType.EMERGENCY, Urgency.CRITICAL)
        assert score == 1.0

    def test_emergency_partial_skills(self):
        caregiver = CaregiverModel(
            id="c1", name="Dr. A", qualification_verified=True,
            skills=["emergency_care", "cpr"],  # Only 2 of 4
            service_areas=["Delhi"], languages=[Language.EN], rating=4.5,
            availability=[], lat=28.6139, lng=77.2090
        )
        score = calculate_skill_fit(caregiver, CareType.EMERGENCY, Urgency.CRITICAL)
        assert score == 0.5

    def test_primary_care_skills(self):
        caregiver = CaregiverModel(
            id="c1", name="Dr. A", qualification_verified=True,
            skills=["primary_care", "general_assessment", "vitals"],
            service_areas=["Delhi"], languages=[Language.EN], rating=4.5,
            availability=[], lat=28.6139, lng=77.2090
        )
        score = calculate_skill_fit(caregiver, CareType.PRIMARY_CARE, Urgency.MODERATE)
        assert score == 1.0

    def test_no_matching_skills(self):
        caregiver = CaregiverModel(
            id="c1", name="Dr. A", qualification_verified=True,
            skills=["dermatology"],  # Not relevant for emergency
            service_areas=["Delhi"], languages=[Language.EN], rating=4.5,
            availability=[], lat=28.6139, lng=77.2090
        )
        score = calculate_skill_fit(caregiver, CareType.EMERGENCY, Urgency.CRITICAL)
        assert score == 0.0


class TestCalculateDistanceScore:
    """Test distance score calculation."""

    def test_zero_distance(self):
        assert calculate_distance_score(0) == 1.0

    def test_close_distance(self):
        assert calculate_distance_score(5) == 0.9
        assert calculate_distance_score(10) == 0.9

    def test_medium_distance(self):
        assert calculate_distance_score(15) == 0.7
        assert calculate_distance_score(25) == 0.7

    def test_far_distance(self):
        assert calculate_distance_score(40) == 0.5
        assert calculate_distance_score(50) == 0.5

    def test_very_far(self):
        assert calculate_distance_score(60) == 0.3
        assert calculate_distance_score(80) == 0.1
        assert calculate_distance_score(150) == 0.0


class TestCalculateAvailabilityScore:
    """Test availability score calculation."""

    def test_no_availability(self):
        caregiver = CaregiverModel(
            id="c1", name="Dr. A", qualification_verified=True,
            skills=[], service_areas=[], languages=[], rating=4.5,
            availability=[], lat=28.6139, lng=77.2090
        )
        assert calculate_availability_score(caregiver, Urgency.CRITICAL) == 0.1
        assert calculate_availability_score(caregiver, Urgency.HIGH) == 0.2
        assert calculate_availability_score(caregiver, Urgency.MODERATE) == 0.3
        assert calculate_availability_score(caregiver, Urgency.LOW) == 0.5

    def test_has_availability(self):
        caregiver = CaregiverModel(
            id="c1", name="Dr. A", qualification_verified=True,
            skills=[], service_areas=[], languages=[], rating=4.5,
            availability=[{"day": 0, "start": 9, "end": 17}],
            lat=28.6139, lng=77.2090
        )
        assert calculate_availability_score(caregiver, Urgency.CRITICAL) == 0.4
        assert calculate_availability_score(caregiver, Urgency.HIGH) == 0.8
        assert calculate_availability_score(caregiver, Urgency.MODERATE) == 0.9

    def test_24h_availability(self):
        caregiver = CaregiverModel(
            id="c1", name="Dr. A", qualification_verified=True,
            skills=[], service_areas=[], languages=[], rating=4.5,
            availability=[{"is_24h": True}],
            lat=28.6139, lng=77.2090
        )
        assert calculate_availability_score(caregiver, Urgency.CRITICAL) == 1.0


class TestCalculateLanguageScore:
    """Test language match score."""

    def test_exact_match(self):
        caregiver = CaregiverModel(
            id="c1", name="Dr. A", qualification_verified=True,
            skills=[], service_areas=[], languages=[Language.EN], rating=4.5,
            availability=[], lat=28.6139, lng=77.2090
        )
        assert calculate_language_score(caregiver, Language.EN) == 1.0

    def test_hinglish_hindi_match(self):
        caregiver = CaregiverModel(
            id="c1", name="Dr. A", qualification_verified=True,
            skills=[], service_areas=[], languages=[Language.HI], rating=4.5,
            availability=[], lat=28.6139, lng=77.2090
        )
        assert calculate_language_score(caregiver, Language.HINGLISH) == 0.8

    def test_hindi_hinglish_match(self):
        caregiver = CaregiverModel(
            id="c1", name="Dr. A", qualification_verified=True,
            skills=[], service_areas=[], languages=[Language.HINGLISH], rating=4.5,
            availability=[], lat=28.6139, lng=77.2090
        )
        assert calculate_language_score(caregiver, Language.HI) == 0.8

    def test_english_fallback(self):
        caregiver = CaregiverModel(
            id="c1", name="Dr. A", qualification_verified=True,
            skills=[], service_areas=[], languages=[Language.EN], rating=4.5,
            availability=[], lat=28.6139, lng=77.2090
        )
        assert calculate_language_score(caregiver, Language.HI) == 0.6

    def test_no_match(self):
        caregiver = CaregiverModel(
            id="c1", name="Dr. A", qualification_verified=True,
            skills=[], service_areas=[], languages=[Language.HI], rating=4.5,
            availability=[], lat=28.6139, lng=77.2090
        )
        assert calculate_language_score(caregiver, Language.EN) == 0.2


class TestCalculateRatingScore:
    """Test rating normalization."""

    def test_perfect_rating(self):
        assert calculate_rating_score(5.0) == 1.0

    def test_good_rating(self):
        assert calculate_rating_score(4.0) == 0.8

    def test_average_rating(self):
        assert calculate_rating_score(3.0) == 0.6

    def test_low_rating(self):
        assert calculate_rating_score(1.0) == 0.2

    def test_zero_rating(self):
        assert calculate_rating_score(0.0) == 0.0


class TestCalculateTotalScore:
    """Test weighted total score."""

    def test_all_max(self):
        total = calculate_total_score(1.0, 1.0, 1.0, 1.0, 1.0)
        assert total == 1.0

    def test_all_min(self):
        total = calculate_total_score(0.0, 0.0, 0.0, 0.0, 0.0)
        assert total == 0.0

    def test_weights_sum(self):
        # Verify weights sum to 1.0
        assert abs(sum(WEIGHTS.values()) - 1.0) < 0.001

    def test_skill_heavy(self):
        # Skill fit has highest weight (0.35)
        total1 = calculate_total_score(1.0, 0.0, 0.0, 0.0, 0.0)
        total2 = calculate_total_score(0.0, 1.0, 0.0, 0.0, 0.0)
        assert total1 > total2  # Skill weight > distance weight


class TestWeights:
    """Test weight configuration."""

    def test_all_weights_present(self):
        expected = ["skill_fit", "distance", "availability", "language", "rating"]
        for key in expected:
            assert key in WEIGHTS

    def test_weight_values(self):
        assert WEIGHTS["skill_fit"] == 0.35
        assert WEIGHTS["distance"] == 0.25
        assert WEIGHTS["availability"] == 0.20
        assert WEIGHTS["language"] == 0.10
        assert WEIGHTS["rating"] == 0.10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])