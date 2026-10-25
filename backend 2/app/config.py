# SwasthyaAI Configuration
# Single source of truth for all configurable values

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        protected_namespaces=("settings_",),
    )

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    environment: str = "development"

    # CORS
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8081,http://127.0.0.1:8081,exp://localhost:8081"

    # Database
    database_url: str = "sqlite:///./swasthyaai.db"

    # Model
    model_path: str = "./models/triage_model"
    model_source: str = "mock"

    # Safety
    safety_escalation_enabled: bool = True

    # Ranking weights (must sum to 1.0)
    weight_skill_fit: float = 0.35
    weight_distance: float = 0.25
    weight_availability: float = 0.20
    weight_language: float = 0.10
    weight_rating: float = 0.10

    # Authentication
    secret_key: str = "your-super-secret-key-change-in-production-min-32-chars"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    refresh_token_expire_days: int = 30

    # Optional OpenAI-compatible conversational model (server-side only)
    llm_api_key: str = ""
    llm_base_url: str = "http://localhost:11434/v1"
    llm_model: str = "qwen2.5:3b"

    # TinyFish API
    tinyfish_api_key: str = ""
    tinyfish_base_url: str = "https://api.tinyfish.ai"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def ranking_weights(self) -> dict[str, float]:
        return {
            "skill_fit": self.weight_skill_fit,
            "distance": self.weight_distance,
            "availability": self.weight_availability,
            "language": self.weight_language,
            "rating": self.weight_rating,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()