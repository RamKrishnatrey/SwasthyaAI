# SwasthyaAI TinyFish Router
# Web intelligence powered by TinyFish API - Official Sponsor Integration
# https://www.tinyfish.ai/

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.services.auth import get_current_active_user, get_current_user_optional
from app.services.tinyfish import (
    tinyfish_service,
    TinyFishError,
    TinyFishAuthenticationError,
    TinyFishRateLimitError,
    search_healthcare_web,
    research_health_topic,
    get_drug_info,
    get_condition_info,
    find_providers,
)

router = APIRouter(prefix="/api/tinyfish", tags=["tinyfish"])


# ===== Request/Response Schemas =====

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    max_results: int = Field(default=10, ge=1, le=50)
    source_filter: Optional[List[str]] = None
    recency_days: Optional[int] = Field(None, ge=1, le=3650)


class SearchResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    total_results: int
    search_time_ms: int
    sponsored_by: str = "TinyFish"


class HealthcareSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    max_results: int = Field(default=10, ge=1, le=50)
    recency_days: int = Field(default=365, ge=1, le=3650)


class ResearchRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500)
    depth: str = Field(default="standard", pattern="^(quick|standard|deep)$")
    max_sources: int = Field(default=10, ge=1, le=50)
    focus_areas: Optional[List[str]] = None


class HealthcareResearchRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500)
    condition: Optional[str] = None
    treatment: Optional[str] = None
    population: Optional[str] = None


class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: List[Dict[str, Any]]
    key_findings: List[str]
    confidence: float
    research_time_ms: int
    sponsored_by: str = "TinyFish"


class ExtractRequest(BaseModel):
    url: str = Field(..., pattern=r"^https?://")
    extract_type: str = Field(default="article", pattern="^(article|full|summary)$")


class ExtractResponse(BaseModel):
    url: str
    title: Optional[str]
    content: str
    author: Optional[str]
    published_date: Optional[str]
    word_count: int
    extract_type: str
    sponsored_by: str = "TinyFish"


class DrugInfoRequest(BaseModel):
    drug_name: str = Field(..., min_length=1, max_length=200)
    include_interactions: bool = True
    include_side_effects: bool = True


class ConditionInfoRequest(BaseModel):
    condition: str = Field(..., min_length=1, max_length=200)
    include_symptoms: bool = True
    include_treatments: bool = True
    include_prevention: bool = True


class ProviderSearchRequest(BaseModel):
    location: str = Field(..., min_length=1, max_length=200)
    specialty: Optional[str] = None
    service_type: Optional[str] = None


class GuidelinesRequest(BaseModel):
    condition: str = Field(..., min_length=1, max_length=200)
    guideline_body: Optional[str] = None


class HealthCheckResponse(BaseModel):
    status: str
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str
    sponsored_by: str = "TinyFish"


# ===== TinyFish Endpoints =====

@router.get("/health", response_model=HealthCheckResponse)
async def tinyfish_health_check():
    """Check TinyFish API health status."""
    result = await tinyfish_service.health_check()
    result["sponsored_by"] = "TinyFish"
    return result


@router.post("/search", response_model=SearchResponse)
async def search_web(
    request: SearchRequest,
    current_user = Depends(get_current_user_optional)
):
    """
    Search the web for information using TinyFish.
    Supports optional source filtering and recency filtering.
    """
    try:
        result = await tinyfish_service.search_web(
            query=request.query,
            max_results=request.max_results,
            source_filter=request.source_filter,
            recency_days=request.recency_days,
        )
        result["sponsored_by"] = "TinyFish"
        return result
    except TinyFishAuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TinyFish API not configured. Please contact administrator."
        )
    except TinyFishRateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    except TinyFishError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"TinyFish API error: {e.message}"
        )


@router.post("/search/healthcare", response_model=SearchResponse)
async def search_healthcare(
    request: HealthcareSearchRequest,
    current_user = Depends(get_current_user_optional)
):
    """
    Search trusted healthcare sources (WHO, NIH, CDC, ICMR, etc.)
    """
    try:
        result = await tinyfish_service.search_healthcare_sources(
            query=request.query,
            max_results=request.max_results,
            recency_days=request.recency_days,
        )
        result["sponsored_by"] = "TinyFish"
        return result
    except TinyFishAuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TinyFish API not configured. Please contact administrator."
        )
    except TinyFishRateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    except TinyFishError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"TinyFish API error: {e.message}"
        )


@router.post("/research", response_model=ResearchResponse)
async def research_topic(
    request: ResearchRequest,
    current_user = Depends(get_current_user_optional)
):
    """
    Conduct multi-step research on a topic using TinyFish's agent.
    """
    try:
        result = await tinyfish_service.research_topic(
            topic=request.topic,
            depth=request.depth,
            max_sources=request.max_sources,
            focus_areas=request.focus_areas,
        )
        result["sponsored_by"] = "TinyFish"
        return result
    except TinyFishAuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TinyFish API not configured. Please contact administrator."
        )
    except TinyFishRateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    except TinyFishError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"TinyFish API error: {e.message}"
        )


