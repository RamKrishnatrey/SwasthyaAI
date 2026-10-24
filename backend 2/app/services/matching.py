# SwasthyaAI Matching Service
# Weighted ranking: S = 0.35*K + 0.25*D + 0.20*A + 0.10*L + 0.10*R
# K=skill fit, D=distance, A=availability, L=language, R=rating

from typing import Optional
from math import radians, sin, cos, sqrt, atan2
from app.schemas import (
    MatchRequest, MatchResponse, MatchedCaregiver, Caregiver,
    ScoreBreakdown, MatchExplanation, CareType, Urgency, Language
)
from app.db import SessionLocal
from app.models.caregiver import CaregiverModel
from app.config import get_settings


# ===== Ranking Weights =====
WEIGHTS = {
    "skill_fit": 0.35,
    "distance": 0.25,
    "availability": 0.20,
    "language": 0.10,
    "rating": 0.10,
}


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance in km between two lat/lng points."""
    R = 6371  # Earth radius in km
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c


def calculate_skill_fit(caregiver: CaregiverModel, care_type: CareType, urgency: Urgency) -> float:
    """Calculate skill fit score (0-1) based on caregiver skills and care type/urgency."""
    skills = set(caregiver.skills or [])

    # Define required skills for each care type/urgency
    required_skills = {
        CareType.EMERGENCY: {"emergency_care", "cpr", "trauma", "first_aid"},
        CareType.URGENT_CARE: {"urgent_care", "wound_care", "iv_therapy", "assessment"},
        CareType.PRIMARY_CARE: {"primary_care", "general_assessment", "vitals"},
        CareType.TELECONSULT: {"teleconsultation", "remote_assessment"},
        CareType.SELF_CARE: {"health_education", "self_care_guidance"},
    }

    required = required_skills.get(care_type, set())
    if not required:
        return 0.5  # Neutral if no specific skills defined

    matches = len(skills & required)
    return min(matches / len(required), 1.0)


def calculate_distance_score(distance_km: float) -> float:
    """Calculate distance score (0-1). Closer = higher score.
    0km = 1.0, 50km = 0.5, 100km+ = 0.0"""
    if distance_km <= 0:
        return 1.0
    elif distance_km <= 10:
        return 0.9
    elif distance_km <= 25:
        return 0.7
    elif distance_km <= 50:
        return 0.5
    elif distance_km <= 75:
        return 0.3
    elif distance_km <= 100:
        return 0.1
    else:
        return 0.0


def calculate_availability_score(caregiver: CaregiverModel, urgency: Urgency) -> float:
    """Calculate availability score (0-1) based on urgency and caregiver schedule."""
    # For now, simplified: check if caregiver has any availability
    # In production, check specific day/time against patient request
    avail = caregiver.availability or []

    if not avail:
        # No availability listed - score depends on urgency
        if urgency == Urgency.CRITICAL:
            return 0.1
        elif urgency == Urgency.HIGH:
            return 0.2
        elif urgency == Urgency.MODERATE:
            return 0.3
        else:  # LOW
            return 0.5

    # Has availability listed
    if urgency == Urgency.CRITICAL:
        # Need 24/7 or emergency availability
        has_24h = any(a.get("is_24h") for a in avail)
        has_emergency = any(a.get("emergency_available") for a in avail)
        if has_24h or has_emergency:
            return 1.0
        return 0.4
    elif urgency == Urgency.HIGH:
        return 0.8
    elif urgency == Urgency.MODERATE:
        return 0.9
    else:  # LOW
        return 0.95


def calculate_language_score(caregiver: CaregiverModel, language: Language) -> float:
    """Calculate language match score (0-1)."""
    caregiver_langs = set(caregiver.languages or [])

    if language in caregiver_langs:
        return 1.0

    # Partial match for Hinglish/Hindi
    if language == Language.HINGLISH:
        if Language.HI in caregiver_langs:
            return 0.8
    if language == Language.HI:
        if Language.HINGLISH in caregiver_langs:
            return 0.8

    # English as fallback
    if Language.EN in caregiver_langs:
        return 0.6

    return 0.2


def calculate_rating_score(rating: float) -> float:
    """Normalize rating (0-5) to 0-1 scale."""
    return max(0.0, min(rating / 5.0, 1.0))


def calculate_total_score(
    skill_fit: float,
    distance: float,
    availability: float,
    language: float,
    rating: float
) -> float:
    """Calculate weighted total score."""
    return (
        WEIGHTS["skill_fit"] * skill_fit +
        WEIGHTS["distance"] * distance +
        WEIGHTS["availability"] * availability +
        WEIGHTS["language"] * language +
        WEIGHTS["rating"] * rating
    )


def generate_explanation(
    caregiver: CaregiverModel,
    score: ScoreBreakdown,
    care_type: CareType,
    urgency: Urgency,
    language: Language,
    patient_lat: float,
    patient_lng: float
) -> MatchExplanation:
    """Generate human-readable explanation for the match."""
    reasons = []

    # Skill fit
    if score.skill_fit >= 0.8:
        reasons.append(f"Strong skill match for {care_type.value}")
    elif score.skill_fit >= 0.5:
        reasons.append(f"Good skill match for {care_type.value}")
    else:
        reasons.append(f"Basic skills for {care_type.value}")

    # Distance
    distance_km = haversine_distance(patient_lat, patient_lng, caregiver.lat, caregiver.lng)
    if distance_km <= 10:
        reasons.append(f"Very close ({distance_km:.1f} km away)")
    elif distance_km <= 25:
        reasons.append(f"Nearby ({distance_km:.1f} km away)")
    elif distance_km <= 50:
        reasons.append(f"Within reach ({distance_km:.1f} km away)")
    else:
        reasons.append(f"Far ({distance_km:.1f} km away)")

    # Availability
    if score.availability >= 0.8:
        reasons.append("Available for urgent needs")
    elif score.availability >= 0.5:
        reasons.append("Generally available")
    else:
        reasons.append("Limited availability")

    # Language
    if score.language >= 0.8:
        reasons.append(f"Speaks {language.value}")
    elif score.language >= 0.5:
        reasons.append(f"Can communicate in {language.value}")
    else:
        reasons.append("Language barrier possible")

    # Rating
    if score.rating >= 0.8:
        reasons.append(f"Highly rated ({caregiver.rating:.1f}/5)")
    elif score.rating >= 0.6:
        reasons.append(f"Good rating ({caregiver.rating:.1f}/5)")
    else:
        reasons.append(f"Average rating ({caregiver.rating:.1f}/5)")

    return MatchExplanation(
        caregiver_id=caregiver.id,
        caregiver_name=caregiver.name,
        score=score,
        why=". ".join(reasons) + ".",
        passed_filters=True,
    )


def match_caregivers(request: MatchRequest) -> MatchResponse:
    """
    Main matching function.
    Filters caregivers by care type/urgency, scores them, returns top matches with explanations.
    """
    db = SessionLocal()
    try:
        # Get all caregivers
        caregivers = db.query(CaregiverModel).all()

        if not caregivers:
            return MatchResponse(
                session_id=request.session_id,
                matches=[],
                fallback="No caregivers available in the system",
                unmet_demand_logged=True,
            )

        # Score all caregivers
        scored_caregivers = []
        for cg in caregivers:
            distance_km = haversine_distance(
                request.patient_lat, request.patient_lng, cg.lat, cg.lng
            )

            skill_fit = calculate_skill_fit(cg, request.care_type, request.urgency)
            distance = calculate_distance_score(distance_km)
            availability = calculate_availability_score(cg, request.urgency)
            language = calculate_language_score(cg, request.language)
            rating = calculate_rating_score(cg.rating)
            total = calculate_total_score(skill_fit, distance, availability, language, rating)

            score = ScoreBreakdown(
                skill_fit=skill_fit,
                distance=distance,
                availability=availability,
                language=language,
                rating=rating,
                total=total,
            )

            explanation = generate_explanation(
                cg, score, request.care_type, request.urgency,
                request.language, request.patient_lat, request.patient_lng
            )

            # Convert to Caregiver schema
            caregiver_schema = Caregiver(
                id=cg.id,
                name=cg.name,
                qualification_verified=cg.qualification_verified,
                skills=cg.skills or [],
                service_areas=cg.service_areas or [],
                languages=cg.languages or [],
                rating=cg.rating,
                availability=cg.availability or [],
                lat=cg.lat,
                lng=cg.lng,
            )

            scored_caregivers.append((
                total,
                MatchedCaregiver(
                    caregiver=caregiver_schema,
                    score=score,
                    explanation=explanation,
                )
            ))

        # Sort by total score descending
        scored_caregivers.sort(key=lambda x: x[0], reverse=True)

        # Take top 5 matches
        matches = [mc for _, mc in scored_caregivers[:5]]

        # Filter: only return matches with total score > 0.3
        matches = [m for m in matches if m.score.total > 0.3]

        if not matches:
            return MatchResponse(
                session_id=request.session_id,
                matches=[],
                fallback="No suitable caregivers found for your needs. Try expanding search area or contact 112/108 for emergencies.",
                unmet_demand_logged=True,
            )

        return MatchResponse(
            session_id=request.session_id,
            matches=matches,
            unmet_demand_logged=False,
        )

    finally:
        db.close()


# Export for testing
__all__ = [
    "match_caregivers",
    "calculate_skill_fit",
    "calculate_distance_score",
    "calculate_availability_score",
    "calculate_language_score",
    "calculate_rating_score",
    "calculate_total_score",
    "generate_explanation",
    "haversine_distance",
    "WEIGHTS",
]