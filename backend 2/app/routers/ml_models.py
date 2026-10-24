# SwasthyaAI ML Models Router
# Model inference endpoints for trained ML/DL models

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.services.auth import get_current_active_user, get_current_user_optional
from app.services.ml_models import (
    model_registry,
    ModelMetadata,
    ModelFormat,
    ModelTask,
    DDXPlusInference,
    predict_triage,
    initialize_models,
    get_model_registry,
)

router = APIRouter(prefix="/api/ml", tags=["ml-models"])


# ===== Request/Response Schemas =====

class ModelMetadataResponse(BaseModel):
    name: str
    version: str
    task: str
    format: str
    path: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    labels: List[str]
    description: str
    created_at: str
    metrics: Dict[str, float]
    requirements: Dict[str, str]

    class Config:
        from_attributes = True


class ModelListResponse(BaseModel):
    models: List[ModelMetadataResponse]
    total: int


class TriagePredictionRequest(BaseModel):
    symptoms: List[str] = Field(..., min_length=1)
    age_group: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = Field(None, pattern="^(male|female|other)$")
    language: str = Field(default="en", pattern="^(en|hi|hinglish)$")
    model: Optional[str] = "ddxplus"


class TriagePredictionResponse(BaseModel):
    differentials: List[Dict[str, Any]]
    input_symptoms: List[str]
    model: str
    disclaimer: str


class DDxPlusRequest(BaseModel):
    symptoms: List[str] = Field(..., min_length=1)
    age: Optional[int] = Field(None, ge=0, le=120)
    sex: Optional[str] = Field(None, pattern="^(male|female|other)$")
    top_k: int = Field(default=5, ge=1, le=20)


class DDxPlusResponse(BaseModel):
    differentials: List[Dict[str, Any]]
    input_symptoms: List[str]
    model: str
    disclaimer: str


class GenericPredictRequest(BaseModel):
    model_name: str
    inputs: Dict[str, Any]


class GenericPredictResponse(BaseModel):
    model_name: str
    outputs: Dict[str, Any]


# ===== ML Model Endpoints =====

@router.get("/models", response_model=ModelListResponse)
async def list_models(
    task: Optional[ModelTask] = None,
    current_user = Depends(get_current_user_optional)
):
    """List all registered ML models."""
    models = model_registry.list_models()
    if task:
        models = [m for m in models if m.task == task]
    return ModelListResponse(models=models, total=len(models))


@router.get("/models/{model_name}", response_model=ModelMetadataResponse)
async def get_model_metadata(
    model_name: str,
    current_user = Depends(get_current_user_optional)
):
    """Get metadata for a specific model."""
    metadata = model_registry.get_metadata(model_name)
    if not metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model {model_name} not found"
        )
    return metadata


@router.post("/predict/triage", response_model=TriagePredictionResponse)
async def predict_triage_endpoint(
    request: TriagePredictionRequest,
    current_user = Depends(get_current_user_optional)
):
    """
    Predict triage/differential diagnosis from symptoms.
    Uses DDXPlus if available, falls back to mock.
    """
    try:
        result = await predict_triage(
            symptoms=request.symptoms,
            age_group=request.age_group or "adult",
            language=request.language
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/predict/ddxplus", response_model=DDxPlusResponse)
async def predict_ddxplus(
    request: DDxPlusRequest,
    current_user = Depends(get_current_user_optional)
):
    """
    Run DDXPlus differential diagnosis.
    """
    try:
        ddxplus = DDXPlusInference("./models/ddxplus")
        result = ddxplus.predict_differential(
            symptoms=request.symptoms,
            age=request.age,
            sex=request.sex,
            top_k=request.top_k
        )
        return result
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="DDXPlus model not found. Please ensure model files are in ./models/ddxplus/"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DDXPlus prediction failed: {str(e)}"
        )


@router.post("/predict", response_model=GenericPredictResponse)
async def generic_predict(
    request: GenericPredictRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Generic prediction endpoint for any registered model.
    Requires authentication.
    """
    try:
        result = model_registry.predict(request.model_name, request.inputs)
        return GenericPredictResponse(model_name=request.model_name, outputs=result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/initialize")
async def initialize_models_endpoint(
    models_dir: str = "./models",
    current_user = Depends(get_current_active_user)
):
    """Initialize/reload model registry (admin only)."""
    try:
        initialize_models(models_dir)
        models = model_registry.list_models()
        return {
            "message": "Models initialized successfully",
            "models_loaded": len(models),
            "models": [m.name for m in models]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Initialization failed: {str(e)}"
        )


@router.get("/health")
async def ml_models_health():
    """Health check for ML models service."""
    models = model_registry.list_models()
    loaded_models = list(model_registry.models.keys())
    return {
        "status": "healthy",
        "registered_models": len(models),
        "loaded_models": len(loaded_models),
        "models": [m.name for m in models],
        "torch_available": False,  # Would check dynamically
        "onnx_available": False,
        "transformers_available": False,
    }