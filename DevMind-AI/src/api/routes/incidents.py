"""Incident Responder API routes."""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from src.core.auth import get_current_user
from src.core.llm import get_llm_router
from src.agents.incident_responder.agent import IncidentResponderAgent
from src.agents.base import AgentContext

router = APIRouter()

@router.post("/process", status_code=200)
async def process_incident(
    payload: dict,
    source: str = "pagerduty",
    current_user: Any = Depends(get_current_user),
) -> dict[str, Any]:
    """Process an incoming incident alert."""
    try:
        # Initialize agent
        llm_router = get_llm_router()
        client = llm_router.get_client("claude")
        agent = IncidentResponderAgent(client)

        context = AgentContext(
            repository_id="incident-response",
            pr_id=None,
            user_id=str(current_user.id) if hasattr(current_user, "id") else "system"
        )

        result = await agent.execute(
            context,
            alert_payload=payload,
            source=source
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook/{source}", status_code=200)
async def webhook_receiver(
    source: str,
    payload: dict,
) -> dict[str, Any]:
    """Webhook endpoint for PagerDuty/Datadog."""
    try:
        # Initialize agent
        llm_router = get_llm_router()
        client = llm_router.get_client("claude")
        agent = IncidentResponderAgent(client)

        context = AgentContext(
            repository_id="webhook",
            pr_id=None,
            user_id="webhook"
        )

        result = await agent.execute(
            context,
            alert_payload=payload,
            source=source
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
