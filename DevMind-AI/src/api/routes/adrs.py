# src/api/routes/adrs.py
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from qdrant_client import AsyncQdrantClient

from src.core.llm import get_llm_client
from src.core.config import settings
from src.agents.adr_recorder.agent import ADRRecorderAgent
from src.agents.base import AgentContext

router = APIRouter()

class ConversationMessage(BaseModel):
    author: str
    content: str

class CaptureRequest(BaseModel):
    messages: list[ConversationMessage]
    source: str = "manual"
    next_adr_number: int = 1

class SearchRequest(BaseModel):
    query: str

async def get_qdrant_client() -> AsyncQdrantClient:
    """Dependency to get Qdrant client."""
    return AsyncQdrantClient(url=settings.QDRANT_URL)

@router.post("/capture")
async def capture_decisions(
    request: CaptureRequest,
    llm_client: Any = Depends(get_llm_client),
    qdrant_client: AsyncQdrantClient = Depends(get_qdrant_client),
):
    """Capture decisions from a conversation and generate ADRs."""
    # Note: We need an embedding client too. In a real app, this would be injected.
    # For now, we will assume llm_client can also embed or pass None if not supported.
    # To fix properly, we need get_embedding_client dependency.
    embedding_client = None
    if hasattr(llm_client, "embed"):
        embedding_client = llm_client

    agent = ADRRecorderAgent(llm_client, qdrant_client, embedding_client)

    context = AgentContext(
        repository_id="global", # ADRs might be global or repo-specific
        pr_number=None,
        files=[]
    )

    result = await agent.execute(
        context,
        action="capture",
        messages=[m.dict() for m in request.messages],
        source=request.source,
        next_adr_number=request.next_adr_number
    )

    return result

@router.post("/search")
async def search_adrs(
    request: SearchRequest,
    llm_client: Any = Depends(get_llm_client),
    qdrant_client: AsyncQdrantClient = Depends(get_qdrant_client),
):
    """Search for existing ADRs."""
    embedding_client = None
    if hasattr(llm_client, "embed"):
        embedding_client = llm_client

    agent = ADRRecorderAgent(llm_client, qdrant_client, embedding_client)
    context = AgentContext(repository_id="global", pr_number=None, files=[])

    if not embedding_client:
        # Fallback or error if no embedding capability
        # Ideally we inject a dedicated embedding client
        return {"error": "Embedding client not configured"}

    result = await agent.execute(
        context,
        action="search",
        query=request.query
    )
    return result
