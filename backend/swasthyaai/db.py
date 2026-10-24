import sqlite3
from pathlib import Path


_SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password_salt BLOB NOT NULL,
    password_hash BLOB NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('patient', 'clinician')),
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
    token_digest TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS records (
    record_id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    care_type TEXT NOT NULL,
    requested_for TEXT,
    idempotency_key TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status = 'requested'),
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS reminders (
    reminder_id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status = 'scheduled'),
    delivery TEXT NOT NULL CHECK (delivery = 'in_app_demo'),
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_records_patient_category ON records(patient_id, category);
CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_id);
CREATE INDEX IF NOT EXISTS idx_reminders_patient ON reminders(patient_id);
"""


def init_db(path: str | Path) -> None:
    database = Path(path)
    database.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database) as connection:
        connection.executescript(_SCHEMA)
        columns = {row[1] for row in connection.execute("PRAGMA table_info(appointments)")}
        if "idempotency_key" not in columns:
            connection.execute("ALTER TABLE appointments ADD COLUMN idempotency_key TEXT")
            connection.execute("UPDATE appointments SET idempotency_key = appointment_id WHERE idempotency_key IS NULL")
        connection.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_appointments_idempotency ON appointments(patient_id, idempotency_key)"
        )
