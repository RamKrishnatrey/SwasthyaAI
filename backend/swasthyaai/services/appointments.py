import uuid
from datetime import datetime, timezone

from backend.swasthyaai.agent.contracts import CareType
from backend.swasthyaai.models.appointments import AppointmentCreate
from backend.swasthyaai.services.db import connect


def create_appointment(patient_id: str, request: AppointmentCreate, idempotency_key: str) -> tuple[dict, bool] | None:
    if request.care_type == CareType.EMERGENCY_112:
        return None
    requested_for = request.requested_for.isoformat() if request.requested_for else None
    with connect() as connection:
        connection.execute("BEGIN IMMEDIATE")
        existing = connection.execute(
            "SELECT appointment_id, care_type, requested_for, status, created_at FROM appointments WHERE patient_id = ? AND idempotency_key = ?",
            (patient_id, idempotency_key),
        ).fetchone()
        if existing is not None:
            if existing["care_type"] != request.care_type.value or existing["requested_for"] != requested_for:
                raise ValueError("Idempotency-Key was already used for a different appointment request")
            return dict(existing), False
        appointment_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        connection.execute(
            "INSERT INTO appointments(appointment_id, patient_id, care_type, requested_for, idempotency_key, status, created_at) VALUES (?, ?, ?, ?, ?, 'requested', ?)",
            (appointment_id, patient_id, request.care_type.value, requested_for, idempotency_key, created_at),
        )
    return {
        "appointment_id": appointment_id,
        "care_type": request.care_type,
        "requested_for": requested_for,
        "status": "requested",
        "created_at": created_at,
    }, True


def list_appointments(patient_id: str) -> list[dict]:
    with connect() as connection:
        rows = connection.execute(
            "SELECT appointment_id, care_type, requested_for, status, created_at FROM appointments WHERE patient_id = ? ORDER BY created_at",
            (patient_id,),
        ).fetchall()
    return [dict(row) for row in rows]
