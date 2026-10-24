# SwasthyaAI Medical Records Router
# Medical record management, document upload, AI analysis

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
import uuid
import os
import hashlib
import json

from app.db import get_db
from app.services.auth import get_current_active_user, get_current_patient, get_current_clinician
from app.models.user import UserModel, PatientProfileModel, ClinicianProfileModel, UserRole
from app.models.appointment import MedicalRecordModel, MedicalRecordType, AppointmentModel

router = APIRouter(prefix="/api/medical-records", tags=["medical-records"])

# Upload directory
UPLOAD_DIR = "./uploads/medical_records"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.dcm', '.dicom', '.txt', '.csv'}


# ===== Request/Response Schemas =====

class MedicalRecordCreate(BaseModel):
    appointment_id: Optional[str] = None
    type: MedicalRecordType
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    record_date: datetime
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    tags: Optional[List[str]] = None
    body_system: Optional[str] = None
    icd_codes: Optional[List[str]] = None
    is_sensitive: bool = False
    share_with_clinicians: bool = True
    share_with_family: bool = False
    structured_data: Optional[dict] = None


class MedicalRecordUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[MedicalRecordType] = None
    record_date: Optional[datetime] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    tags: Optional[List[str]] = None
    body_system: Optional[str] = None
    icd_codes: Optional[List[str]] = None
    is_sensitive: Optional[bool] = None
    share_with_clinicians: Optional[bool] = None
    share_with_family: Optional[bool] = None
    structured_data: Optional[dict] = None
    ai_analysis: Optional[str] = None
    ai_model: Optional[str] = None
    ai_confidence: Optional[float] = None


class MedicalRecordResponse(BaseModel):
    id: str
    patient_id: str
    appointment_id: Optional[str]
    clinician_id: Optional[str]
    type: MedicalRecordType
    title: str
    description: Optional[str]
    file_path: Optional[str]
    file_name: Optional[str]
    file_size: Optional[int]
    file_type: Optional[str]
    file_hash: Optional[str]
    structured_data: Optional[dict]
    extracted_text: Optional[str]
    ai_analysis: Optional[str]
    ai_model: Optional[str]
    ai_confidence: Optional[float]
    ai_processed_at: Optional[datetime]
    record_date: datetime
    valid_from: Optional[datetime]
    valid_until: Optional[datetime]
    tags: Optional[List[str]]
    body_system: Optional[str]
    icd_codes: Optional[List[str]]
    is_sensitive: bool
    share_with_clinicians: bool
    share_with_family: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MedicalRecordListResponse(BaseModel):
    records: List[MedicalRecordResponse]
    total: int
    page: int
    page_size: int


# ===== Helper Functions =====

def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA256 hash of file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def validate_file(file: UploadFile) -> tuple[bool, str]:
    """Validate uploaded file."""
    if not file.filename:
        return False, "No filename provided"

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"File type {ext} not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"

    return True, ""


# ===== Patient Medical Record Endpoints =====

@router.post("", response_model=MedicalRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_medical_record(
    request: MedicalRecordCreate,
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Create a medical record entry (without file upload)."""
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

    record = MedicalRecordModel(
        id=str(uuid.uuid4()),
        patient_id=patient.id,
        appointment_id=request.appointment_id,
        type=request.type,
        title=request.title,
        description=request.description,
        record_date=request.record_date,
        valid_from=request.valid_from,
        valid_until=request.valid_until,
        tags=request.tags or [],
        body_system=request.body_system,
        icd_codes=request.icd_codes or [],
        is_sensitive=request.is_sensitive,
        share_with_clinicians=request.share_with_clinicians,
        share_with_family=request.share_with_family,
        structured_data=request.structured_data,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/upload", response_model=MedicalRecordResponse, status_code=status.HTTP_201_CREATED)
async def upload_medical_record(
    file: UploadFile = File(...),
    type: MedicalRecordType = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    appointment_id: Optional[str] = Form(None),
    record_date: str = Form(...),  # ISO format
    valid_from: Optional[str] = Form(None),
    valid_until: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # JSON array
    body_system: Optional[str] = Form(None),
    icd_codes: Optional[str] = Form(None),  # JSON array
    is_sensitive: bool = Form(False),
    share_with_clinicians: bool = Form(True),
    share_with_family: bool = Form(False),
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Upload a medical record file."""
    # Validate file
    is_valid, error = validate_file(file)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    # Check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)} MB"
        )

    # Verify appointment if provided
    if appointment_id:
        appointment = db.query(AppointmentModel).filter(
            AppointmentModel.id == appointment_id,
            AppointmentModel.patient_id == patient.id
        ).first()
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )

    # Save file
    file_ext = os.path.splitext(file.filename)[1].lower()
    file_name = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    with open(file_path, "wb") as f:
        f.write(content)

    # Calculate hash
    file_hash = calculate_file_hash(file_path)

    # Parse JSON fields
    tags_list = json.loads(tags) if tags else []
    icd_list = json.loads(icd_codes) if icd_codes else []

    # Parse dates
    record_dt = datetime.fromisoformat(record_date.replace('Z', '+00:00'))
    valid_from_dt = datetime.fromisoformat(valid_from.replace('Z', '+00:00')) if valid_from else None
    valid_until_dt = datetime.fromisoformat(valid_until.replace('Z', '+00:00')) if valid_until else None

    record = MedicalRecordModel(
        id=str(uuid.uuid4()),
        patient_id=patient.id,
        appointment_id=appointment_id,
        type=type,
        title=title,
        description=description,
        file_path=file_path,
        file_name=file.filename,
        file_size=len(content),
        file_type=file.content_type,
        file_hash=file_hash,
        record_date=record_dt,
        valid_from=valid_from_dt,
        valid_until=valid_until_dt,
        tags=tags_list,
        body_system=body_system,
        icd_codes=icd_list,
        is_sensitive=is_sensitive,
        share_with_clinicians=share_with_clinicians,
        share_with_family=share_with_family,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=MedicalRecordListResponse)
