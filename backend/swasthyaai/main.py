from fastapi import FastAPI

from backend.swasthyaai.api.agent import router as agent_router
from backend.swasthyaai.api.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(title="SwasthyaAI", version="0.1.0")
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(agent_router, prefix="/api/v1")
    return app


app = create_app()
