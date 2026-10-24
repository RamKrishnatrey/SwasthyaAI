from fastapi import APIRouter, Depends

from backend.swasthyaai.models.appointments import Reminder, ReminderCreate
from backend.swasthyaai.models.auth import User
from backend.swasthyaai.services.auth import require_role
from backend.swasthyaai.services.reminders import create_reminder, list_reminders

router = APIRouter(prefix="/reminders")


@router.post("", response_model=Reminder, status_code=201)
def add_reminder(
    request: ReminderCreate,
    user: User = Depends(require_role("patient")),
) -> dict:
    return create_reminder(user.user_id, request)


@router.get("", response_model=list[Reminder])
def reminders(user: User = Depends(require_role("patient"))) -> list[dict]:
    return list_reminders(user.user_id)
