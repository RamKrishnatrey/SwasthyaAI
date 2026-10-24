# SwasthyaAI Backend - FastAPI Application Factory

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.schemas import HealthResponse
from app.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (if needed)


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="SwasthyaAI Backend",
        description="AI care navigation for India - multilingual, safe, explainable decision support",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS for Vite dev server
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers (will be added incrementally)
    from app.routers import health, intake, triage, matching, auth, conversations, appointments, medical_records, reminders, tinyfish, ml_models, agent_bridge
    app.include_router(health.router)
    app.include_router(intake.router)
    app.include_router(triage.router)
    app.include_router(matching.router)
    app.include_router(auth.router)
    app.include_router(conversations.router)
    app.include_router(appointments.router)
    app.include_router(medical_records.router)
    app.include_router(reminders.router)
    app.include_router(tinyfish.router)
    app.include_router(ml_models.router)
    app.include_router(agent_bridge.router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
    )