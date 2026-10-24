# SwasthyaAI Appointment and Medical Record Database Models

from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Boolean, JSON, Enum as SQLEnum, Index, Float
from sqlalchemy.orm import relationship
from app.db import Base
import enum


class AppointmentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class AppointmentType(str, enum.Enum):
    IN_PERSON = "in_person"
    TELECONSULT = "teleconsult"
    HOME_VISIT = "home_visit"
    EMERGENCY = "emergency"


class AppointmentModel(Base):
    __tablename__ = "appointments"

    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patient_profiles.id"), nullable=False, index=True)
    clinician_id = Column(String, ForeignKey("clinician_profiles.id"), nullable=False, index=True)
    status = Column(SQLEnum(AppointmentStatus), default=AppointmentStatus.PENDING, nullable=False)
    type = Column(SQLEnum(AppointmentType), default=AppointmentType.IN_PERSON, nullable=False)

    # Scheduling
    scheduled_at = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, default=30, nullable=False)
    timezone = Column(String, default="Asia/Kolkata", nullable=False)

    # Location (for in-person/home visit)
    address = Column(Text, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Teleconsult details
    meeting_link = Column(String, nullable=True)
    meeting_id = Column(String, nullable=True)
    meeting_password = Column(String, nullable=True)

    # Chief complaint and notes
    chief_complaint = Column(Text, nullable=True)
    symptoms = Column(JSON, nullable=True)  # Array of symptom strings
    patient_notes = Column(Text, nullable=True)
    clinician_notes = Column(Text, nullable=True)

    # Prescription and follow-up
    prescription = Column(Text, nullable=True)  # JSON
    follow_up_required = Column(Boolean, default=False, nullable=False)
    follow_up_date = Column(DateTime, nullable=True)
    follow_up_notes = Column(Text, nullable=True)

    # Cancellation
    cancelled_at = Column(DateTime, nullable=True)
    cancelled_by = Column(String, nullable=True)  # patient, clinician, system
    cancellation_reason = Column(Text, nullable=True)

    # Reminders
    reminder_sent_24h = Column(Boolean, default=False, nullable=False)
    reminder_sent_2h = Column(Boolean, default=False, nullable=False)
    reminder_sent_30m = Column(Boolean, default=False, nullable=False)

    # Metadata
    source = Column(String, default="app", nullable=False)  # app, web, phone, walk_in
    metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    patient = relationship("PatientProfileModel", back_populates="appointments")
    clinician = relationship("ClinicianProfileModel", back_populates="appointments")

    __table_args__ = (
        Index("ix_appointments_patient_status", "patient_id", "status"),
        Index("ix_appointments_clinician_status", "clinician_id", "status"),
        Index("ix_appointments_scheduled", "scheduled_at"),
        Index("ix_appointments_patient_scheduled", "patient_id", "scheduled_at"),
    )


class MedicalRecordType(str, enum.Enum):
    PRESCRIPTION = "prescription"
    LAB_REPORT = "lab_report"
    IMAGING = "imaging"
    DISCHARGE_SUMMARY = "discharge_summary"
    VACCINATION = "vaccination"
    ALLERGY = "allergy"
    CHRONIC_CONDITION = "chronic_condition"
    SURGERY = "surgery"
    CONSULTATION_NOTE = "consultation_note"
    REFERRAL = "referral"
    INSURANCE_CLAIM = "insurance_claim"
    OTHER = "other"


class MedicalRecordModel(Base):
    __tablename__ = "medical_records"

    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patient_profiles.id"), nullable=False, index=True)
    appointment_id = Column(String, ForeignKey("appointments.id"), nullable=True, index=True)
    clinician_id = Column(String, ForeignKey("clinician_profiles.id"), nullable=True, index=True)

    type = Column(SQLEnum(MedicalRecordType), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # File storage
    file_path = Column(String, nullable=True)  # Path to stored file
    file_name = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    file_type = Column(String, nullable=True)  # MIME type
    file_hash = Column(String, nullable=True)  # SHA256 for integrity

    # Structured data
    structured_data = Column(JSON, nullable=True)  # Parsed/extracted data
    extracted_text = Column(Text, nullable=True)  # OCR/extracted text

    # Analysis
    ai_analysis = Column(Text, nullable=True)  # AI analysis results
    ai_model = Column(String, nullable=True)
    ai_confidence = Column(Float, nullable=True)
    ai_processed_at = Column(DateTime, nullable=True)

    # Dates
    record_date = Column(DateTime, nullable=False, index=True)  # When the record was created/issued
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)

    # Tags and categorization
    tags = Column(JSON, nullable=True)  # Array of tags
    body_system = Column(String, nullable=True)  # cardiovascular, respiratory, etc.
    icd_codes = Column(JSON, nullable=True)  # ICD-10 codes

    # Privacy and sharing
    is_sensitive = Column(Boolean, default=False, nullable=False)
    share_with_clinicians = Column(Boolean, default=True, nullable=False)
    share_with_family = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    patient = relationship("PatientProfileModel", back_populates="medical_records")

    __table_args__ = (
        Index("ix_medical_records_patient_type", "patient_id", "type"),
        Index("ix_medical_records_patient_date", "patient_id", "record_date"),
        Index("ix_medical_records_appointment", "appointment_id"),
    )


class ReminderType(str, enum.Enum):
    MEDICATION = "medication"
    APPOINTMENT = "appointment"
    FOLLOW_UP = "follow_up"
    VACCINATION = "vaccination"
    CHECKUP = "checkup"
    LAB_TEST = "lab_test"
    PRESCRIPTION_REFILL = "prescription_refill"
    HEALTH_GOAL = "health_goal"
    CUSTOM = "custom"


class ReminderFrequency(str, enum.Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class ReminderModel(Base):
    __tablename__ = "reminders"

    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patient_profiles.id"), nullable=False, index=True)
    appointment_id = Column(String, ForeignKey("appointments.id"), nullable=True, index=True)
    medical_record_id = Column(String, ForeignKey("medical_records.id"), nullable=True, index=True)

    type = Column(SQLEnum(ReminderType), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Scheduling
    frequency = Column(SQLEnum(ReminderFrequency), default=ReminderFrequency.ONCE, nullable=False)
    scheduled_at = Column(DateTime, nullable=False, index=True)
    end_date = Column(DateTime, nullable=True)
    timezone = Column(String, default="Asia/Kolkata", nullable=False)

    # For recurring reminders
    days_of_week = Column(JSON, nullable=True)  # Array of 0-6 (Mon-Sun)
    day_of_month = Column(Integer, nullable=True)
    time_of_day = Column(String, nullable=True)  # HH:MM format

    # Medication specific
    medication_name = Column(String, nullable=True)
    dosage = Column(String, nullable=True)
    instructions = Column(Text, nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    snoozed_until = Column(DateTime, nullable=True)
    skipped_count = Column(Integer, default=0, nullable=False)

    # Notifications
    notify_via_push = Column(Boolean, default=True, nullable=False)
    notify_via_sms = Column(Boolean, default=False, nullable=False)
    notify_via_email = Column(Boolean, default=False, nullable=False)
    last_notified_at = Column(DateTime, nullable=True)
    next_notification_at = Column(DateTime, nullable=True, index=True)

    # Metadata
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    patient = relationship("PatientProfileModel", back_populates="reminders")

    __table_args__ = (
        Index("ix_reminders_patient_active", "patient_id", "is_active"),
        Index("ix_reminders_next_notification", "next_notification_at"),
        Index("ix_reminders_patient_scheduled", "patient_id", "scheduled_at"),
    )