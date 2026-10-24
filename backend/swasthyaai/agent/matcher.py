from math import asin, cos, radians, sin, sqrt

from backend.swasthyaai.agent.contracts import (
    CareType,
    Caregiver,
    CaregiverMatch,
    Language,
    Location,
)


_REQUIRED_SKILLS = {
    CareType.HOME_NURSING: "injection_im",
    CareType.PARAMEDIC_HOME_VISIT: "paramedic_home_visit",
    CareType.LAB_TEST_HOME: "lab_test_home",
    CareType.TELECONSULTATION: "teleconsultation",
}


def _distance_km(location: Location, caregiver: Caregiver) -> float | None:
    if caregiver.base_lat is None or caregiver.base_lng is None:
        return None
    lat1, lat2 = radians(location.lat), radians(caregiver.base_lat)
    delta_lat = lat2 - lat1
    delta_lng = radians(caregiver.base_lng - location.lng)
    a = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lng / 2) ** 2
    return 6371 * 2 * asin(sqrt(a))


def rank_caregivers(
    caregivers: list[Caregiver],
    care_type: CareType,
    location: Location | None,
    language: Language,
) -> list[CaregiverMatch]:
    ranked = []
    required_skill = _REQUIRED_SKILLS.get(care_type)
    for caregiver in caregivers:
        if not caregiver.active or not caregiver.available or not caregiver.qualification.strip():
            continue
        if required_skill and required_skill not in caregiver.skills:
            continue

        distance = _distance_km(location, caregiver) if location else None
        if location and care_type != CareType.TELECONSULTATION:
            if distance is None or distance > caregiver.max_radius_km:
                continue
        distance_factor = 1.0 if distance is None else max(0.0, 1 - distance / max(caregiver.max_radius_km, 1))
        skill_factor = 1.0 if required_skill in caregiver.skills else 0.0
        language_factor = 1.0 if language.value in caregiver.languages else 0.0
        availability_factor = 1.0
        rating_factor = caregiver.rating / 5
        factors = {
            "skill": skill_factor,
            "distance": distance_factor,
            "availability": availability_factor,
            "language": language_factor,
            "rating": rating_factor,
        }
        score = min(1.0, 0.35 * skill_factor + 0.25 * distance_factor + 0.20 * availability_factor + 0.10 * language_factor + 0.10 * rating_factor)
        reference_score = 0.35 * language_factor + 0.30 * distance_factor + 0.20 * skill_factor + 0.15 * rating_factor
        reasons = ["Available", caregiver.qualification]
        if distance is not None:
            reasons.append(f"Within {distance:.1f} km")
        if language_factor:
            reasons.append(f"Speaks {language.value}")
        ranked.append(CaregiverMatch(
            caregiver=caregiver,
            score=score,
            reference_score=reference_score,
            distance_km=distance,
            factors=factors,
            reasons=reasons,
        ))
    return sorted(ranked, key=lambda match: match.score, reverse=True)
