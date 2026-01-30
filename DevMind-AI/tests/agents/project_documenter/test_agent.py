"""Tests for ProjectDocumenterAgent."""

import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents.base import AgentContext
from src.agents.project_documenter import ProjectDocumenterAgent


class TestProjectDocumenterAgent:
    """Test suite for ProjectDocumenterAgent."""

    @pytest.fixture
    def agent(self):
        """Create an agent instance with mocked LLM."""
        with patch("src.agents.project_documenter.agent.get_llm_router") as mock_router:
            mock_client = MagicMock()
            mock_client.generate = AsyncMock(return_value="Generated content")
            mock_router.return_value.get_client.return_value = mock_client

            agent = ProjectDocumenterAgent()
            return agent

    @pytest.fixture
    def mock_project(self, tmp_path):
        """Create a minimal mock project."""
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text(
            """
def hello():
    return "Hello, World!"
"""
        )
        (tmp_path / "pyproject.toml").write_text(
            """
[project]
name = "mock-project"
version = "0.1.0"
"""
        )
        (tmp_path / "README.md").write_text("# Mock Project\n\nA test project.")
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "HEAD").write_text("ref: refs/heads/main")

        return tmp_path

    def test_agent_attributes(self, agent):
        """Agent should have correct attributes."""
        assert agent.name == "project_documenter"
        assert "documentation" in agent.description.lower()

    def test_available_formats(self, agent):
        """Should return all available formats."""
        formats = agent.get_available_formats()

        assert "claude" in formats
        assert "copilot" in formats
        assert "cursor" in formats
        assert "gemini" in formats
        assert "windsurf" in formats
        assert "speckit" in formats
        assert "human" in formats

    def test_format_descriptions(self, agent):
        """Should return descriptions for formats."""
        desc = agent.get_format_description("claude")
        assert "claude" in desc.lower()

        desc = agent.get_format_description("copilot")
        assert "copilot" in desc.lower()

    @pytest.mark.asyncio
    async def test_execute_without_path(self, agent):
        """Should return error when path is missing."""
        context = AgentContext()
        result = await agent.execute(context)

        assert "error" in result
        assert "path" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_execute_with_nonexistent_path(self, agent):
        """Should return error for nonexistent path."""
        context = AgentContext()
        result = await agent.execute(context, path="/nonexistent/path/12345")

        assert "error" in result
        assert "does not exist" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_with_invalid_format(self, agent, mock_project):
        """Should return error for invalid format."""
        context = AgentContext()
        result = await agent.execute(
            context,
            path=str(mock_project),
            formats=["invalid_format"],
        )

        assert "error" in result
        assert "invalid" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_execute_generates_docs(self, agent, mock_project):
        """Should generate documentation for specified formats."""
        context = AgentContext()
        result = await agent.execute(
            context,
            path=str(mock_project),
            formats=["claude", "copilot"],
        )

        assert result.get("success") is True
        assert "generated_docs" in result
        assert len(result["generated_docs"]) > 0

        # Check that requested formats are in the output
        formats_generated = result.get("formats_generated", [])
        assert "claude" in formats_generated
        assert "copilot" in formats_generated

    @pytest.mark.asyncio
    async def test_execute_returns_profile(self, agent, mock_project):
        """Should return analyzed profile."""
        context = AgentContext()
        result = await agent.execute(
            context,
            path=str(mock_project),
            formats=["claude"],
        )

        assert "profile" in result
        profile = result["profile"]
        assert profile["name"] == mock_project.name
        assert profile["primary_language"] == "python"

    @pytest.mark.asyncio
    async def test_execute_with_write_files(self, agent, mock_project):
        """Should write files when requested."""
        context = AgentContext()
        result = await agent.execute(
            context,
            path=str(mock_project),
            formats=["claude"],
            write_files=True,
        )

        assert result.get("success") is True
        assert "written_files" in result

        # Check that CLAUDE.md was written
        claude_md = mock_project / "CLAUDE.md"
        assert claude_md.exists()

    @pytest.mark.asyncio
    async def test_execute_include_human(self, agent, mock_project):
        """Should include human docs when requested."""
        context = AgentContext()
        result = await agent.execute(
            context,
            path=str(mock_project),
            formats=["claude"],
            include_human=True,
        )

        formats_generated = result.get("formats_generated", [])
        assert "human" in formats_generated

    @pytest.mark.asyncio
    async def test_execute_include_speckit(self, agent, mock_project):
        """Should include speckit when requested."""
        context = AgentContext()
        result = await agent.execute(
            context,
            path=str(mock_project),
            formats=["claude"],
            include_speckit=True,
        )

        formats_generated = result.get("formats_generated", [])
        assert "speckit" in formats_generated

    @pytest.mark.asyncio
    async def test_execute_all_formats(self, agent, mock_project):
        """Should generate all formats when requested."""
        context = AgentContext()
        result = await agent.execute(
            context,
            path=str(mock_project),
            all_formats=True,
        )

        formats_generated = result.get("formats_generated", [])
        for fmt in agent.AVAILABLE_FORMATS:
            assert fmt in formats_generated

    @pytest.mark.asyncio
    async def test_analyze_only(self, agent, mock_project):
        """Should analyze codebase without generating docs."""
        profile = await agent.analyze_only(str(mock_project))

        assert profile.name == mock_project.name
        assert profile.primary_language == "python"

    @pytest.mark.asyncio
    async def test_generate_format(self, agent, mock_project):
        """Should generate docs for a specific format."""
        profile = await agent.analyze_only(str(mock_project))
        docs = await agent.generate_format(profile, "claude")

        assert len(docs) > 0
        assert docs[0].format_name == "claude"
        assert docs[0].path == "CLAUDE.md"

    @pytest.mark.asyncio
    async def test_generate_format_invalid(self, agent, mock_project):
        """Should raise error for invalid format."""
        profile = await agent.analyze_only(str(mock_project))

        with pytest.raises(ValueError, match="Unknown format"):
            await agent.generate_format(profile, "invalid_format")


