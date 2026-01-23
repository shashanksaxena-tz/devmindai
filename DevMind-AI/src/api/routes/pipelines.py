"""Pipeline generation API endpoints."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.core.auth import get_current_user
from src.agents.pipeline_generator.agent import PipelineGeneratorAgent
from src.core.llm import get_claude_client

router = APIRouter(tags=["pipelines"])


class GeneratePipelineRequest(BaseModel):
    """Request to generate CI/CD pipeline."""
    files: dict[str, str] = Field(..., description="Project files content map")
    platform: str = Field(default="github_actions", description="Target CI/CD platform")


class GeneratePipelineResponse(BaseModel):
    """Response with generated pipeline."""
    analysis: dict[str, Any]
    pipeline: dict[str, str]
    optimization: dict[str, Any]


@router.post("/generate", response_model=GeneratePipelineResponse)
async def generate_pipeline(
    request: GeneratePipelineRequest,
    user: dict = Depends(get_current_user),
):
    """Generate CI/CD pipeline for project."""
    agent = PipelineGeneratorAgent(llm_client=get_claude_client())

    from src.agents.base import AgentContext
    context = AgentContext(
        repository_id="inline",
        user_id=user.get("id"),
    )

    result = await agent.execute(
        context,
        files=request.files,
        platform=request.platform,
    )

    return GeneratePipelineResponse(
        analysis=result["analysis"],
        pipeline=result["pipeline"],
        optimization=result["optimization"],
    )
