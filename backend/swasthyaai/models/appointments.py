from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from backend.swasthyaai.agent.contracts import CareType


class AppointmentCreate(BaseModel):
    care_type: CareType
    requested_for: datetime | None = None


class Appointment(BaseModel):
    appointment_id: str
    care_type: CareType
    requested_for: datetime | None = None
    status: Literal["requested"] = "requested"
    created_at: datetime


class ReminderCreate(BaseModel):
    text: str = Field(min_length=1, max_length=500)


class Reminder(BaseModel):
    reminder_id: str
    text: str
    status: Literal["scheduled"] = "scheduled"
    delivery: Literal["in_app_demo"] = "in_app_demo"
    created_at: datetime
