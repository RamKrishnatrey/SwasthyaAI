import json
import uuid
from datetime import datetime, timezone

from backend.swasthyaai.services.db import connect


_CATEGORIES = {"history", "allergies", "medications", "report_metadata"}


def create_record(patient_id: str, category: str, data: dict[str, str]) -> dict | None:
    if category not in _CATEGORIES:
        return None
    record_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    with connect() as connection:
        connection.execute(
            "INSERT INTO records(record_id, patient_id, category, payload_json, created_at) VALUES (?, ?, ?, ?, ?)",
            (record_id, patient_id, category, json.dumps(data), created_at),
        )
    return {"record_id": record_id, "category": category, "data": data, "created_at": created_at}


def list_records(patient_id: str, category: str) -> list[dict]:
    if category not in _CATEGORIES:
        return []
    with connect() as connection:
        rows = connection.execute(
            "SELECT record_id, category, payload_json, created_at FROM records WHERE patient_id = ? AND category = ? ORDER BY created_at",
            (patient_id, category),
        ).fetchall()
    return [
        {"record_id": row["record_id"], "category": row["category"], "data": json.loads(row["payload_json"]), "created_at": row["created_at"]}
        for row in rows
    ]


def delete_record(patient_id: str, record_id: str) -> bool:
    with connect() as connection:
        cursor = connection.execute(
            "DELETE FROM records WHERE record_id = ? AND patient_id = ?",
            (record_id, patient_id),
        )
    return cursor.rowcount == 1
