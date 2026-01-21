"""Test generation API endpoints."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from src.core.auth import get_current_user
from src.agents.test_generator.agent import TestGeneratorAgent
from src.core.llm import get_claude_client

router = APIRouter(tags=["tests"])


class GenerateTestsRequest(BaseModel):
    """Request to generate tests."""
    code: str = Field(..., description="Source code to generate tests for")
    file_path: str = Field(..., description="Path to source file")
    framework: str = Field(default="pytest", description="Test framework")
    focus: Optional[str] = Field(
        default=None,
        description="Focus on specific function/class",
    )


class GenerateTestsResponse(BaseModel):
    """Response with generated tests."""
    tests: list[dict[str, Any]]
    test_file_content: str
    test_file_path: str
    functions_analyzed: int
    tests_generated: int


class GenerateFunctionTestsRequest(BaseModel):
    """Request to generate tests for a single function."""
    function_code: str
    function_name: str
    framework: str = "pytest"


class CoverageReportRequest(BaseModel):
    """Request for coverage analysis."""
    repo_id: str
    coverage_xml: Optional[str] = None


@router.post("/generate", response_model=GenerateTestsResponse)
async def generate_tests(
    request: GenerateTestsRequest,
    user: dict = Depends(get_current_user),
):
    """Generate tests for source code."""
    agent = TestGeneratorAgent(llm_client=get_claude_client())

    from src.agents.base import AgentContext
    context = AgentContext(
        repository_id="inline",
        user_id=user.get("id"),
    )

    result = await agent.execute(
        context,
        code=request.code,
        file_path=request.file_path,
        framework=request.framework,
    )

    return GenerateTestsResponse(
        tests=result["tests"],
        test_file_content=result["test_file_content"],
        test_file_path=result["test_file_path"],
        functions_analyzed=result["functions_analyzed"],
        tests_generated=result["tests_generated"],
    )


@router.post("/generate-function")
async def generate_function_tests(
    request: GenerateFunctionTestsRequest,
    user: dict = Depends(get_current_user),
):
    """Generate tests for a single function."""
    agent = TestGeneratorAgent(llm_client=get_claude_client())

    from src.agents.base import AgentContext
    context = AgentContext(
        repository_id="inline",
        user_id=user.get("id"),
    )

    result = await agent.generate_for_function(
        context,
        function_code=request.function_code,
        function_name=request.function_name,
        framework=request.framework,
    )

    return result


@router.get("/repos/{repo_id}/coverage")
async def get_coverage_report(
    repo_id: str,
    user: dict = Depends(get_current_user),
):
    """Get test coverage report for a repository."""
    # TODO: Fetch from database
    return {
        "repo_id": repo_id,
        "overall_coverage": 0.0,
        "files": [],
        "gaps": [],
    }


@router.post("/repos/{repo_id}/generate", status_code=202)
async def trigger_repo_test_generation(
    repo_id: str,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
):
    """Trigger test generation for entire repository."""
    job_id = str(uuid.uuid4())

    # TODO: Queue background job
    background_tasks.add_task(
        _generate_repo_tests,
        job_id=job_id,
        repo_id=repo_id,
    )

    return {
        "job_id": job_id,
        "status": "queued",
        "message": f"Test generation queued for repository {repo_id}",
    }


async def _generate_repo_tests(job_id: str, repo_id: str):
    """Background task to generate tests for a repository."""
    # TODO: Implement full repo scanning and test generation
    pass
