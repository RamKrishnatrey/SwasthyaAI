from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CareType(StrEnum):
    HOME_NURSING = "home_nursing"
    PARAMEDIC_HOME_VISIT = "paramedic_home_visit"
    LAB_TEST_HOME = "lab_test_home"
    TELECONSULTATION = "teleconsultation"
    EMERGENCY_112 = "emergency_112"


class Language(StrEnum):
    AUTO = "auto"
    ENGLISH = "English"
    HINDI = "Hindi"
    HINGLISH = "Hinglish"


class Location(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)


class AgentInput(BaseModel):
    session_id: str = Field(min_length=1, max_length=128)
    user_message: str = Field(min_length=1, max_length=2000)
    language: str = "auto"
    location: Location | None = None
    external_ai_consent: bool = False
    task: str = "care_triage"


class Caregiver(BaseModel):
    model_config = ConfigDict(extra="ignore")

    caregiver_id: str
    qualification: str = ""
    skills: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    base_lat: float | None = None
    base_lng: float | None = None
    max_radius_km: float = 0
    rating: float = Field(default=0, ge=0, le=5)
    active: bool = True
    available: bool = True


class CaregiverMatch(BaseModel):
    caregiver: Caregiver
    score: float = Field(ge=0, le=1)
    reference_score: float = Field(ge=0, le=1)
    distance_km: float | None = None
    factors: dict[str, float]
    reasons: list[str]


class ModelResult(BaseModel):
    name: str
    version: str
    task: str
    status: Literal["used", "unavailable", "failed"] = "used"
    care_type: CareType | None = None
    urgency: Literal["emergency", "same_day", "scheduled"] | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    safety_flags: list[str] = Field(default_factory=list)
    feature_summary: list[str] = Field(default_factory=list)


class AggregatedTriage(BaseModel):
    status: Literal["agreed", "single_model", "disagreement", "fallback"]
    care_type: CareType | None = None
    urgency: Literal["emergency", "same_day", "scheduled"] | None = None
    confidence: float | None = None
    safety_flags: list[str] = Field(default_factory=list)
    needs_human_review: bool = True


class AgentResponse(BaseModel):
    session_id: str
    status: Literal["needs_follow_up", "decision", "emergency", "unavailable"]
    response: str
    follow_up_question: str | None = None
    care_type: CareType | None = None
    urgency: Literal["emergency", "same_day", "scheduled"] | None = None
    safety_flags: list[str] = Field(default_factory=list)
    matched_caregivers: list[CaregiverMatch] = Field(default_factory=list)
    models: list[ModelResult] = Field(default_factory=list)
    aggregation_status: Literal["agreed", "single_model", "disagreement", "fallback"] = "fallback"
    needs_human_review: bool = True
    disclaimer: str = "This demo is not a medical diagnosis or emergency service."
