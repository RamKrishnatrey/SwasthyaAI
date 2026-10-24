# SwasthyaAI Appointments Router
# Appointment booking, management, and scheduling

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import Optional, List
import uuid

from app.db import get_db
from app.services.auth import get_current_active_user, get_current_patient, get_current_clinician, require_role
from app.models.user import UserModel, PatientProfileModel, ClinicianProfileModel, UserRole
from app.models.appointment import AppointmentModel, MedicalRecordModel, ReminderModel, AppointmentStatus, AppointmentType, MedicalRecordType, ReminderType, ReminderFrequency
from app.models.caregiver import CaregiverModel

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


# ===== Request/Response Schemas =====

class AppointmentCreate(BaseModel):
    clinician_id: str
    type: AppointmentType = AppointmentType.IN_PERSON
    scheduled_at: datetime
    duration_minutes: int = Field(default=30, ge=15, le=120)
    timezone: str = "Asia/Kolkata"
    chief_complaint: Optional[str] = None
    symptoms: Optional[List[str]] = None
    patient_notes: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class AppointmentUpdate(BaseModel):
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    chief_complaint: Optional[str] = None
    symptoms: Optional[List[str]] = None
    patient_notes: Optional[str] = None
    clinician_notes: Optional[str] = None
    status: Optional[AppointmentStatus] = None
    meeting_link: Optional[str] = None
    meeting_id: Optional[str] = None
    meeting_password: Optional[str] = None
    prescription: Optional[str] = None
    follow_up_required: Optional[bool] = None
    follow_up_date: Optional[datetime] = None
    follow_up_notes: Optional[str] = None
    cancellation_reason: Optional[str] = None


class AppointmentResponse(BaseModel):
    id: str
    patient_id: str
    clinician_id: str
    status: AppointmentStatus
    type: AppointmentType
    scheduled_at: datetime
    duration_minutes: int
    timezone: str
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    pincode: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    meeting_link: Optional[str]
    meeting_id: Optional[str]
    meeting_password: Optional[str]
    chief_complaint: Optional[str]
    symptoms: Optional[List[str]]
    patient_notes: Optional[str]
    clinician_notes: Optional[str]
    prescription: Optional[str]
    follow_up_required: bool
    follow_up_date: Optional[datetime]
    follow_up_notes: Optional[str]
    cancelled_at: Optional[datetime]
    cancelled_by: Optional[str]
    cancellation_reason: Optional[str]
    source: str
    metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AppointmentListResponse(BaseModel):
    appointments: List[AppointmentResponse]
    total: int
    page: int
    page_size: int


class AvailableSlot(BaseModel):
    clinician_id: str
    clinician_name: str
    start_time: datetime
    end_time: datetime
    type: AppointmentType
    is_available: bool


# ===== Patient Appointment Endpoints =====

