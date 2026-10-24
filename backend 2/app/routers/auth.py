# SwasthyaAI Authentication Router
# Registration, login, token refresh, password reset

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta
from typing import Optional
import secrets

from app.db import get_db
from app.config import get_settings
from app.services.auth import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    decode_token, generate_user_id, generate_patient_id, generate_clinician_id,
    get_current_user, get_current_active_user, get_current_patient, get_current_clinician,
    require_role, UserRole, UserStatus
)
from app.models.user import UserModel, PatientProfileModel, ClinicianProfileModel

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer(auto_error=False)
settings = get_settings()


# ===== Request/Response Schemas =====

class RegisterRequest(BaseModel):
    email: EmailStr
    phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=100)
    role: UserRole = UserRole.PATIENT
    language: str = Field(default="en", pattern=r'^(en|hi|hinglish)$')


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: str
    email: str
    phone: Optional[str]
    full_name: str
    role: UserRole
    status: UserStatus
    language: str
    email_verified: bool
    phone_verified: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class PatientProfileResponse(BaseModel):
    id: str
    user_id: str
    date_of_birth: Optional[datetime]
    gender: Optional[str]
    blood_group: Optional[str]
    height_cm: Optional[int]
    weight_kg: Optional[int]
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    emergency_contact_relation: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    pincode: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    allergies: Optional[str]
    chronic_conditions: Optional[str]
    current_medications: Optional[str]
    family_history: Optional[str]
    insurance_provider: Optional[str]
    insurance_policy_number: Optional[str]
    preferred_language: str
    notification_preferences: Optional[str]

    class Config:
        from_attributes = True


class PatientProfileUpdate(BaseModel):
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None
    current_medications: Optional[str] = None
    family_history: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_policy_number: Optional[str] = None
    preferred_language: Optional[str] = None
    notification_preferences: Optional[str] = None


# ===== Helper Functions =====

def create_user_response(user: UserModel) -> dict:
    """Create user dict for token response."""
    return {
        "id": user.id,
        "email": user.email,
        "phone": user.phone,
        "full_name": user.full_name,
        "role": user.role.value,
        "status": user.status.value,
        "language": user.language,
        "email_verified": user.email_verified,
        "phone_verified": user.phone_verified,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
    }


