"""API routes for incident response."""

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.core.auth import get_current_user
from src.db.models.user import User
from src.agents.incident_responder.agent import IncidentResponderAgent
from src.agents.base import AgentContext

router = APIRouter()

@router.post("/webhook/{source}")
async def receive_alert(
    source: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Receive alert webhook from monitoring tools."""
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Run agent in background
    background_tasks.add_task(
        _process_alert,
        source=source,
        payload=payload,
    )

    return {"status": "accepted", "message": "Alert received and processing started"}


async def _process_alert(source: str, payload: Dict[str, Any]):
    """Process alert in background."""
    # Initialize agent
    agent = IncidentResponderAgent()
    context = AgentContext()

    try:
        result = await agent.run(
            context,
            alert_payload=payload,
            source=source
        )
        # In a real app, we would save the result to DB here.
        # For now, just logging (printing)
        print(f"Incident processed: {result}")
    except Exception as e:
        print(f"Error processing incident: {e}")

@router.get("/{incident_id}")
async def get_incident(
    incident_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get incident details."""
    # Placeholder as we haven't implemented DB persistence for incidents yet.
    return {"incident_id": incident_id, "status": "processing"}
