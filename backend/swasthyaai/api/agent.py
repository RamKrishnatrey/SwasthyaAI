from fastapi import APIRouter

from backend.swasthyaai.agent.contracts import AgentInput, AgentResponse
from backend.swasthyaai.agent.service import run_healthcare_agent

router = APIRouter()


@router.post("/agent/turn", response_model=AgentResponse)
async def agent_turn(request: AgentInput) -> AgentResponse:
    return await run_healthcare_agent(
        request.session_id,
        request.user_message,
        {
            "language": request.language,
            "location": request.location.model_dump() if request.location else None,
            "external_ai_consent": request.external_ai_consent,
            "task": request.task,
        },
    )
