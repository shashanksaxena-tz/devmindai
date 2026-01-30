"""Project Documentation API endpoints."""
from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from src.core.auth import get_current_user
from src.agents.project_documenter import ProjectDocumenterAgent
from src.agents.base import AgentContext

router = APIRouter(tags=["project-docs"])


class AnalyzeProjectRequest(BaseModel):
    """Request to analyze a project."""

    path: str = Field(..., description="Path to the project to analyze")


class AnalyzeProjectResponse(BaseModel):
    """Response with project analysis."""

    name: str
    root_path: str
    description: str
    primary_language: str
    languages: dict[str, int]
    frameworks: list[str]
    architecture_patterns: list[str]
    api_style: str
    has_git: bool
    default_branch: str
    build_commands: list[str]
    test_commands: list[str]
    lint_commands: list[str]
    code_style: dict[str, Any]
    naming_conventions: dict[str, str]
    existing_docs: list[str]
    file_count: int
    directory_count: int


class GenerateDocsRequest(BaseModel):
    """Request to generate documentation."""

    path: str = Field(..., description="Path to the project")
    formats: list[str] = Field(
        default=["claude", "copilot", "cursor", "gemini", "windsurf"],
        description="Documentation formats to generate",
    )
    write_files: bool = Field(
        default=False,
        description="Whether to write files to disk",
    )
    include_human: bool = Field(
        default=False,
        description="Include human-readable documentation",
    )
    include_speckit: bool = Field(
        default=False,
        description="Include GitHub Spec Kit constitution",
    )


class GeneratedDocInfo(BaseModel):
    """Information about a generated document."""

    path: str
    format: str
    description: str
    content_preview: str


class GenerateDocsResponse(BaseModel):
    """Response with generated documentation."""

    success: bool
    profile: AnalyzeProjectResponse
    generated_docs: list[GeneratedDocInfo]
    written_files: list[str]
    formats_generated: list[str]


class GenerateSingleFormatRequest(BaseModel):
    """Request to generate documentation for a single format."""

    path: str = Field(..., description="Path to the project")
    format: str = Field(..., description="Documentation format to generate")
    write_files: bool = Field(default=False)


class AvailableFormatsResponse(BaseModel):
    """Response with available formats."""

    formats: list[dict[str, str]]


@router.post("/analyze", response_model=AnalyzeProjectResponse)
async def analyze_project(
    request: AnalyzeProjectRequest,
    user: dict = Depends(get_current_user),
):
    """Analyze a project and return its profile.

    This endpoint analyzes a codebase without generating any documentation,
    returning information about:
    - Languages and frameworks used
    - Project structure
    - Build/test/lint commands
    - Code style and naming conventions
    - Existing documentation
    """
    agent = ProjectDocumenterAgent()

    try:
        profile = await agent.analyze_only(request.path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    return AnalyzeProjectResponse(
        name=profile.name,
        root_path=profile.root_path,
        description=profile.description,
        primary_language=profile.primary_language,
        languages=profile.languages,
        frameworks=profile.frameworks,
        architecture_patterns=profile.architecture_patterns,
        api_style=profile.api_style or "",
        has_git=profile.has_git,
        default_branch=profile.default_branch,
        build_commands=profile.build_commands,
        test_commands=profile.test_commands,
        lint_commands=profile.lint_commands,
        code_style=profile.code_style,
        naming_conventions=profile.naming_conventions,
        existing_docs=profile.existing_docs,
        file_count=len(profile.structure.files),
        directory_count=len(profile.structure.directories),
    )


@router.post("/generate", response_model=GenerateDocsResponse)
async def generate_documentation(
    request: GenerateDocsRequest,
    user: dict = Depends(get_current_user),
):
    """Generate AI-agent documentation for a project.

    This endpoint analyzes the project and generates documentation in the
    specified formats. Available formats:

    **AI Agent Formats:**
    - `claude`: CLAUDE.md for Claude Code
    - `copilot`: .github/copilot-instructions.md for GitHub Copilot
    - `cursor`: .cursor/rules/*.mdc for Cursor AI
    - `gemini`: GEMINI.md for Google Gemini Code Assist
    - `windsurf`: .windsurf/rules/*.md for Windsurf/Codeium

    **Additional Formats:**
    - `speckit`: GitHub Spec Kit constitution files
    - `human`: Human-readable docs (README, ARCHITECTURE, CONTRIBUTING)
    """
    agent = ProjectDocumenterAgent()
    context = AgentContext(user_id=user.get("id"))

    # Add optional formats
    formats = list(request.formats)
    if request.include_human and "human" not in formats:
        formats.append("human")
    if request.include_speckit and "speckit" not in formats:
        formats.append("speckit")

    result = await agent.execute(
        context,
        path=request.path,
        formats=formats,
        write_files=request.write_files,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))

    profile_data = result["profile"]

    return GenerateDocsResponse(
        success=True,
        profile=AnalyzeProjectResponse(**profile_data),
        generated_docs=[
            GeneratedDocInfo(
                path=doc["path"],
                format=doc["format"],
                description=doc["description"],
                content_preview=doc["content_preview"],
            )
            for doc in result["generated_docs"]
        ],
        written_files=result.get("written_files", []),
        formats_generated=result.get("formats_generated", []),
    )


@router.post("/generate/{format_name}")
async def generate_single_format(
    format_name: str,
    request: GenerateSingleFormatRequest,
    user: dict = Depends(get_current_user),
):
    """Generate documentation for a specific format only.

    This is a convenience endpoint for generating a single format.
    """
    agent = ProjectDocumenterAgent()
    context = AgentContext(user_id=user.get("id"))

    # Validate format
    available = agent.get_available_formats()
    if format_name not in available:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown format: {format_name}. Available: {available}",
        )

    result = await agent.execute(
        context,
        path=request.path,
        formats=[format_name],
        write_files=request.write_files,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))

    return {
        "format": format_name,
        "generated_docs": result["generated_docs"],
        "written_files": result.get("written_files", []),
    }


@router.get("/formats", response_model=AvailableFormatsResponse)
async def get_available_formats():
    """Get list of available documentation formats.

    Returns all formats that can be generated, with descriptions.
    """
    agent = ProjectDocumenterAgent()
    formats = []

    for format_name in agent.get_available_formats():
        formats.append({
            "name": format_name,
            "description": agent.get_format_description(format_name),
        })

    return AvailableFormatsResponse(formats=formats)


@router.get("/doc/{format_name}/preview")
async def preview_format_content(
    format_name: str,
    path: str,
    user: dict = Depends(get_current_user),
):
    """Preview documentation content for a specific format without writing files.

    Returns the full content of generated documentation files.
    """
    agent = ProjectDocumenterAgent()
    context = AgentContext(user_id=user.get("id"))

    # Validate format
    available = agent.get_available_formats()
    if format_name not in available:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown format: {format_name}. Available: {available}",
        )

    # Analyze and generate
    try:
        profile = await agent.analyze_only(path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    docs = await agent.generate_format(profile, format_name)

    return {
        "format": format_name,
        "files": [
            {
                "path": doc.path,
                "content": doc.content,
                "description": doc.description,
            }
            for doc in docs
        ],
    }
