"""API routes for documentation generation."""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.agents.doc_generator.agent import DocGeneratorAgent
from src.core.auth import get_current_user
from src.core.llm import get_llm_router, TaskComplexity
from src.db.models import User

router = APIRouter()


class DocRequest(BaseModel):
    """Request model for documentation generation."""
    code: str
    doc_type: str = "docstring"  # docstring, api, readme
    file_path: str = ""
    repository_id: str = "default"


@router.post("/generate", status_code=status.HTTP_200_OK)
async def generate_docs(
    request: DocRequest,
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Generate documentation from code."""
    llm_router = get_llm_router()
    # Note: DocGeneratorAgent expects an LLMRouter instance (or None to use global default),
    # not a client directly in the corrected architecture.
    agent = DocGeneratorAgent(llm_router)

    # Simplified context since we don't have full repo access in this endpoint yet
    # In a real scenario, we might want to fetch repo details
    from src.agents.base import AgentContext
    context = AgentContext(repository_id=request.repository_id)

    result = await agent.execute(
        context,
        code=request.code,
        file_path=request.file_path,
        doc_type=request.doc_type,
    )

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"],
        )

    return result