@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    request: AppointmentCreate,
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Create a new appointment."""
    # Verify clinician exists
    clinician = db.query(ClinicianProfileModel).filter(ClinicianProfileModel.id == request.clinician_id).first()
    if not clinician:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinician not found"
        )

    # Check for conflicts
    existing = db.query(AppointmentModel).filter(
        AppointmentModel.clinician_id == request.clinician_id,
        AppointmentModel.scheduled_at == request.scheduled_at,
        AppointmentModel.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED, AppointmentStatus.IN_PROGRESS])
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Time slot not available"
        )

    appointment = AppointmentModel(
        id=str(uuid.uuid4()),
        patient_id=patient.id,
        clinician_id=request.clinician_id,
        status=AppointmentStatus.PENDING,
        type=request.type,
        scheduled_at=request.scheduled_at,
        duration_minutes=request.duration_minutes,
        timezone=request.timezone,
        chief_complaint=request.chief_complaint,
        symptoms=request.symptoms or [],
        patient_notes=request.patient_notes,
        address=request.address,
        city=request.city,
        state=request.state,
        pincode=request.pincode,
        latitude=request.latitude,
        longitude=request.longitude,
        source="app",
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.get("", response_model=AppointmentListResponse)
async def list_appointments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[AppointmentStatus] = None,
    type: Optional[AppointmentType] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """List appointments for the current patient."""
    query = db.query(AppointmentModel).filter(AppointmentModel.patient_id == patient.id)

    if status:
        query = query.filter(AppointmentModel.status == status)
    if type:
        query = query.filter(AppointmentModel.type == type)
    if from_date:
        query = query.filter(AppointmentModel.scheduled_at >= from_date)
    if to_date:
        query = query.filter(AppointmentModel.scheduled_at <= to_date)

    total = query.count()
    appointments = query.order_by(AppointmentModel.scheduled_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return AppointmentListResponse(
        appointments=appointments,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/upcoming", response_model=List[AppointmentResponse])
async def get_upcoming_appointments(
    limit: int = Query(5, ge=1, le=20),
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Get upcoming appointments for the current patient."""
    now = datetime.utcnow()
    appointments = db.query(AppointmentModel).filter(
        AppointmentModel.patient_id == patient.id,
        AppointmentModel.scheduled_at >= now,
        AppointmentModel.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
    ).order_by(AppointmentModel.scheduled_at.asc()).limit(limit).all()

    return appointments


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: str,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific appointment."""
    appointment = db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    # Check authorization
    if current_user.role == UserRole.PATIENT:
        patient = db.query(PatientProfileModel).filter(PatientProfileModel.user_id == current_user.id).first()
        if not patient or appointment.patient_id != patient.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this appointment"
            )
    elif current_user.role == UserRole.CLINICIAN:
        clinician = db.query(ClinicianProfileModel).filter(ClinicianProfileModel.user_id == current_user.id).first()
        if not clinician or appointment.clinician_id != clinician.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this appointment"
            )

    return appointment


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: str,
    request: AppointmentUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an appointment."""
    appointment = db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    # Check authorization
    if current_user.role == UserRole.PATIENT:
        patient = db.query(PatientProfileModel).filter(PatientProfileModel.user_id == current_user.id).first()
        if not patient or appointment.patient_id != patient.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this appointment"
            )
        # Patients can only update certain fields
        allowed_fields = ['scheduled_at', 'duration_minutes', 'chief_complaint', 'symptoms', 'patient_notes', 'status']
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field in allowed_fields:
                setattr(appointment, field, value)

    elif current_user.role == UserRole.CLINICIAN:
        clinician = db.query(ClinicianProfileModel).filter(ClinicianProfileModel.user_id == current_user.id).first()
        if not clinician or appointment.clinician_id != clinician.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this appointment"
            )
        # Clinicians can update more fields
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(appointment, field, value)

    # Handle status transitions
    if request.status == AppointmentStatus.CANCELLED:
        appointment.cancelled_at = datetime.utcnow()
        appointment.cancelled_by = current_user.role.value
        if request.cancellation_reason:
            appointment.cancellation_reason = request.cancellation_reason

    appointment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(appointment)
    return appointment


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_appointment(
    appointment_id: str,
    reason: Optional[str] = None,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel an appointment."""
    appointment = db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    # Check authorization
    if current_user.role == UserRole.PATIENT:
        patient = db.query(PatientProfileModel).filter(PatientProfileModel.user_id == current_user.id).first()
        if not patient or appointment.patient_id != patient.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to cancel this appointment"
            )
    elif current_user.role == UserRole.CLINICIAN:
        clinician = db.query(ClinicianProfileModel).filter(ClinicianProfileModel.user_id == current_user.id).first()
        if not clinician or appointment.clinician_id != clinician.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to cancel this appointment"
            )

    appointment.status = AppointmentStatus.CANCELLED
    appointment.cancelled_at = datetime.utcnow()
    appointment.cancelled_by = current_user.role.value
    appointment.cancellation_reason = reason
    appointment.updated_at = datetime.utcnow()
    db.commit()


# ===== Clinician Appointment Endpoints =====

@router.get("/clinician/schedule", response_model=AppointmentListResponse)
async def get_clinician_schedule(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    date: Optional[datetime] = None,
    status: Optional[AppointmentStatus] = None,
    clinician: ClinicianProfileModel = Depends(get_current_clinician),
    db: Session = Depends(get_db)
):
    """Get clinician's appointment schedule."""
    query = db.query(AppointmentModel).filter(AppointmentModel.clinician_id == clinician.id)

    if date:
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        query = query.filter(
            AppointmentModel.scheduled_at >= start_of_day,
            AppointmentModel.scheduled_at < end_of_day
        )
    if status:
        query = query.filter(AppointmentModel.status == status)

    total = query.count()
    appointments = query.order_by(AppointmentModel.scheduled_at.asc()).offset((page - 1) * page_size).limit(page_size).all()

    return AppointmentListResponse(
        appointments=appointments,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/clinician/available-slots", response_model=List[AvailableSlot])
async def get_available_slots(
    clinician_id: str,
    date: datetime,
    db: Session = Depends(get_db)
):
    """Get available time slots for a clinician on a specific date."""
    clinician = db.query(ClinicianProfileModel).filter(ClinicianProfileModel.id == clinician_id).first()
    if not clinician:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinician not found"
        )

    # Get clinician's user for name
    user = db.query(UserModel).filter(UserModel.id == clinician.user_id).first()
    clinician_name = user.full_name if user else "Unknown"

    # Get booked slots for the day
    start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    booked = db.query(AppointmentModel).filter(
        AppointmentModel.clinician_id == clinician_id,
        AppointmentModel.scheduled_at >= start_of_day,
        AppointmentModel.scheduled_at < end_of_day,
        AppointmentModel.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED, AppointmentStatus.IN_PROGRESS])
    ).all()

    booked_times = {a.scheduled_at for a in booked}

    # Generate available slots (9 AM - 5 PM, 30 min intervals)
    slots = []
    current = start_of_day.replace(hour=9, minute=0)
    end = start_of_day.replace(hour=17, minute=0)

    while current < end:
        slot_end = current + timedelta(minutes=30)
        is_booked = current in booked_times
        slots.append(AvailableSlot(
            clinician_id=clinician_id,
            clinician_name=clinician_name,
            start_time=current,
            end_time=slot_end,
            type=AppointmentType.IN_PERSON,
            is_available=not is_booked
        ))
        current = slot_end

    return slots


