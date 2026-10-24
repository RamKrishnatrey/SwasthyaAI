import pytest

from backend.swasthyaai.agent.contracts import CareType, Caregiver, Language, Location
from backend.swasthyaai.agent.matcher import rank_caregivers


def caregiver(**changes):
    values = {
        "caregiver_id": "CG_001",
        "qualification": "GNM",
        "skills": ["injection_im"],
        "languages": ["Hindi", "English"],
        "base_lat": 28.54,
        "base_lng": 77.27,
        "max_radius_km": 10,
        "rating": 4.5,
        "active": True,
        "available": True,
    }
    values.update(changes)
    return Caregiver(**values)


def test_excludes_ineligible_candidates_before_ranking():
    eligible = caregiver(caregiver_id="eligible")
    unqualified = caregiver(caregiver_id="unqualified", qualification="")
    unavailable = caregiver(caregiver_id="unavailable", available=False)
    outside_area = caregiver(caregiver_id="outside", base_lat=29.0, base_lng=77.27)

    matches = rank_caregivers(
        [eligible, unqualified, unavailable, outside_area],
        CareType.HOME_NURSING,
        Location(lat=28.54, lng=77.27),
        Language.HINDI,
    )

    assert [match.caregiver.caregiver_id for match in matches] == ["eligible"]
    assert matches[0].score == 0.99
    assert matches[0].factors["skill"] == 1.0
    assert matches[0].reasons


def test_teleconsultation_does_not_require_location():
    doctor = caregiver(caregiver_id="doctor", skills=["teleconsultation"])

    matches = rank_caregivers(
        [doctor], CareType.TELECONSULTATION, None, Language.HINDI
    )

    assert len(matches) == 1
    assert matches[0].factors["distance"] == 1.0


def test_returns_proposal_and_dataset_baseline_scores_separately():
    matches = rank_caregivers(
        [caregiver()], CareType.HOME_NURSING, Location(lat=28.54, lng=77.27), Language.HINDI
    )

    assert matches[0].score == 0.99
    assert matches[0].reference_score == pytest.approx(0.985)
