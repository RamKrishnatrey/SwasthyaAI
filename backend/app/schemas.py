# SwasthyaAI API Schemas
# Single source of truth for all request/response models

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal, Annotated
from datetime import datetime
from enum import Enum


# ===== Enums =====
class Language(str, Enum):
    EN = "en"
    HI = "hi"
    HINGLISH = "hinglish"


class CareType(str, Enum):
    EMERGENCY = "emergency"
    URGENT_CARE = "urgent_care"
    PRIMARY_CARE = "primary_care"
    TELECONSULT = "teleconsult"
    SELF_CARE = "self_care"


class Urgency(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"


class ModelSource(str, Enum):
    MOCK = "mock"
    TRAINED = "trained"


class SafetyFlagType(str, Enum):
    CHEST_PAIN = "chest_pain"
    DIFFICULTY_BREATHING = "difficulty_breathing"
    UNCONSCIOUSNESS = "unconsciousness"
    SEVERE_BLEEDING = "severe_bleeding"
    STROKE_SIGNS = "stroke_signs"
    SEIZURE = "seizure"
    SUICIDAL_THOUGHTS = "suicidal_thoughts"
    PREGNANCY_EMERGENCY = "pregnancy_emergency"


class RedFlagSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ===== Health =====
class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str = "swasthyaai-backend"
    version: str = "0.1.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ===== Intake =====
class IntakeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="Free-text symptom description")
    session_id: Optional[str] = Field(None, description="Existing session ID if continuing")
    language_hint: Optional[Language] = Field(None, description="Optional language hint from UI")


class ExtractedFields(BaseModel):
    who: Optional[str] = Field(None, description="Who is the patient (self, mother, father, child, etc.)")
    symptoms: list[str] = Field(default_factory=list, description="List of symptoms mentioned")
    duration: Optional[str] = Field(None, description="Duration text (e.g., '2 days')")
    age_group: Optional[str] = Field(None, description="Age group if mentioned (infant, child, adult, elderly)")
    language: Language = Field(default=Language.EN, description="Detected language")


class FollowUpQuestion(BaseModel):
    id: str
    question: str
    field: str = Field(..., description="Which extracted field this question targets")
    required: bool = True


class EditableSummary(BaseModel):
    who: str = ""
    symptoms: list[str] = Field(default_factory=list)
    duration: str = ""
    age_group: str = ""
    language: Language = Language.EN
    original_text: str = ""


class IntakeResponse(BaseModel):
    session_id: str
    extracted: ExtractedFields
    follow_up_questions: list[FollowUpQuestion] = Field(default_factory=list)
    editable_summary: EditableSummary
    language: Language
    is_complete: bool = Field(False, description="True when no more follow-ups needed")


# ===== Safety =====
class SafetyFlag(BaseModel):
    type: SafetyFlagType
    severity: RedFlagSeverity
    matched_text: str
    rule_id: str


class SafetyResult(BaseModel):
    red_flag: bool
    matched_rules: list[SafetyFlag] = Field(default_factory=list)
    instructions: Optional[str] = Field(None, description="Emergency instructions if red_flag is True")
    bypass_matching: bool = Field(False, description="If True, matching/booking should be skipped")


# ===== Triage =====
class TriageRequest(BaseModel):
    session_id: str
    confirmed_summary: EditableSummary
    language: Language


class TriageResponse(BaseModel):
    session_id: str
    safety: SafetyResult
    care_type: Optional[CareType] = None
    urgency: Optional[Urgency] = None
    reason: Optional[str] = Field(None, description="Plain-language reason for triage decision")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    model_source: ModelSource = ModelSource.MOCK
    disclaimer: str = "This is decision support only, not a medical diagnosis or prescription. For emergencies, call 112/108 immediately."


# ===== Caregivers =====
class CaregiverAvailability(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    start_hour: int = Field(..., ge=0, le=23)
    end_hour: int = Field(..., ge=0, le=23)


class Caregiver(BaseModel):
    id: str
    name: str
    qualification_verified: bool
    skills: list[str] = Field(default_factory=list)
    service_areas: list[str] = Field(default_factory=list)
    languages: list[Language] = Field(default_factory=list)
    rating: float = Field(..., ge=0.0, le=5.0)
    availability: list[CaregiverAvailability] = Field(default_factory=list)
    lat: float
    lng: float


class CaregiversListResponse(BaseModel):
    caregivers: list[Caregiver]
    total: int


# ===== Matching =====
class ScoreBreakdown(BaseModel):
    skill_fit: float = Field(..., ge=0.0, le=1.0)
    distance: float = Field(..., ge=0.0, le=1.0)
    availability: float = Field(..., ge=0.0, le=1.0)
    language: float = Field(..., ge=0.0, le=1.0)
    rating: float = Field(..., ge=0.0, le=1.0)
    total: float = Field(..., ge=0.0, le=1.0)


class MatchExplanation(BaseModel):
    caregiver_id: str
    caregiver_name: str
    score: ScoreBreakdown
    why: str = Field(..., description="Human-readable explanation of the match")
    passed_filters: bool = True


class MatchRequest(BaseModel):
    session_id: str
    care_type: CareType
    urgency: Urgency
    patient_lat: float
    patient_lng: float
    language: Language


class MatchedCaregiver(BaseModel):
    caregiver: Caregiver
    score: ScoreBreakdown
    explanation: MatchExplanation


class MatchResponse(BaseModel):
    session_id: str
    matches: list[MatchedCaregiver] = Field(default_factory=list)
    fallback: Optional[str] = Field(None, description="Fallback message if no eligible caregivers")
    unmet_demand_logged: bool = False


# ===== Bookings =====
class BookingRequest(BaseModel):
    session_id: str
    caregiver_id: str
    patient_name: str
    patient_phone: str
    preferred_time: Optional[datetime] = None
    notes: Optional[str] = None


class Booking(BaseModel):
    id: str
    session_id: str
    caregiver_id: str
    patient_name: str
    patient_phone: str
    status: BookingStatus
    created_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = None
    notes: Optional[str] = None


class BookingResponse(BaseModel):
    booking: Optional[Booking] = None
    status: BookingStatus
    message: str = Field(..., description="Human-readable status message")


# ===== Analytics (stretch) =====
class DemandStats(BaseModel):
    total_requests: int
    by_care_type: dict[str, int]
    by_urgency: dict[str, int]
    unmet_demand_count: int
    top_unmet_areas: list[dict[str, str]]


class AnalyticsResponse(BaseModel):
    demand: DemandStats
    generated_at: datetime = Field(default_factory=datetime.utcnow)