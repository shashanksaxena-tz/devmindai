"""End-to-end tests for per-folder documentation generation."""

from pathlib import Path
import pytest
from unittest.mock import Mock, AsyncMock, patch

from src.agents.project_documenter import ProjectDocumenterAgent
from src.agents.base import AgentContext


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    client = Mock()
    client.generate = AsyncMock(return_value="""
## Purpose
This module provides core functionality.

## Key Files
- main.py - Entry point

## Coding Conventions
- Use type hints
- Follow PEP 8

## Common Patterns
Standard patterns used.

## Testing Approach
Run with pytest.

## Integration Points
Imports from core.
""")
    return client


@pytest.fixture
def test_project(tmp_path):
    """Create a test project structure."""
    project = tmp_path / "test_project"
    project.mkdir()

    # Create src/core folder
    (project / "src").mkdir()
    (project / "src" / "core").mkdir()
    (project / "src" / "core" / "__init__.py").write_text("")
    (project / "src" / "core" / "utils.py").write_text("""
def helper_function():
    '''A helper function.'''
    return True
""")

    # Create src/api folder
    (project / "src" / "api").mkdir()
    (project / "src" / "api" / "main.py").write_text("""
def api_handler():
    '''API handler.'''
    pass
""")

    # Create tests folder
    (project / "tests").mkdir()
    (project / "tests" / "test_utils.py").write_text("def test_helper(): pass")

    return project


@pytest.mark.asyncio
async def test_folder_analyzer_integration(test_project):
    """Test FolderAnalyzer finds the expected folders."""
    from src.agents.project_documenter.folder_analyzer import FolderAnalyzer

    analyzer = FolderAnalyzer()
    folders = analyzer.analyze_folders(test_project)

    folder_names = [f.relative_path.name for f in folders]
    
    assert "core" in folder_names
    assert "api" in folder_names
    assert "tests" in folder_names
    assert len(folders) >= 3


@pytest.mark.asyncio
async def test_metadata_manager_integration(test_project):
    """Test MetadataManager tracking workflow."""
    from src.agents.project_documenter.metadata_manager import MetadataManager

    manager = MetadataManager()
    manager.initialize(test_project)

    folder_path = test_project / "src" / "core"

    # Initially changed
    assert manager.has_folder_changed(folder_path) is True

    # Update
    manager.update_folder(folder_path, file_count=2)

    # Not changed
    assert manager.has_folder_changed(folder_path) is False

    # Modify file
    (test_project / "src" / "core" / "utils.py").write_text("# Modified")

    # Now changed
    assert manager.has_folder_changed(folder_path) is True


@pytest.mark.asyncio
async def test_smart_merger_integration():
    """Test SmartMerger preserves custom content."""
    from src.agents.project_documenter.smart_merger import SmartMerger

    existing = """# Module

<!-- AUTO-GENERATED: Purpose - DO NOT EDIT -->
## Purpose
Old purpose
<!-- END AUTO-GENERATED -->

<!-- CUSTOM SECTION: Team Notes -->
## Team Notes
This is our custom documentation that should be preserved.
<!-- END CUSTOM SECTION -->
"""

    new_content = """# Module

<!-- AUTO-GENERATED: Purpose - DO NOT EDIT -->
## Purpose
New purpose with updated content
<!-- END AUTO-GENERATED -->

<!-- CUSTOM SECTION: Team Notes -->
## Team Notes
<!-- END CUSTOM SECTION -->
"""

    merger = SmartMerger()
    result = merger.merge(existing, new_content)

    # New auto-generated content
    assert "New purpose with updated content" in result
    # Preserved custom content
    assert "This is our custom documentation that should be preserved" in result


@pytest.mark.asyncio
async def test_per_folder_generator_integration(test_project, mock_llm_client):
    """Test PerFolderGenerator produces valid output."""
    from src.agents.project_documenter.per_folder_generator import PerFolderGenerator
    from src.agents.project_documenter.folder_analyzer import FolderInfo

    generator = PerFolderGenerator(mock_llm_client)

    folder_info = FolderInfo(
        path=test_project / "src" / "core",
        relative_path=Path("src/core"),
        score=15,
        file_count=2,
        has_subfolders=False,
        primary_language="python",
    )

    class MockProfile:
        name = "TestProject"
        primary_language = "python"

    ai_context = await generator.generate_ai_context(folder_info, MockProfile())
    readme = await generator.generate_readme(folder_info, MockProfile())

    # Verify AI-CONTEXT.md
    assert "src/core/AI-CONTEXT.md" in ai_context.path
    assert "<!-- AUTO-GENERATED: Purpose" in ai_context.content
    assert "<!-- CUSTOM SECTION:" in ai_context.content

    # Verify README.md
    assert "src/core/README.md" in readme.path
    assert "<!-- AUTO-GENERATED: Overview" in readme.content


