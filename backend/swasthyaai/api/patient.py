from fastapi import APIRouter, Depends, HTTPException, Response

from backend.swasthyaai.models.auth import User
from backend.swasthyaai.models.records import Record, RecordCategory, RecordCreate
from backend.swasthyaai.services.auth import require_role
from backend.swasthyaai.services.records import create_record, delete_record, list_records

router = APIRouter(prefix="/patient")


@router.post("/records/{category}", response_model=Record, status_code=201)
def add_record(
    category: RecordCategory,
    request: RecordCreate,
    user: User = Depends(require_role("patient")),
) -> dict:
    return create_record(user.user_id, category, request.data)


@router.get("/records/{category}", response_model=list[Record])
def get_records(
    category: RecordCategory,
    user: User = Depends(require_role("patient")),
) -> list[dict]:
    return list_records(user.user_id, category)


@router.delete("/records/{record_id}", status_code=204)
def remove_record(
    record_id: str,
    user: User = Depends(require_role("patient")),
) -> Response:
    if not delete_record(user.user_id, record_id):
        raise HTTPException(status_code=404, detail="Record not found")
    return Response(status_code=204)
