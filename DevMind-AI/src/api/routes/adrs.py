from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

from src.agents.adr_recorder.agent import ADRRecorderAgent
from src.agents.base import AgentContext
from src.core.auth import get_current_user

router = APIRouter()

class Message(BaseModel):
    author: str
    content: str

class CaptureRequest(BaseModel):
    messages: List[Message]
    source: str = "manual"
    next_adr_number: int = 1

class SearchRequest(BaseModel):
    query: str

@router.post("/capture")
async def capture_decisions(
    request: CaptureRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Capture decisions from conversation and generate ADRs.
    """
    agent = ADRRecorderAgent()
    context = AgentContext(
        user_id=current_user.get("id")
    )

    # Convert messages to dicts
    messages_dicts = [m.model_dump() for m in request.messages]

    result = await agent.execute(
        context,
        action="capture",
        messages=messages_dicts,
        source=request.source,
        next_adr_number=request.next_adr_number
    )

    if "error" in result:
         raise HTTPException(status_code=400, detail=result["error"])

    return result

@router.post("/search")
async def search_adrs(
    request: SearchRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Search for existing ADRs.
    """
    agent = ADRRecorderAgent()
    context = AgentContext(
        user_id=current_user.get("id")
    )

    result = await agent.execute(
        context,
        action="search",
        query=request.query
    )

    if "error" in result:
         raise HTTPException(status_code=400, detail=result["error"])

    return result