# ===== Search/Discovery Endpoints =====

@router.get("/search/clinicians")
async def search_clinicians(
    specialty: Optional[str] = None,
    city: Optional[str] = None,
    type: Optional[AppointmentType] = None,
    available_for_teleconsult: Optional[bool] = None,
    language: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radius_km: float = 50,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search for clinicians."""
    query = db.query(ClinicianProfileModel).join(UserModel).filter(
        ClinicianProfileModel.verification_status == "verified"
    )

    if specialty:
        query = query.filter(ClinicianProfileModel.specialization.ilike(f"%{specialty}%"))
    if city:
        query = query.filter(ClinicianProfileModel.clinic_city.ilike(f"%{city}%"))
    if available_for_teleconsult:
        query = query.filter(ClinicianProfileModel.available_for_teleconsult == True)
    if type == AppointmentType.TELECONSULT:
        query = query.filter(ClinicianProfileModel.available_for_teleconsult == True)

    clinicians = query.limit(limit).all()

    # Filter by distance if lat/lng provided
    if lat is not None and lng is not None:
        from math import radians, sin, cos, sqrt, atan2
        def haversine(lat1, lng1, lat2, lng2):
            R = 6371
            lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
            dlat = lat2 - lat1
            dlng = lng2 - lng1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            return R * c

        filtered = []
        for c in clinicians:
            if c.clinic_latitude and c.clinic_longitude:
                dist = haversine(lat, lng, c.clinic_latitude, c.clinic_longitude)
                if dist <= radius_km:
                    filtered.append(c)
        clinicians = filtered

    return {
        "clinicians": [
            {
                "id": c.id,
                "name": c.user.full_name if c.user else "Unknown",
                "specialization": c.specialization,
                "qualifications": c.qualifications,
                "experience_years": c.experience_years,
                "clinic_name": c.clinic_name,
                "clinic_address": c.clinic_address,
                "clinic_city": c.clinic_city,
                "clinic_state": c.clinic_state,
                "consultation_fee": c.consultation_fee,
                "available_for_teleconsult": c.available_for_teleconsult,
                "available_for_home_visit": c.available_for_home_visit,
                "rating": c.rating,
                "total_reviews": c.total_reviews,
            }
            for c in clinicians
        ],
        "total": len(clinicians)
    }