@router.post("/research/healthcare", response_model=ResearchResponse)
async def research_healthcare(
    request: HealthcareResearchRequest,
    current_user = Depends(get_current_user_optional)
):
    """
    Research a healthcare topic with structured medical parameters.
    """
    try:
        result = await tinyfish_service.research_healthcare_topic(
            topic=request.topic,
            condition=request.condition,
            treatment=request.treatment,
            population=request.population,
        )
        result["sponsored_by"] = "TinyFish"
        return result
    except TinyFishAuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TinyFish API not configured. Please contact administrator."
        )
    except TinyFishRateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    except TinyFishError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"TinyFish API error: {e.message}"
        )


@router.post("/extract", response_model=ExtractResponse)
async def extract_content(
    request: ExtractRequest,
    current_user = Depends(get_current_user_optional)
):
    """
    Extract content from a web page.
    """
    try:
        result = await tinyfish_service.extract_content(
            url=request.url,
            extract_type=request.extract_type,
        )
        result["sponsored_by"] = "TinyFish"
        return result
    except TinyFishAuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TinyFish API not configured. Please contact administrator."
        )
    except TinyFishRateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    except TinyFishError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"TinyFish API error: {e.message}"
        )


@router.post("/drug-info", response_model=ResearchResponse)
async def drug_information(
    request: DrugInfoRequest,
    current_user = Depends(get_current_user_optional)
):
    """
    Get comprehensive drug information including interactions and side effects.
    """
    try:
        result = await tinyfish_service.get_drug_information(
            drug_name=request.drug_name,
            include_interactions=request.include_interactions,
            include_side_effects=request.include_side_effects,
        )
        result["sponsored_by"] = "TinyFish"
        return result
    except TinyFishAuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TinyFish API not configured. Please contact administrator."
        )
    except TinyFishRateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    except TinyFishError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"TinyFish API error: {e.message}"
        )


@router.post("/condition-info", response_model=ResearchResponse)
async def condition_information(
    request: ConditionInfoRequest,
    current_user = Depends(get_current_user_optional)
):
    """
    Get comprehensive medical condition information.
    """
    try:
        result = await tinyfish_service.get_condition_information(
            condition=request.condition,
            include_symptoms=request.include_symptoms,
            include_treatments=request.include_treatments,
            include_prevention=request.include_prevention,
        )
        result["sponsored_by"] = "TinyFish"
        return result
    except TinyFishAuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TinyFish API not configured. Please contact administrator."
        )
    except TinyFishRateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    except TinyFishError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"TinyFish API error: {e.message}"
        )


@router.post("/treatment-guidelines", response_model=SearchResponse)
async def treatment_guidelines(
    request: GuidelinesRequest,
    current_user = Depends(get_current_user_optional)
):
    """
    Get treatment guidelines for a medical condition.
    """
    try:
        result = await tinyfish_service.get_treatment_guidelines(
            condition=request.condition,
            guideline_body=request.guideline_body,
        )
        result["sponsored_by"] = "TinyFish"
        return result
    except TinyFishAuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TinyFish API not configured. Please contact administrator."
        )
    except TinyFishRateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    except TinyFishError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"TinyFish API error: {e.message}"
        )


@router.post("/find-providers", response_model=SearchResponse)
async def find_healthcare_providers(
    request: ProviderSearchRequest,
    current_user = Depends(get_current_user_optional)
):
    """
    Find healthcare providers in a location.
    """
    try:
        result = await tinyfish_service.find_healthcare_providers(
            location=request.location,
            specialty=request.specialty,
            service_type=request.service_type,
        )
        result["sponsored_by"] = "TinyFish"
        return result
    except TinyFishAuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TinyFish API not configured. Please contact administrator."
        )
    except TinyFishRateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    except TinyFishError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"TinyFish API error: {e.message}"
        )


# ===== Convenience Endpoints for AI Assistant Integration =====

@router.get("/quick-search")
async def quick_search(
    q: str = Query(..., min_length=1, max_length=500),
    max_results: int = Query(5, ge=1, le=20),
    current_user = Depends(get_current_user_optional)
):
    """Quick healthcare search for AI assistant integration."""
    try:
        result = await search_healthcare_web(q, max_results)
        return {
            "query": q,
            "results": result.get("results", [])[:max_results],
            "sponsored_by": "TinyFish",
        }
    except Exception as e:
        return {
            "query": q,
            "results": [],
            "error": str(e),
            "sponsored_by": "TinyFish",
        }


@router.get("/quick-drug-info")
async def quick_drug_info(
    drug: str = Query(..., min_length=1, max_length=200),
    current_user = Depends(get_current_user_optional)
):
    """Quick drug info for AI assistant integration."""
    try:
        result = await get_drug_info(drug)
        return {
            "drug": drug,
            "summary": result.get("summary", ""),
            "sources": result.get("sources", [])[:3],
            "sponsored_by": "TinyFish",
        }
    except Exception as e:
        return {
            "drug": drug,
            "summary": "",
            "sources": [],
            "error": str(e),
            "sponsored_by": "TinyFish",
        }


@router.get("/quick-condition-info")
async def quick_condition_info(
    condition: str = Query(..., min_length=1, max_length=200),
    current_user = Depends(get_current_user_optional)
):
    """Quick condition info for AI assistant integration."""
    try:
        result = await get_condition_info(condition)
        return {
            "condition": condition,
            "summary": result.get("summary", ""),
            "sources": result.get("sources", [])[:3],
            "sponsored_by": "TinyFish",
        }
    except Exception as e:
        return {
            "condition": condition,
            "summary": "",
            "sources": [],
            "error": str(e),
            "sponsored_by": "TinyFish",
        }