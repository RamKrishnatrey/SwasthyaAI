# SwasthyaAI Conversations Router
# Chat history, AI interactions, symptom assessments

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
import uuid

from app.db import get_db
from app.services.auth import get_current_active_user, get_current_patient
from app.models.user import UserModel, PatientProfileModel
from app.models.conversation import ConversationModel, MessageModel, SymptomAssessmentModel, ConversationType, ConversationStatus, MessageRole

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


# ===== Request/Response Schemas =====

class ConversationCreate(BaseModel):
    type: ConversationType = ConversationType.GENERAL_CHAT
    language: str = Field(default="en", pattern=r'^(en|hi|hinglish)$')
    title: Optional[str] = None


class ConversationResponse(BaseModel):
    id: str
    patient_id: str
    type: ConversationType
    status: ConversationStatus
    language: str
    title: Optional[str]
    summary: Optional[str]
    metadata: Optional[dict]
    started_at: datetime
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    conversations: List[ConversationResponse]
    total: int
    page: int
    page_size: int


class MessageCreate(BaseModel):
    role: MessageRole
    content: str
    content_type: str = "text"
    metadata: Optional[dict] = None


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: MessageRole
    content: str
    content_type: str
    metadata: Optional[dict]
    tokens_used: Optional[int]
    model_name: Optional[str]
    model_version: Optional[str]
    confidence: Optional[float]
    processing_time_ms: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    messages: List[MessageResponse]
    total: int


class SymptomAssessmentCreate(BaseModel):
    session_id: str
    original_text: str
    extracted_who: Optional[str] = None
    extracted_symptoms: Optional[List[str]] = None
    extracted_duration: Optional[str] = None
    extracted_age_group: Optional[str] = None
    detected_language: str = "en"


class SymptomAssessmentResponse(BaseModel):
    id: str
    conversation_id: str
    patient_id: str
    session_id: str
    original_text: str
    extracted_who: Optional[str]
    extracted_symptoms: Optional[List[str]]
    extracted_duration: Optional[str]
    extracted_age_group: Optional[str]
    detected_language: str
    follow_up_answers: Optional[dict]
    safety_red_flag: bool
    safety_flags: Optional[List[dict]]
    safety_instructions: Optional[str]
    bypass_matching: bool
    care_type: Optional[str]
    urgency: Optional[str]
    triage_reason: Optional[str]
    triage_confidence: Optional[float]
    model_source: str
    suggested_specialty: Optional[str]
    matched_caregivers: Optional[List[dict]]
    selected_caregiver_id: Optional[str]
    is_complete: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== Conversation Endpoints =====