@pytest.mark.asyncio
async def test_index_builder_integration(test_project):
    """Test IndexBuilder adds navigation."""
    from src.agents.project_documenter.index_builder import IndexBuilder
    from src.agents.project_documenter.folder_analyzer import FolderAnalyzer

    analyzer = FolderAnalyzer()
    folders = analyzer.analyze_folders(test_project)

    builder = IndexBuilder()

    # Test module index
    claude_content = """# Project

## Overview
This is a test project.

## Architecture
Some architecture info.
"""

    result = builder.add_module_index(claude_content, folders)

    assert "<!-- AUTO-GENERATED: Documentation Index -->" in result
    assert "Module Documentation" in result

    # Test folder structure
    readme_content = """# Project

## Overview
Project overview.
"""

    result2 = builder.add_folder_structure(readme_content, folders)

    assert "<!-- AUTO-GENERATED: Folder Structure -->" in result2
    assert "Repository Structure" in result2


@pytest.mark.asyncio
async def test_full_per_folder_workflow(test_project, mock_llm_client):
    """Test the complete per-folder documentation workflow."""
    from src.agents.project_documenter.folder_analyzer import FolderAnalyzer
    from src.agents.project_documenter.per_folder_generator import PerFolderGenerator
    from src.agents.project_documenter.smart_merger import SmartMerger
    from src.agents.project_documenter.metadata_manager import MetadataManager
    from src.agents.project_documenter.index_builder import IndexBuilder

    # Initialize components
    folder_analyzer = FolderAnalyzer()
    generator = PerFolderGenerator(mock_llm_client)
    merger = SmartMerger()
    metadata = MetadataManager()
    index_builder = IndexBuilder()

    # Analyze project
    folders = folder_analyzer.analyze_folders(test_project)
    assert len(folders) >= 3

    # Initialize metadata
    metadata.initialize(test_project)

    # Generate docs for each folder
    class MockProfile:
        name = "TestProject"
        primary_language = "python"

    generated_docs = []
    for folder in folders:
        if metadata.has_folder_changed(folder.path):
            ai_context = await generator.generate_ai_context(folder, MockProfile())
            readme = await generator.generate_readme(folder, MockProfile())
            generated_docs.extend([ai_context, readme])
            metadata.update_folder(folder.path, folder.file_count)

    # Verify we generated docs
    assert len(generated_docs) >= 6  # At least 3 folders * 2 files each

    # Verify documentation structure
    ai_context_docs = [d for d in generated_docs if "AI-CONTEXT.md" in d.path]
    readme_docs = [d for d in generated_docs if "README.md" in d.path]

    assert len(ai_context_docs) >= 3
    assert len(readme_docs) >= 3

    # All should have markers
    for doc in generated_docs:
        assert "<!-- AUTO-GENERATED:" in doc.content
        assert "<!-- CUSTOM SECTION:" in doc.content


@pytest.mark.asyncio
async def test_incremental_regeneration_workflow(test_project, mock_llm_client):
    """Test incremental regeneration only processes changed folders."""
    from src.agents.project_documenter.folder_analyzer import FolderAnalyzer
    from src.agents.project_documenter.per_folder_generator import PerFolderGenerator
    from src.agents.project_documenter.metadata_manager import MetadataManager

    folder_analyzer = FolderAnalyzer()
    generator = PerFolderGenerator(mock_llm_client)
    metadata = MetadataManager()

    class MockProfile:
        name = "TestProject"
        primary_language = "python"

    # First run - all folders
    folders = folder_analyzer.analyze_folders(test_project)
    metadata.initialize(test_project)

    first_run_count = 0
    for folder in folders:
        if metadata.has_folder_changed(folder.path):
            await generator.generate_ai_context(folder, MockProfile())
            metadata.update_folder(folder.path, folder.file_count)
            first_run_count += 1

    assert first_run_count >= 3  # All folders processed

    # Second run - no changes
    second_run_count = 0
    for folder in folders:
        if metadata.has_folder_changed(folder.path):
            await generator.generate_ai_context(folder, MockProfile())
            metadata.update_folder(folder.path, folder.file_count)
            second_run_count += 1

    assert second_run_count == 0  # No folders processed

    # Modify one file
    (test_project / "src" / "core" / "utils.py").write_text("# Modified content")

    # Third run - only modified folder
    third_run_count = 0
    for folder in folders:
        if metadata.has_folder_changed(folder.path):
            await generator.generate_ai_context(folder, MockProfile())
            metadata.update_folder(folder.path, folder.file_count)
            third_run_count += 1

    assert third_run_count == 1  # Only one folder processed