class TestGeneratedDocuments:
    """Tests for generated documentation content."""

    @pytest.fixture
    def agent(self):
        """Create an agent with mocked LLM."""
        with patch("src.agents.project_documenter.agent.get_llm_router") as mock_router:
            mock_client = MagicMock()
            mock_client.generate = AsyncMock(return_value="- Guideline 1\n- Guideline 2")
            mock_router.return_value.get_client.return_value = mock_client

            return ProjectDocumenterAgent()

    @pytest.fixture
    def fastapi_project(self, tmp_path):
        """Create a FastAPI project mock."""
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "api").mkdir()
        (tmp_path / "src" / "api" / "routes.py").write_text(
            """
from fastapi import APIRouter

router = APIRouter()

@router.get("/users")
async def get_users():
    return []
"""
        )
        (tmp_path / "src" / "main.py").write_text(
            """
from fastapi import FastAPI

app = FastAPI()
"""
        )
        (tmp_path / "tests").mkdir()
        (tmp_path / "pyproject.toml").write_text(
            """
[project]
name = "fastapi-project"
version = "1.0.0"

[project.dependencies]
fastapi = ">=0.100.0"

[tool.pytest.ini_options]
testpaths = ["tests"]
"""
        )
        (tmp_path / "README.md").write_text("# FastAPI Project\n\nA REST API.")
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "HEAD").write_text("ref: refs/heads/main")

        return tmp_path

    @pytest.mark.asyncio
    async def test_claude_md_structure(self, agent, fastapi_project):
        """CLAUDE.md should have proper structure."""
        profile = await agent.analyze_only(str(fastapi_project))
        docs = await agent.generate_format(profile, "claude")

        assert len(docs) == 1
        content = docs[0].content

        # Should have key sections
        assert "# " in content  # Title
        assert "## Tech Stack" in content or "## Commands" in content
        assert "python" in content.lower()

    @pytest.mark.asyncio
    async def test_copilot_instructions_structure(self, agent, fastapi_project):
        """Copilot instructions should have proper structure."""
        profile = await agent.analyze_only(str(fastapi_project))
        docs = await agent.generate_format(profile, "copilot")

        assert len(docs) == 1
        assert docs[0].path == ".github/copilot-instructions.md"
        content = docs[0].content

        assert "Python" in content or "python" in content

    @pytest.mark.asyncio
    async def test_cursor_generates_multiple_files(self, agent, fastapi_project):
        """Cursor should generate multiple .mdc files."""
        profile = await agent.analyze_only(str(fastapi_project))
        docs = await agent.generate_format(profile, "cursor")

        assert len(docs) >= 1  # At least index.mdc
        assert any(doc.path.endswith(".mdc") for doc in docs)
        assert any("index.mdc" in doc.path for doc in docs)

    @pytest.mark.asyncio
    async def test_gemini_md_structure(self, agent, fastapi_project):
        """GEMINI.md should have proper structure."""
        profile = await agent.analyze_only(str(fastapi_project))
        docs = await agent.generate_format(profile, "gemini")

        main_doc = next((d for d in docs if d.path == "GEMINI.md"), None)
        assert main_doc is not None
        assert "python" in main_doc.content.lower()

    @pytest.mark.asyncio
    async def test_windsurf_generates_rules(self, agent, fastapi_project):
        """Windsurf should generate rules files."""
        profile = await agent.analyze_only(str(fastapi_project))
        docs = await agent.generate_format(profile, "windsurf")

        assert any(".windsurfrules.md" in doc.path for doc in docs)
        assert any(".windsurf/rules" in doc.path for doc in docs)

    @pytest.mark.asyncio
    async def test_speckit_generates_constitution(self, agent, fastapi_project):
        """Spec Kit should generate constitution file."""
        profile = await agent.analyze_only(str(fastapi_project))
        docs = await agent.generate_format(profile, "speckit")

        constitution = next(
            (d for d in docs if "constitution.md" in d.path),
            None
        )
        assert constitution is not None
        assert "Article" in constitution.content  # Should have articles

    @pytest.mark.asyncio
    async def test_human_generates_docs(self, agent, fastapi_project):
        """Human format should generate documentation files."""
        profile = await agent.analyze_only(str(fastapi_project))
        docs = await agent.generate_format(profile, "human")

        paths = [d.path for d in docs]
        assert any("README" in p for p in paths)
        assert any("ARCHITECTURE" in p for p in paths)
        assert any("CONTRIBUTING" in p for p in paths)