@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    request: ConversationCreate,
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Create a new conversation."""
    conversation = ConversationModel(
        id=str(uuid.uuid4()),
        patient_id=patient.id,
        type=request.type,
        language=request.language,
        title=request.title,
        status=ConversationStatus.ACTIVE,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: Optional[ConversationType] = None,
    status: Optional[ConversationStatus] = None,
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """List conversations for the current patient."""
    query = db.query(ConversationModel).filter(ConversationModel.patient_id == patient.id)

    if type:
        query = query.filter(ConversationModel.type == type)
    if status:
        query = query.filter(ConversationModel.status == status)

    total = query.count()
    conversations = query.order_by(ConversationModel.started_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # Add message counts
    result = []
    for conv in conversations:
        msg_count = db.query(MessageModel).filter(MessageModel.conversation_id == conv.id).count()
        conv_dict = ConversationResponse.model_validate(conv)
        conv_dict.message_count = msg_count
        result.append(conv_dict)

    return ConversationListResponse(
        conversations=result,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Get a specific conversation."""
    conversation = db.query(ConversationModel).filter(
        ConversationModel.id == conversation_id,
        ConversationModel.patient_id == patient.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    msg_count = db.query(MessageModel).filter(MessageModel.conversation_id == conversation.id).count()
    conv_dict = ConversationResponse.model_validate(conversation)
    conv_dict.message_count = msg_count
    return conv_dict


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    title: Optional[str] = None,
    status: Optional[ConversationStatus] = None,
    summary: Optional[str] = None,
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Update a conversation."""
    conversation = db.query(ConversationModel).filter(
        ConversationModel.id == conversation_id,
        ConversationModel.patient_id == patient.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    if title is not None:
        conversation.title = title
    if status is not None:
        conversation.status = status
        if status == ConversationStatus.COMPLETED:
            conversation.completed_at = datetime.utcnow()
    if summary is not None:
        conversation.summary = summary

    conversation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(conversation)
    return conversation


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Delete a conversation (soft delete - archive)."""
    conversation = db.query(ConversationModel).filter(
        ConversationModel.id == conversation_id,
        ConversationModel.patient_id == patient.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    conversation.status = ConversationStatus.ARCHIVED
    conversation.updated_at = datetime.utcnow()
    db.commit()


# ===== Message Endpoints =====

@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_message(
    conversation_id: str,
    request: MessageCreate,
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Add a message to a conversation."""
    conversation = db.query(ConversationModel).filter(
        ConversationModel.id == conversation_id,
        ConversationModel.patient_id == patient.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    if conversation.status != ConversationStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add messages to non-active conversation"
        )

    message = MessageModel(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        role=request.role,
        content=request.content,
        content_type=request.content_type,
        metadata=request.metadata,
    )
    db.add(message)

    conversation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(message)
    return message


@router.get("/{conversation_id}/messages", response_model=MessageListResponse)
async def list_messages(
    conversation_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """List messages in a conversation."""
    conversation = db.query(ConversationModel).filter(
        ConversationModel.id == conversation_id,
        ConversationModel.patient_id == patient.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    query = db.query(MessageModel).filter(MessageModel.conversation_id == conversation_id)
    total = query.count()
    messages = query.order_by(MessageModel.created_at.asc()).offset((page - 1) * page_size).limit(page_size).all()

    return MessageListResponse(messages=messages, total=total)


# ===== Symptom Assessment Endpoints =====

@router.post("/{conversation_id}/assessments", response_model=SymptomAssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_symptom_assessment(
    conversation_id: str,
    request: SymptomAssessmentCreate,
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Create a symptom assessment record."""
    conversation = db.query(ConversationModel).filter(
        ConversationModel.id == conversation_id,
        ConversationModel.patient_id == patient.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    assessment = SymptomAssessmentModel(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        patient_id=patient.id,
        session_id=request.session_id,
        original_text=request.original_text,
        extracted_who=request.extracted_who,
        extracted_symptoms=request.extracted_symptoms or [],
        extracted_duration=request.extracted_duration,
        extracted_age_group=request.extracted_age_group,
        detected_language=request.detected_language,
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@router.get("/{conversation_id}/assessments", response_model=List[SymptomAssessmentResponse])
async def list_symptom_assessments(
    conversation_id: str,
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """List symptom assessments for a conversation."""
    conversation = db.query(ConversationModel).filter(
        ConversationModel.id == conversation_id,
        ConversationModel.patient_id == patient.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    assessments = db.query(SymptomAssessmentModel).filter(
        SymptomAssessmentModel.conversation_id == conversation_id
    ).order_by(SymptomAssessmentModel.created_at.desc()).all()

    return assessments


@router.get("/{conversation_id}/assessments/{assessment_id}", response_model=SymptomAssessmentResponse)
async def get_symptom_assessment(
    conversation_id: str,
    assessment_id: str,
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Get a specific symptom assessment."""
    assessment = db.query(SymptomAssessmentModel).filter(
        SymptomAssessmentModel.id == assessment_id,
        SymptomAssessmentModel.conversation_id == conversation_id,
        SymptomAssessmentModel.patient_id == patient.id
    ).first()

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )

    return assessment


@router.put("/{conversation_id}/assessments/{assessment_id}", response_model=SymptomAssessmentResponse)
async def update_symptom_assessment(
    conversation_id: str,
    assessment_id: str,
    follow_up_answers: Optional[dict] = None,
    safety_red_flag: Optional[bool] = None,
    safety_flags: Optional[List[dict]] = None,
    safety_instructions: Optional[str] = None,
    bypass_matching: Optional[bool] = None,
    care_type: Optional[str] = None,
    urgency: Optional[str] = None,
    triage_reason: Optional[str] = None,
    triage_confidence: Optional[float] = None,
    model_source: Optional[str] = None,
    suggested_specialty: Optional[str] = None,
    matched_caregivers: Optional[List[dict]] = None,
    selected_caregiver_id: Optional[str] = None,
    is_complete: Optional[bool] = None,
    patient: PatientProfileModel = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Update a symptom assessment with triage/matching results."""
    assessment = db.query(SymptomAssessmentModel).filter(
        SymptomAssessmentModel.id == assessment_id,
        SymptomAssessmentModel.conversation_id == conversation_id,
        SymptomAssessmentModel.patient_id == patient.id
    ).first()

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )

    if follow_up_answers is not None:
        assessment.follow_up_answers = follow_up_answers
    if safety_red_flag is not None:
        assessment.safety_red_flag = safety_red_flag
    if safety_flags is not None:
        assessment.safety_flags = safety_flags
    if safety_instructions is not None:
        assessment.safety_instructions = safety_instructions
    if bypass_matching is not None:
        assessment.bypass_matching = bypass_matching
    if care_type is not None:
        assessment.care_type = care_type
    if urgency is not None:
        assessment.urgency = urgency
    if triage_reason is not None:
        assessment.triage_reason = triage_reason
    if triage_confidence is not None:
        assessment.triage_confidence = triage_confidence
    if model_source is not None:
        assessment.model_source = model_source
    if suggested_specialty is not None:
        assessment.suggested_specialty = suggested_specialty
    if matched_caregivers is not None:
        assessment.matched_caregivers = matched_caregivers
    if selected_caregiver_id is not None:
        assessment.selected_caregiver_id = selected_caregiver_id
    if is_complete is not None:
        assessment.is_complete = is_complete

    assessment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(assessment)
    return assessment