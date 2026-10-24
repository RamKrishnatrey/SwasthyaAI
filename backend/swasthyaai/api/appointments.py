from fastapi import APIRouter, Depends, Header, HTTPException, Response

from backend.swasthyaai.models.appointments import Appointment, AppointmentCreate
from backend.swasthyaai.models.auth import User
from backend.swasthyaai.services.appointments import create_appointment, list_appointments
from backend.swasthyaai.services.auth import require_role

router = APIRouter(prefix="/appointments")


@router.post("", response_model=Appointment, status_code=201)
def request_appointment(
    request: AppointmentCreate,
    response: Response,
    idempotency_key: str = Header(..., alias="Idempotency-Key", min_length=1, max_length=128),
    user: User = Depends(require_role("patient")),
) -> dict:
    try:
        result = create_appointment(user.user_id, request, idempotency_key)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    if result is None:
        raise HTTPException(status_code=422, detail="Emergency requests must use emergency services, not scheduling")
    appointment, created = result
    if not created:
        response.status_code = 200
    return appointment


@router.get("", response_model=list[Appointment])
def appointments(user: User = Depends(require_role("patient"))) -> list[dict]:
    return list_appointments(user.user_id)
