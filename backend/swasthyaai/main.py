from fastapi import FastAPI

from backend.swasthyaai.api.agent import router as agent_router
from backend.swasthyaai.api.appointments import router as appointments_router
from backend.swasthyaai.api.auth import router as auth_router
from backend.swasthyaai.api.clinician import router as clinician_router
from backend.swasthyaai.api.discovery import router as discovery_router
from backend.swasthyaai.api.health import router as health_router
from backend.swasthyaai.api.patient import router as patient_router
from backend.swasthyaai.api.reminders import router as reminders_router


def create_app() -> FastAPI:
    app = FastAPI(title="SwasthyaAI", version="0.1.0")
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(agent_router, prefix="/api/v1")
    for router in (auth_router, patient_router, clinician_router, discovery_router, appointments_router, reminders_router):
        app.include_router(router, prefix="/api/v1")
    return app


app = create_app()
