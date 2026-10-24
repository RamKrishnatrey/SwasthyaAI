# SwasthyaAI Conversation Database Models
# Chat history, AI interactions, symptom assessments

from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Boolean, JSON, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from app.db import Base
import enum


class ConversationType(str, enum.Enum):
    SYMPTOM_ASSESSMENT = "symptom_assessment"
    GENERAL_CHAT = "general_chat"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"
    MEDICAL_REPORT_ANALYSIS = "medical_report_analysis"
    APPOINTMENT_BOOKING = "appointment_booking"
    MEDICATION_REMINDER = "medication_reminder"
    HEALTH_EDUCATION = "health_education"


class ConversationStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    ESCALATED = "escalated"


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationModel(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patient_profiles.id"), nullable=False, index=True)
    type = Column(SQLEnum(ConversationType), default=ConversationType.GENERAL_CHAT, nullable=False)
    status = Column(SQLEnum(ConversationStatus), default=ConversationStatus.ACTIVE, nullable=False)
    language = Column(String, default="en", nullable=False)
    title = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Flexible metadata
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    patient = relationship("PatientProfileModel", back_populates="conversations")
    messages = relationship("MessageModel", back_populates="conversation", order_by="MessageModel.created_at")

    __table_args__ = (
        Index("ix_conversations_patient_status", "patient_id", "status"),
        Index("ix_conversations_patient_type", "patient_id", "type"),
    )


class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(SQLEnum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String, default="text", nullable=False)  # text, audio, image, file
    metadata = Column(JSON, nullable=True)  # For model info, citations, follow-up data, etc.
    tokens_used = Column(Integer, nullable=True)
    model_name = Column(String, nullable=True)
    model_version = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    conversation = relationship("ConversationModel", back_populates="messages")

    __table_args__ = (
        Index("ix_messages_conversation_created", "conversation_id", "created_at"),
    )


class SymptomAssessmentModel(Base):
    __tablename__ = "symptom_assessments"

    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False, index=True)
    patient_id = Column(String, ForeignKey("patient_profiles.id"), nullable=False, index=True)
    session_id = Column(String, nullable=False, index=True)

    # Intake data
    original_text = Column(Text, nullable=False)
    extracted_who = Column(String, nullable=True)
    extracted_symptoms = Column(JSON, nullable=True)  # Array of symptom strings
    extracted_duration = Column(String, nullable=True)
    extracted_age_group = Column(String, nullable=True)
    detected_language = Column(String, nullable=False)

    # Follow-up data
    follow_up_answers = Column(JSON, nullable=True)  # Q&A pairs

    # Triage results
    safety_red_flag = Column(Boolean, default=False, nullable=False)
    safety_flags = Column(JSON, nullable=True)  # Array of safety flag objects
    safety_instructions = Column(Text, nullable=True)
    bypass_matching = Column(Boolean, default=False, nullable=False)

    care_type = Column(String, nullable=True)
    urgency = Column(String, nullable=True)
    triage_reason = Column(Text, nullable=True)
    triage_confidence = Column(Float, nullable=True)
    model_source = Column(String, default="mock", nullable=False)
    suggested_specialty = Column(String, nullable=True)

    # Matching results
    matched_caregivers = Column(JSON, nullable=True)  # Array of matched caregiver objects
    selected_caregiver_id = Column(String, nullable=True)

    # Status
    is_complete = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_assessments_patient_created", "patient_id", "created_at"),
        Index("ix_assessments_session", "session_id"),
    )


from sqlalchemy import Float