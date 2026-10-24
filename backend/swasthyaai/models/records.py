from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


RecordCategory = Literal["history", "allergies", "medications", "report_metadata"]


class RecordCreate(BaseModel):
    data: dict[str, str] = Field(min_length=1, max_length=20)

    @field_validator("data")
    @classmethod
    def metadata_only(cls, value: dict[str, str]) -> dict[str, str]:
        forbidden = {"file", "file_data", "content", "path", "upload", "blob"}
        if any(key.casefold() in forbidden or len(key) > 64 or len(item) > 2000 for key, item in value.items()):
            raise ValueError("Records accept bounded metadata only; file uploads are not supported")
        return value


class Record(BaseModel):
    record_id: str
    category: RecordCategory
    data: dict[str, str]
    created_at: datetime
