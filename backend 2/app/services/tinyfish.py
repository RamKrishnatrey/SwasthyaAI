# SwasthyaAI TinyFish Integration Service
# Web intelligence powered by TinyFish API
# Official sponsor integration - https://www.tinyfish.ai/

import httpx
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# TinyFish API Configuration
TINYFISH_BASE_URL = settings.tinyfish_base_url
TINYFISH_API_KEY = settings.tinyfish_api_key

# Default headers for TinyFish API
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "SwasthyaAI/1.0 (Healthcare Navigation Platform)",
}


class TinyFishError(Exception):
    """Base exception for TinyFish API errors."""
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(message)


class TinyFishAuthenticationError(TinyFishError):
    """TinyFish authentication error."""
    pass


class TinyFishRateLimitError(TinyFishError):
    """TinyFish rate limit exceeded."""
    pass


class TinyFishService:
    """Service for interacting with TinyFish API."""

    def __init__(self):
        self.base_url = TINYFISH_BASE_URL
        self.api_key = TINYFISH_API_KEY
        self.client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self.client is None or self.client.is_closed:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(30.0, connect=10.0),
                headers={**DEFAULT_HEADERS, "Authorization": f"Bearer {self.api_key}"} if self.api_key else DEFAULT_HEADERS,
            )
        return self.client

    async def close(self):
        """Close HTTP client."""
        if self.client and not self.client.is_closed:
            await self.client.aclose()

    def _handle_error(self, response: httpx.Response) -> None:
        """Handle API error responses."""
        try:
            error_data = response.json()
            error_message = error_data.get("error", error_data.get("message", "Unknown error"))
        except:
            error_message = response.text or "Unknown error"

        if response.status_code == 401:
            raise TinyFishAuthenticationError(f"Authentication failed: {error_message}", response.status_code)
        elif response.status_code == 429:
            raise TinyFishRateLimitError(f"Rate limit exceeded: {error_message}", response.status_code)
        elif response.status_code >= 500:
            raise TinyFishError(f"Server error: {error_message}", response.status_code)
        else:
            raise TinyFishError(f"API error: {error_message}", response.status_code)

    # ===== Search Capabilities =====

    async def search_web(
        self,
        query: str,
        max_results: int = 10,
        source_filter: Optional[List[str]] = None,
        recency_days: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Search the web for healthcare information.

        Args:
            query: Search query string
            max_results: Maximum number of results (default 10)
            source_filter: List of preferred domains (e.g., ["who.int", "nih.gov"])
            recency_days: Filter results to last N days
        """
        if not self.api_key:
            raise TinyFishAuthenticationError("TinyFish API key not configured")

        client = await self._get_client()

        payload = {
            "query": query,
            "max_results": max_results,
        }

        if source_filter:
            payload["source_filter"] = source_filter
        if recency_days:
            payload["recency_days"] = recency_days

        try:
            response = await client.post("/v1/search", json=payload)
            if response.status_code != 200:
                self._handle_error(response)
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"TinyFish search request failed: {e}")
            raise TinyFishError(f"Request failed: {str(e)}")

    async def search_healthcare_sources(
        self,
        query: str,
        max_results: int = 10,
        recency_days: int = 365,
    ) -> Dict[str, Any]:
        """
        Search specifically trusted healthcare sources.
        """
        trusted_sources = [
            "who.int",
            "nih.gov",
            "cdc.gov",
            "fda.gov",
            "ema.europa.eu",
            "icmr.gov.in",
            "mohfw.gov.in",
            "nhp.gov.in",
            "pmc.ncbi.nlm.nih.gov",
            "pubmed.ncbi.nlm.nih.gov",
            "cochrane.org",
            "bmj.com",
            "thelancet.com",
            "nejm.org",
            "jamanetwork.com",
            "nature.com",
            "sciencedirect.com",
            "springer.com",
            "wiley.com",
            "medscape.com",
            "webmd.com",
            "mayoclinic.org",
            "clevelandclinic.org",
            "hopkinsmedicine.org",
        ]

        return await self.search_web(
            query=query,
            max_results=max_results,
            source_filter=trusted_sources,
            recency_days=recency_days,
        )

    # ===== Content Extraction =====

    async def extract_content(
        self,
        url: str,
        extract_type: str = "article",  # article, full, summary
    ) -> Dict[str, Any]:
        """
        Extract content from a web page.

        Args:
            url: URL to extract content from
            extract_type: Type of extraction (article, full, summary)
        """
        if not self.api_key:
            raise TinyFishAuthenticationError("TinyFish API key not configured")

        client = await self._get_client()

        payload = {
            "url": url,
            "extract_type": extract_type,
        }

        try:
            response = await client.post("/v1/extract", json=payload)
            if response.status_code != 200:
                self._handle_error(response)
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"TinyFish extract request failed: {e}")
            raise TinyFishError(f"Request failed: {str(e)}")

    # ===== Research Agent =====

    async def research_topic(
        self,
        topic: str,
        depth: str = "standard",  # quick, standard, deep
        max_sources: int = 10,
        focus_areas: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Conduct multi-step research on a topic using TinyFish's agent.

        Args:
            topic: Research topic
            depth: Research depth (quick, standard, deep)
            max_sources: Maximum sources to consult
            focus_areas: Specific areas to focus on
        """
        if not self.api_key:
            raise TinyFishAuthenticationError("TinyFish API key not configured")

        client = await self._get_client()

        payload = {
            "topic": topic,
            "depth": depth,
            "max_sources": max_sources,
        }

        if focus_areas:
            payload["focus_areas"] = focus_areas

        try:
            response = await client.post("/v1/research", json=payload)
            if response.status_code != 200:
                self._handle_error(response)
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"TinyFish research request failed: {e}")
            raise TinyFishError(f"Request failed: {str(e)}")

    async def research_healthcare_topic(
        self,
        topic: str,
        condition: Optional[str] = None,
        treatment: Optional[str] = None,
        population: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Research a healthcare topic with structured parameters.
        """
        focus_areas = []
        if condition:
            focus_areas.append(f"condition:{condition}")
        if treatment:
            focus_areas.append(f"treatment:{treatment}")
        if population:
            focus_areas.append(f"population:{population}")

        # Add standard healthcare focus areas
        focus_areas.extend([
            "guidelines",
            "clinical_trials",
            "systematic_reviews",
            "meta_analyses",
            "official_recommendations",
        ])

        return await self.research_topic(
            topic=topic,
            depth="standard",
            max_sources=15,
            focus_areas=focus_areas,
        )

    # ===== Structured Data Extraction =====

    async def extract_structured_data(
        self,
        url: str,
        schema: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Extract structured data from a page using a schema.

        Args:
            url: URL to extract from
            schema: JSON schema defining expected structure
        """
        if not self.api_key:
            raise TinyFishAuthenticationError("TinyFish API key not configured")

        client = await self._get_client()

        payload = {
            "url": url,
            "schema": schema,
        }

        try:
            response = await client.post("/v1/extract/structured", json=payload)
            if response.status_code != 200:
                self._handle_error(response)
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"TinyFish structured extract request failed: {e}")
            raise TinyFishError(f"Request failed: {str(e)}")

    # ===== Health-Specific Helpers =====

    async def find_healthcare_providers(
        self,
        location: str,
        specialty: Optional[str] = None,
        service_type: Optional[str] = None,  # hospital, clinic, telehealth, pharmacy
    ) -> Dict[str, Any]:
        """Search for healthcare providers in a location."""
        query_parts = [f"healthcare providers {location}"]
        if specialty:
            query_parts.append(specialty)
        if service_type:
            query_parts.append(service_type)

        query = " ".join(query_parts)

        return await self.search_web(
            query=query,
            max_results=10,
            recency_days=90,
        )

    async def get_drug_information(
        self,
        drug_name: str,
        include_interactions: bool = True,
        include_side_effects: bool = True,
    ) -> Dict[str, Any]:
        """Get comprehensive drug information."""
        focus_areas = ["dosage", "indications", "contraindications"]
        if include_interactions:
            focus_areas.append("interactions")
        if include_side_effects:
            focus_areas.append("side_effects")
        focus_areas.extend(["warnings", "pregnancy_category", "mechanism_of_action"])

        return await self.research_topic(
            topic=f"{drug_name} drug information",
            depth="standard",
            max_sources=10,
            focus_areas=focus_areas,
        )

    async def get_condition_information(
        self,
        condition: str,
        include_symptoms: bool = True,
        include_treatments: bool = True,
        include_prevention: bool = True,
    ) -> Dict[str, Any]:
        """Get comprehensive condition/disease information."""
        focus_areas = []
        if include_symptoms:
            focus_areas.append("symptoms")
        if include_treatments:
            focus_areas.extend(["treatments", "medications", "therapies"])
        if include_prevention:
            focus_areas.append("prevention")
        focus_areas.extend(["diagnosis", "prognosis", "risk_factors", "complications"])

        return await self.research_topic(
            topic=f"{condition} medical condition",
            depth="standard",
            max_sources=15,
            focus_areas=focus_areas,
        )

    async def get_treatment_guidelines(
        self,
        condition: str,
        guideline_body: Optional[str] = None,  # WHO, NICE, AHA, ACC, etc.
    ) -> Dict[str, Any]:
        """Get treatment guidelines for a condition."""
        query = f"{condition} treatment guidelines"
        if guideline_body:
            query += f" {guideline_body}"

        return await self.search_healthcare_sources(
            query=query,
            max_results=10,
            recency_days=730,  # 2 years for guidelines
        )

    # ===== Health Check =====

    async def health_check(self) -> Dict[str, Any]:
        """Check TinyFish API health."""
        if not self.api_key:
            return {
                "status": "not_configured",
                "message": "TinyFish API key not configured",
                "timestamp": datetime.utcnow().isoformat(),
            }

        client = await self._get_client()

        try:
            response = await client.get("/v1/health")
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "details": response.json(),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"API returned {response.status_code}",
                    "timestamp": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }


# Global service instance
tinyfish_service = TinyFishService()


# ===== Convenience Functions =====

async def search_healthcare_web(query: str, max_results: int = 10) -> Dict[str, Any]:
    """Convenience function for healthcare web search."""
    return await tinyfish_service.search_healthcare_sources(query, max_results)


async def research_health_topic(topic: str, **kwargs) -> Dict[str, Any]:
    """Convenience function for healthcare topic research."""
    return await tinyfish_service.research_healthcare_topic(topic, **kwargs)


async def get_drug_info(drug_name: str) -> Dict[str, Any]:
    """Convenience function for drug information."""
    return await tinyfish_service.get_drug_information(drug_name)


async def get_condition_info(condition: str) -> Dict[str, Any]:
    """Convenience function for condition information."""
    return await tinyfish_service.get_condition_information(condition)


async def find_providers(location: str, specialty: str = None) -> Dict[str, Any]:
    """Convenience function for finding providers."""
    return await tinyfish_service.find_healthcare_providers(location, specialty)


# Export
__all__ = [
    "TinyFishService",
    "TinyFishError",
    "TinyFishAuthenticationError",
    "TinyFishRateLimitError",
    "tinyfish_service",
    "search_healthcare_web",
    "research_health_topic",
    "get_drug_info",
    "get_condition_info",
    "find_providers",
]