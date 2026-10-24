import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class EmailRequest(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip().casefold()
        if len(normalized) > 254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", normalized):
            raise ValueError("A valid email address is required")
        return normalized


class RegisterRequest(EmailRequest):
    password: str = Field(min_length=12, max_length=256)
    role: Literal["patient", "clinician"]


class LoginRequest(EmailRequest):
    password: str = Field(min_length=1, max_length=256)


class User(BaseModel):
    user_id: str
    email: str
    role: Literal["patient", "clinician"]


class Session(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_at: datetime
    user: User