# ===== Authentication Endpoints =====

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if email already exists
    existing_user = db.query(UserModel).filter(UserModel.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if phone already exists
    if request.phone:
        existing_phone = db.query(UserModel).filter(UserModel.phone == request.phone).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )

    # Hash password
    hashed_password = hash_password(request.password)

    # Create user
    user_id = generate_user_id()
    user = UserModel(
        id=user_id,
        email=request.email,
        phone=request.phone,
        hashed_password=hashed_password,
        full_name=request.full_name,
        role=request.role,
        language=request.language,
        status=UserStatus.ACTIVE if request.role == UserRole.PATIENT else UserStatus.PENDING_VERIFICATION,
    )
    db.add(user)

    # Create patient profile if patient
    if request.role == UserRole.PATIENT:
        patient_id = generate_patient_id()
        patient = PatientProfileModel(
            id=patient_id,
            user_id=user_id,
            preferred_language=request.language,
        )
        db.add(patient)

    # Create clinician profile if clinician
    elif request.role == UserRole.CLINICIAN:
        clinician_id = generate_clinician_id()
        clinician = ClinicianProfileModel(
            id=clinician_id,
            user_id=user_id,
            license_number=f"TEMP-{secrets.token_hex(8).upper()}",  # Temporary, must be updated
            specialization="General",
        )
        db.add(clinician)

    db.commit()
    db.refresh(user)

    # Create tokens
    access_token = create_access_token({"sub": user.id, "role": user.role.value})
    refresh_token = create_refresh_token({"sub": user.id, "role": user.role.value})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user=create_user_response(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password."""
    user = db.query(UserModel).filter(UserModel.email == request.email).first()

    if not user or not verify_password(request.password, user.hashed_password):
        # Increment failed login attempts
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account temporarily locked due to failed attempts. Try again later."
        )

    # Check if account is active
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active. Please contact support."
        )

    # Reset failed login attempts on successful login
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.utcnow()
    db.commit()

    # Create tokens
    access_token = create_access_token({"sub": user.id, "role": user.role.value})
    refresh_token = create_refresh_token({"sub": user.id, "role": user.role.value})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user=create_user_response(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    payload = decode_token(request.refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user or user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Create new tokens
    access_token = create_access_token({"sub": user.id, "role": user.role.value})
    refresh_token = create_refresh_token({"sub": user.id, "role": user.role.value})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user=create_user_response(user),
    )


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Logout - in a stateless JWT system, this is mainly client-side.
    Could be extended with token blacklisting if needed."""
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserModel = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    full_name: Optional[str] = None,
    language: Optional[str] = None,
    phone: Optional[str] = None,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user profile."""
    if full_name is not None:
        current_user.full_name = full_name
    if language is not None:
        current_user.language = language
    if phone is not None:
        # Check if phone is already taken
        existing = db.query(UserModel).filter(UserModel.phone == phone, UserModel.id != current_user.id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already in use"
            )
        current_user.phone = phone
        current_user.phone_verified = False

    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/change-password")
async def change_password(
    request: PasswordChangeRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change password for authenticated user."""
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    current_user.hashed_password = hash_password(request.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Password changed successfully"}


@router.post("/forgot-password")
async def forgot_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """Request password reset - generates reset token."""
    user = db.query(UserModel).filter(UserModel.email == request.email).first()

    # Always return success to prevent email enumeration
    if not user:
        return {"message": "If the email exists, a reset link has been sent"}

    # Generate reset token (in production, send via email)
    reset_token = secrets.token_urlsafe(32)
    # Store token with expiry (in production, use Redis or database)
    # For now, we'll just return it (in production, email it)
    return {
        "message": "If the email exists, a reset link has been sent",
        "reset_token": reset_token  # Remove in production!
    }


@router.post("/reset-password")
async def reset_password(request: PasswordResetConfirmRequest, db: Session = Depends(get_db)):
    """Reset password with token."""
    # In production, verify token from Redis/database
    # For now, decode the token to get user_id
    try:
        payload = decode_token(request.token)
        user_id = payload.get("sub")
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )

    user.hashed_password = hash_password(request.new_password)
    user.failed_login_attempts = 0
    user.locked_until = None
    user.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Password reset successfully"}


# ===== Patient Profile Endpoints =====

@router.get("/me/patient-profile", response_model=PatientProfileResponse)
async def get_patient_profile(
    patient: PatientProfileModel = Depends(get_current_patient)
):
    """Get current user's patient profile."""
    return patient


@router.put("/me/patient-profile", response_model=PatientProfileResponse)
async def update_patient_profile(
    request: PatientProfileUpdate,
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Update current user's patient profile."""
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    patient.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(patient)
    return patient


# ===== Clinician Profile Endpoints =====

@router.get("/me/clinician-profile")
async def get_clinician_profile(
    clinician: ClinicianProfileModel = Depends(get_current_clinician)
):
    """Get current user's clinician profile."""
    return clinician


# ===== Admin Endpoints =====

@router.get("/users", dependencies=[Depends(require_role(UserRole.ADMIN))])
async def list_users(
    skip: int = 0,
    limit: int = 50,
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None,
    db: Session = Depends(get_db)
):
    """List all users (admin only)."""
    query = db.query(UserModel)
    if role:
        query = query.filter(UserModel.role == role)
    if status:
        query = query.filter(UserModel.status == status)
    users = query.offset(skip).limit(limit).all()
    return {"users": [create_user_response(u) for u in users], "total": query.count()}


@router.put("/users/{user_id}/status", dependencies=[Depends(require_role(UserRole.ADMIN))])
async def update_user_status(
    user_id: str,
    new_status: UserStatus,
    db: Session = Depends(get_db)
):
    """Update user status (admin only)."""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    user.status = new_status
    user.updated_at = datetime.utcnow()
    db.commit()
    return create_user_response(user)