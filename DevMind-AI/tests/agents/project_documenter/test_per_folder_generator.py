"""Tests for PerFolderGenerator."""

from pathlib import Path
import pytest
from unittest.mock import Mock, AsyncMock
from src.agents.project_documenter.per_folder_generator import PerFolderGenerator
from src.agents.project_documenter.folder_analyzer import FolderInfo


class MockCodebaseProfile:
    """Mock CodebaseProfile for testing."""
    def __init__(self, name="TestProject", primary_language="python"):
        self.name = name
        self.primary_language = primary_language


@pytest.mark.asyncio
async def test_per_folder_generator_creates_ai_context(tmp_path):
    """Test that PerFolderGenerator generates AI-CONTEXT.md."""
    # Create test folder structure
    agents_path = tmp_path / "src" / "agents"
    agents_path.mkdir(parents=True)
    (agents_path / "agent.py").write_text("class Agent: pass")
    (agents_path / "__init__.py").write_text("")
    
    # Mock LLM client
    llm_client = Mock()
    llm_client.generate = AsyncMock(return_value="## Purpose\nTest purpose content\n\n## Key Files\n- file.py")

    generator = PerFolderGenerator(llm_client)

    folder_info = FolderInfo(
        path=agents_path,
        relative_path=Path("src/agents"),
        score=15,
        file_count=2,
        has_subfolders=False,
        primary_language="python",
    )

    profile = MockCodebaseProfile()

    result = await generator.generate_ai_context(folder_info, profile)

    assert result.path == "src/agents/AI-CONTEXT.md"
    assert "AUTO-GENERATED" in result.content
    assert "CUSTOM SECTION" in result.content
    assert "agents - AI Context" in result.content


@pytest.mark.asyncio
async def test_per_folder_generator_creates_readme(tmp_path):
    """Test that PerFolderGenerator generates README.md."""
    # Create test folder structure
    api_path = tmp_path / "src" / "api"
    api_path.mkdir(parents=True)
    (api_path / "main.py").write_text("def api_handler(): pass")
    
    llm_client = Mock()
    llm_client.generate = AsyncMock(return_value="## Overview\nTest overview content\n\n## Key Components\n- Component 1")

    generator = PerFolderGenerator(llm_client)

    folder_info = FolderInfo(
        path=api_path,
        relative_path=Path("src/api"),
        score=12,
        file_count=1,
        has_subfolders=False,
        primary_language="python",
    )

    profile = MockCodebaseProfile()

    result = await generator.generate_readme(folder_info, profile)

    assert result.path == "src/api/README.md"
    assert "Overview" in result.content
    assert "AUTO-GENERATED" in result.content


@pytest.mark.asyncio
async def test_per_folder_generator_handles_llm_error(tmp_path):
    """Test graceful handling of LLM errors."""
    # Create test folder
    src_path = tmp_path / "src"
    src_path.mkdir()
    (src_path / "main.py").write_text("print('hello')")
    
    llm_client = Mock()
    llm_client.generate = AsyncMock(side_effect=Exception("LLM Error"))

    generator = PerFolderGenerator(llm_client)

    folder_info = FolderInfo(
        path=src_path,
        relative_path=Path("src"),
        score=10,
        file_count=1,
        has_subfolders=False,
        primary_language="python",
    )

    profile = MockCodebaseProfile()

    # Should not raise
    result = await generator.generate_ai_context(folder_info, profile)
    
    # Should still generate template with defaults
    assert "AI-CONTEXT.md" in result.path
    assert "Purpose" in result.content


def test_per_folder_generator_extract_section():
    """Test section extraction from LLM response."""
    llm_client = Mock()
    generator = PerFolderGenerator(llm_client)

    content = """
## Purpose
This is the purpose content.
It spans multiple lines.

## Key Files
- file1.py - Main file
- file2.py - Utils

## Other Section
Other content
"""

    purpose = generator._extract_section(content, "Purpose")
    assert purpose is not None
    assert "This is the purpose content" in purpose
    
    files = generator._extract_section(content, "Key Files")
    assert files is not None
    assert "file1.py" in files
    
    # Non-existent section
    missing = generator._extract_section(content, "Nonexistent")
    assert missing is None


def test_per_folder_generator_format_file_list():
    """Test file list formatting for prompts."""
    llm_client = Mock()
    generator = PerFolderGenerator(llm_client)

    files = [
        {"name": "main.py", "preview": "import os\nprint('hello')\n", "line_count": 50},
        {"name": "utils.py", "preview": "def helper():\n    pass", "line_count": 20},
    ]

    result = generator._format_file_list(files)

    assert "main.py" in result
    assert "utils.py" in result
    assert "50 lines" in result
    assert "import os" in result


def test_per_folder_generator_analyze_folder_contents(tmp_path):
    """Test folder content analysis."""
    # Create test folder
    (tmp_path / "main.py").write_text("print('hello')\nprint('world')")
    (tmp_path / "utils.py").write_text("def helper(): pass")
    (tmp_path / "readme.txt").write_text("Not source code")

    llm_client = Mock()
    generator = PerFolderGenerator(llm_client)

    result = generator._analyze_folder_contents(tmp_path)

    assert result["file_count"] == 2  # Only .py files
    assert len(result["files"]) == 2
    file_names = [f["name"] for f in result["files"]]
    assert "main.py" in file_names
    assert "utils.py" in file_names
    assert "readme.txt" not in file_names


@pytest.mark.asyncio
async def test_per_folder_generator_with_real_folder(tmp_path):
    """Test generation with actual folder contents."""
    # Create test folder
    (tmp_path / "main.py").write_text("""
class MyClass:
    '''A sample class.'''
    def __init__(self):
        self.value = 0
    
    def process(self):
        return self.value * 2
""")

    llm_client = Mock()
    llm_client.generate = AsyncMock(return_value="""
## Purpose
This module provides the MyClass implementation.

## Key Files
- main.py - Core class implementation

## Coding Conventions
- Use type hints
- Follow PEP 8
""")

    generator = PerFolderGenerator(llm_client)

    folder_info = FolderInfo(
        path=tmp_path,
        relative_path=Path("mymodule"),
        score=10,
        file_count=1,
        has_subfolders=False,
        primary_language="python",
    )

    profile = MockCodebaseProfile()

    result = await generator.generate_ai_context(folder_info, profile)

    assert "mymodule/AI-CONTEXT.md" in result.path
    assert "AUTO-GENERATED: Purpose" in result.content
    assert "CUSTOM SECTION" in result.content


def test_per_folder_generator_generate_key_files_section():
    """Test key files section generation from folder contents."""
    llm_client = Mock()
    generator = PerFolderGenerator(llm_client)

    contents = {
        "files": [
            {"name": "main.py", "preview": "", "line_count": 100},
            {"name": "utils.py", "preview": "", "line_count": 50},
        ],
        "file_count": 2,
    }

    result = generator._generate_key_files_section(contents)

    assert "## Key Files" in result
    assert "`main.py`" in result
    assert "`utils.py`" in result


def test_per_folder_generator_generate_components_section():
    """Test components section generation from folder contents."""
    llm_client = Mock()
    generator = PerFolderGenerator(llm_client)

    contents = {
        "files": [
            {"name": "handler.py", "preview": "", "line_count": 100},
            {"name": "service.ts", "preview": "", "line_count": 50},
        ],
        "file_count": 2,
    }

    result = generator._generate_components_section(contents)

    assert "## Key Components" in result
    assert "**handler**" in result
    assert "**service**" in result