async def list_medical_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: Optional[MedicalRecordType] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    tag: Optional[str] = None,
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """List medical records for the current patient."""
    query = db.query(MedicalRecordModel).filter(MedicalRecordModel.patient_id == patient.id)

    if type:
        query = query.filter(MedicalRecordModel.type == type)
    if from_date:
        query = query.filter(MedicalRecordModel.record_date >= from_date)
    if to_date:
        query = query.filter(MedicalRecordModel.record_date <= to_date)
    if tag:
        # Filter by tag (JSON contains)
        query = query.filter(MedicalRecordModel.tags.contains([tag]))

    total = query.count()
    records = query.order_by(MedicalRecordModel.record_date.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return MedicalRecordListResponse(
        records=records,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{record_id}", response_model=MedicalRecordResponse)
async def get_medical_record(
    record_id: str,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific medical record."""
    record = db.query(MedicalRecordModel).filter(MedicalRecordModel.id == record_id).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found"
        )

    # Check authorization
    if current_user.role == UserRole.PATIENT:
        patient = db.query(PatientProfileModel).filter(PatientProfileModel.user_id == current_user.id).first()
        if not patient or record.patient_id != patient.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this record"
            )
    elif current_user.role == UserRole.CLINICIAN:
        if not record.share_with_clinicians:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Record not shared with clinicians"
            )
        clinician = db.query(ClinicianProfileModel).filter(ClinicianProfileModel.user_id == current_user.id).first()
        if not clinician or record.clinician_id != clinician.id:
            # Check if clinician has appointment with this patient
            appointment = db.query(AppointmentModel).filter(
                AppointmentModel.clinician_id == clinician.id,
                AppointmentModel.patient_id == record.patient_id
            ).first()
            if not appointment:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view this record"
                )

    return record


@router.put("/{record_id}", response_model=MedicalRecordResponse)
async def update_medical_record(
    record_id: str,
    request: MedicalRecordUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a medical record."""
    record = db.query(MedicalRecordModel).filter(MedicalRecordModel.id == record_id).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found"
        )

    # Check authorization
    if current_user.role == UserRole.PATIENT:
        patient = db.query(PatientProfileModel).filter(PatientProfileModel.user_id == current_user.id).first()
        if not patient or record.patient_id != patient.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this record"
            )
    elif current_user.role == UserRole.CLINICIAN:
        clinician = db.query(ClinicianProfileModel).filter(ClinicianProfileModel.user_id == current_user.id).first()
        if not clinician or record.clinician_id != clinician.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this record"
            )

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "ai_analysis" and value:
            value = value
            record.ai_processed_at = datetime.utcnow()
        setattr(record, field, value)

    record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medical_record(
    record_id: str,
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Delete a medical record."""
    record = db.query(MedicalRecordModel).filter(
        MedicalRecordModel.id == record_id,
        MedicalRecordModel.patient_id == patient.id
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found"
        )

    # Delete file if exists
    if record.file_path and os.path.exists(record.file_path):
        os.remove(record.file_path)

    db.delete(record)
    db.commit()


@router.get("/{record_id}/download")
async def download_medical_record(
    record_id: str,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Download a medical record file."""
    from fastapi.responses import FileResponse

    record = db.query(MedicalRecordModel).filter(MedicalRecordModel.id == record_id).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found"
        )

    if not record.file_path or not os.path.exists(record.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    # Check authorization (same as get_medical_record)
    if current_user.role == UserRole.PATIENT:
        patient = db.query(PatientProfileModel).filter(PatientProfileModel.user_id == current_user.id).first()
        if not patient or record.patient_id != patient.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    elif current_user.role == UserRole.CLINICIAN:
        if not record.share_with_clinicians:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not shared with clinicians")
        clinician = db.query(ClinicianProfileModel).filter(ClinicianProfileModel.user_id == current_user.id).first()
        if not clinician or record.clinician_id != clinician.id:
            appointment = db.query(AppointmentModel).filter(
                AppointmentModel.clinician_id == clinician.id,
                AppointmentModel.patient_id == record.patient_id
            ).first()
            if not appointment:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return FileResponse(
        path=record.file_path,
        filename=record.file_name or "medical_record",
        media_type=record.file_type or "application/octet-stream"
    )


# ===== AI Analysis Endpoint =====

@router.post("/{record_id}/analyze", response_model=MedicalRecordResponse)
async def analyze_medical_record(
    record_id: str,
    clinician: ClinicianProfileModel = Depends(get_current_clinician),
    db: Session = Depends(get_db)
):
    """Trigger AI analysis of a medical record (placeholder for ML integration)."""
    record = db.query(MedicalRecordModel).filter(MedicalRecordModel.id == record_id).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found"
        )

    if record.clinician_id and record.clinician_id != clinician.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to analyze this record"
        )

    # Placeholder for AI analysis
    # In production, this would call the ML service
    record.ai_analysis = "AI analysis placeholder - would integrate with ML models for report analysis"
    record.ai_model = "swasthyaai-medical-report-analyzer-v1"
    record.ai_confidence = 0.0
    record.ai_processed_at = datetime.utcnow()
    record.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(record)
    return record