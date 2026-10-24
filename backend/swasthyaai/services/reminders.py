import uuid
from datetime import datetime, timezone

from backend.swasthyaai.models.appointments import ReminderCreate
from backend.swasthyaai.services.db import connect


def create_reminder(patient_id: str, request: ReminderCreate) -> dict:
    reminder_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    with connect() as connection:
        connection.execute(
            "INSERT INTO reminders(reminder_id, patient_id, text, status, delivery, created_at) VALUES (?, ?, ?, 'scheduled', 'in_app_demo', ?)",
            (reminder_id, patient_id, request.text, created_at),
        )
    return {
        "reminder_id": reminder_id,
        "text": request.text,
        "status": "scheduled",
        "delivery": "in_app_demo",
        "created_at": created_at,
    }


def list_reminders(patient_id: str) -> list[dict]:
    with connect() as connection:
        rows = connection.execute(
            "SELECT reminder_id, text, status, delivery, created_at FROM reminders WHERE patient_id = ? ORDER BY created_at",
            (patient_id,),
        ).fetchall()
    return [dict(row) for row in rows]
