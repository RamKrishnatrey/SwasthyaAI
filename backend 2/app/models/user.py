# SwasthyaAI User Database Models
# Authentication and user management

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, Text, ForeignKey, Index, Integer
from sqlalchemy.orm import relationship
from app.db import Base
import enum


class UserRole(str, enum.Enum):
    PATIENT = "patient"
    CLINICIAN = "clinician"
    ADMIN = "admin"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, unique=True, nullable=True, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.PATIENT, nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING_VERIFICATION, nullable=False)
    language = Column(String, default="en", nullable=False)  # en, hi, hinglish
    email_verified = Column(Boolean, default=False, nullable=False)
    phone_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    patient_profile = relationship("PatientProfileModel", back_populates="user", uselist=False)
    clinician_profile = relationship("ClinicianProfileModel", back_populates="user", uselist=False)

    __table_args__ = (
        Index("ix_users_email_status", "email", "status"),
        Index("ix_users_phone_status", "phone", "status"),
    )


class PatientProfileModel(Base):
    __tablename__ = "patient_profiles"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String, nullable=True)  # male, female, other
    blood_group = Column(String, nullable=True)
    height_cm = Column(Integer, nullable=True)
    weight_kg = Column(Integer, nullable=True)
    emergency_contact_name = Column(String, nullable=True)
    emergency_contact_phone = Column(String, nullable=True)
    emergency_contact_relation = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    allergies = Column(Text, nullable=True)  # JSON array as text
    chronic_conditions = Column(Text, nullable=True)  # JSON array as text
    current_medications = Column(Text, nullable=True)  # JSON array as text
    family_history = Column(Text, nullable=True)
    insurance_provider = Column(String, nullable=True)
    insurance_policy_number = Column(String, nullable=True)
    preferred_language = Column(String, default="en", nullable=False)
    notification_preferences = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("UserModel", back_populates="patient_profile")
    conversations = relationship("ConversationModel", back_populates="patient")
    appointments = relationship("AppointmentModel", back_populates="patient")
    medical_records = relationship("MedicalRecordModel", back_populates="patient")
    reminders = relationship("ReminderModel", back_populates="patient")


class ClinicianProfileModel(Base):
    __tablename__ = "clinician_profiles"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    license_number = Column(String, nullable=False, index=True)
    license_state = Column(String, nullable=True)
    specialization = Column(String, nullable=False)
    qualifications = Column(Text, nullable=True)  # JSON array
    experience_years = Column(Integer, nullable=True)
    clinic_name = Column(String, nullable=True)
    clinic_address = Column(Text, nullable=True)
    clinic_city = Column(String, nullable=True)
    clinic_state = Column(String, nullable=True)
    clinic_pincode = Column(String, nullable=True)
    clinic_latitude = Column(Float, nullable=True)
    clinic_longitude = Column(Float, nullable=True)
    consultation_fee = Column(Integer, nullable=True)
    available_for_teleconsult = Column(Boolean, default=True, nullable=False)
    available_for_home_visit = Column(Boolean, default=False, nullable=False)
    verification_status = Column(String, default="pending", nullable=False)  # pending, verified, rejected
    verification_documents = Column(Text, nullable=True)  # JSON array
    rating = Column(Float, default=0.0, nullable=False)
    total_reviews = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("UserModel", back_populates="clinician_profile")
    appointments = relationship("AppointmentModel", back_populates="clinician")


from sqlalchemy import Integer, Float