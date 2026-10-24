# SwasthyaAI Reminders Router
# Medication reminders, appointment reminders, health goal reminders

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime, time
from typing import Optional, List
import uuid

from app.db import get_db
from app.services.auth import get_current_active_user, get_current_patient, get_current_clinician
from app.models.user import UserModel, PatientProfileModel, ClinicianProfileModel, UserRole
from app.models.appointment import ReminderModel, ReminderType, ReminderFrequency, AppointmentModel, MedicalRecordModel

router = APIRouter(prefix="/api/reminders", tags=["reminders"])


# ===== Request/Response Schemas =====

class ReminderCreate(BaseModel):
    appointment_id: Optional[str] = None
    medical_record_id: Optional[str] = None
    type: ReminderType
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    frequency: ReminderFrequency = ReminderFrequency.ONCE
    scheduled_at: datetime
    end_date: Optional[datetime] = None
    timezone: str = "Asia/Kolkata"
    days_of_week: Optional[List[int]] = None  # 0=Mon, 6=Sun
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    time_of_day: Optional[str] = None  # HH:MM format
    medication_name: Optional[str] = None
    dosage: Optional[str] = None
    instructions: Optional[str] = None
    notify_via_push: bool = True
    notify_via_sms: bool = False
    notify_via_email: bool = False
    metadata: Optional[dict] = None


class ReminderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    frequency: Optional[ReminderFrequency] = None
    scheduled_at: Optional[datetime] = None
    end_date: Optional[datetime] = None
    days_of_week: Optional[List[int]] = None
    day_of_month: Optional[int] = None
    time_of_day: Optional[str] = None
    medication_name: Optional[str] = None
    dosage: Optional[str] = None
    instructions: Optional[str] = None
    is_active: Optional[bool] = None
    notify_via_push: Optional[bool] = None
    notify_via_sms: Optional[bool] = None
    notify_via_email: Optional[bool] = None
    metadata: Optional[dict] = None


class ReminderResponse(BaseModel):
    id: str
    patient_id: str
    appointment_id: Optional[str]
    medical_record_id: Optional[str]
    type: ReminderType
    title: str
    description: Optional[str]
    frequency: ReminderFrequency
    scheduled_at: datetime
    end_date: Optional[datetime]
    timezone: str
    days_of_week: Optional[List[int]]
    day_of_month: Optional[int]
    time_of_day: Optional[str]
    medication_name: Optional[str]
    dosage: Optional[str]
    instructions: Optional[str]
    is_active: bool
    is_completed: bool
    completed_at: Optional[datetime]
    snoozed_until: Optional[datetime]
    skipped_count: int
    notify_via_push: bool
    notify_via_sms: bool
    notify_via_email: bool
    last_notified_at: Optional[datetime]
    next_notification_at: Optional[datetime]
    metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReminderListResponse(BaseModel):
    reminders: List[ReminderResponse]
    total: int
    page: int
    page_size: int


class ReminderActionRequest(BaseModel):
    action: str = Field(..., pattern="^(complete|snooze|skip)$")
    snooze_minutes: Optional[int] = Field(None, ge=1, le=1440)


# ===== Patient Reminder Endpoints =====

@router.post("", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    request: ReminderCreate,
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Create a new reminder."""
    # Verify appointment if provided
    if request.appointment_id:
        appointment = db.query(AppointmentModel).filter(
            AppointmentModel.id == request.appointment_id,
            AppointmentModel.patient_id == patient.id
        ).first()
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )

    # Verify medical record if provided
    if request.medical_record_id:
        record = db.query(MedicalRecordModel).filter(
            MedicalRecordModel.id == request.medical_record_id,
            MedicalRecordModel.patient_id == patient.id
        ).first()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medical record not found"
            )

    # Set next_notification_at based on frequency
    next_notification = request.scheduled_at
    if request.frequency != ReminderFrequency.ONCE:
        next_notification = request.scheduled_at

    reminder = ReminderModel(
        id=str(uuid.uuid4()),
        patient_id=patient.id,
        appointment_id=request.appointment_id,
        medical_record_id=request.medical_record_id,
        type=request.type,
        title=request.title,
        description=request.description,
        frequency=request.frequency,
        scheduled_at=request.scheduled_at,
        end_date=request.end_date,
        timezone=request.timezone,
        days_of_week=request.days_of_week,
        day_of_month=request.day_of_month,
        time_of_day=request.time_of_day,
        medication_name=request.medication_name,
        dosage=request.dosage,
        instructions=request.instructions,
        notify_via_push=request.notify_via_push,
        notify_via_sms=request.notify_via_sms,
        notify_via_email=request.notify_via_email,
        next_notification_at=next_notification,
        metadata=request.metadata,
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


@router.get("", response_model=ReminderListResponse)
async def list_reminders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: Optional[ReminderType] = None,
    is_active: Optional[bool] = None,
    is_completed: Optional[bool] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """List reminders for the current patient."""
    query = db.query(ReminderModel).filter(ReminderModel.patient_id == patient.id)

    if type:
        query = query.filter(ReminderModel.type == type)
    if is_active is not None:
        query = query.filter(ReminderModel.is_active == is_active)
    if is_completed is not None:
        query = query.filter(ReminderModel.is_completed == is_completed)
    if from_date:
        query = query.filter(ReminderModel.scheduled_at >= from_date)
    if to_date:
        query = query.filter(ReminderModel.scheduled_at <= to_date)

    total = query.count()
    reminders = query.order_by(ReminderModel.scheduled_at.asc()).offset((page - 1) * page_size).limit(page_size).all()

    return ReminderListResponse(
        reminders=reminders,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/upcoming", response_model=List[ReminderResponse])
async def get_upcoming_reminders(
    hours: int = Query(24, ge=1, le=168),
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Get upcoming reminders for the current patient."""
    now = datetime.utcnow()
    end_time = now + timedelta(hours=hours)

    reminders = db.query(ReminderModel).filter(
        ReminderModel.patient_id == patient.id,
        ReminderModel.is_active == True,
        ReminderModel.is_completed == False,
        ReminderModel.next_notification_at >= now,
        ReminderModel.next_notification_at <= end_time
    ).order_by(ReminderModel.next_notification_at.asc()).all()

    return reminders


@router.get("/due", response_model=List[ReminderResponse])
async def get_due_reminders(
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Get reminders that are due now (for notification processing)."""
    now = datetime.utcnow()

    reminders = db.query(ReminderModel).filter(
        ReminderModel.patient_id == patient.id,
        ReminderModel.is_active == True,
        ReminderModel.is_completed == False,
        ReminderModel.next_notification_at <= now
    ).order_by(ReminderModel.next_notification_at.asc()).all()

    return reminders


@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: str,
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Get a specific reminder."""
    reminder = db.query(ReminderModel).filter(
        ReminderModel.id == reminder_id,
        ReminderModel.patient_id == patient.id
    ).first()

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )

    return reminder


@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: str,
    request: ReminderUpdate,
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Update a reminder."""
    reminder = db.query(ReminderModel).filter(
        ReminderModel.id == reminder_id,
        ReminderModel.patient_id == patient.id
    ).first()

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(reminder, field, value)

    reminder.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(reminder)
    return reminder


@router.post("/{reminder_id}/action", response_model=ReminderResponse)
async def reminder_action(
    reminder_id: str,
    request: ReminderActionRequest,
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Perform action on a reminder (complete, snooze, skip)."""
    reminder = db.query(ReminderModel).filter(
        ReminderModel.id == reminder_id,
        ReminderModel.patient_id == patient.id
    ).first()

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )

    if request.action == "complete":
        reminder.is_completed = True
        reminder.completed_at = datetime.utcnow()
        reminder.is_active = False

    elif request.action == "snooze":
        snooze_minutes = request.snooze_minutes or 15
        reminder.snoozed_until = datetime.utcnow() + timedelta(minutes=snooze_minutes)
        reminder.next_notification_at = reminder.snoozed_until

    elif request.action == "skip":
        reminder.skipped_count += 1
        # Schedule next occurrence based on frequency
        reminder.next_notification_at = calculate_next_occurrence(reminder)

    reminder.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(reminder)
    return reminder


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: str,
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Delete a reminder."""
    reminder = db.query(ReminderModel).filter(
        ReminderModel.id == reminder_id,
        ReminderModel.patient_id == patient.id
    ).first()

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )

    db.delete(reminder)
    db.commit()


@router.post("/{reminder_id}/snooze", response_model=ReminderResponse)
async def snooze_reminder(
    reminder_id: str,
    minutes: int = Query(15, ge=1, le=1440),
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Snooze a reminder for specified minutes."""
    reminder = db.query(ReminderModel).filter(
        ReminderModel.id == reminder_id,
        ReminderModel.patient_id == patient.id
    ).first()

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )

    reminder.snoozed_until = datetime.utcnow() + timedelta(minutes=minutes)
    reminder.next_notification_at = reminder.snoozed_until
    reminder.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(reminder)
    return reminder


# ===== Helper Functions =====

def calculate_next_occurrence(reminder: ReminderModel) -> Optional[datetime]:
    """Calculate next occurrence based on frequency."""
    from datetime import timedelta

    if reminder.frequency == ReminderFrequency.ONCE:
        return None

    base = reminder.next_notification_at or reminder.scheduled_at or datetime.utcnow()

    if reminder.frequency == ReminderFrequency.DAILY:
        return base + timedelta(days=1)
    elif reminder.frequency == ReminderFrequency.WEEKLY:
        return base + timedelta(weeks=1)
    elif reminder.frequency == ReminderFrequency.MONTHLY:
        # Approximate - add 30 days
        return base + timedelta(days=30)

    return None


# Add the missing import
from datetime import timedelta