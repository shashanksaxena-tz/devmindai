"""Tests for FolderAnalyzer."""

from pathlib import Path
import pytest
from src.agents.project_documenter.folder_analyzer import FolderAnalyzer, FolderInfo


def test_folder_analyzer_identifies_code_folders(tmp_path):
    """Test that FolderAnalyzer finds folders with source code."""
    # Create test structure
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "agents").mkdir()
    (tmp_path / "src" / "agents" / "agent.py").write_text("class Agent: pass")
    (tmp_path / "src" / "agents" / "__init__.py").write_text("")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "test.pyc").write_text("compiled")
    
    # Create another folder without source code
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "readme.txt").write_text("documentation")

    analyzer = FolderAnalyzer()
    folders = analyzer.analyze_folders(tmp_path)

    # Should find src/agents but not __pycache__ or docs
    folder_paths = [f.relative_path for f in folders]
    assert Path("src/agents") in folder_paths
    assert Path("__pycache__") not in folder_paths
    assert Path("docs") not in folder_paths
    assert len(folders) > 0


def test_folder_info_scoring():
    """Test folder scoring prioritization."""
    analyzer = FolderAnalyzer()
    
    # Create folder info with package marker
    folder_info = analyzer._create_folder_info(
        Path("/project/src/agents"),
        Path("/project"),
        ["__init__.py", "agent.py", "base.py", "utils.py"],
        ["subagent"]
    )
    
    # Should have high score: +10 for __init__.py, +5 for 3+ files, +3 for subdirs
    assert folder_info.score >= 18
    assert folder_info.file_count == 4
    assert folder_info.has_subfolders is True
    assert folder_info.primary_language == "python"


def test_folder_analyzer_excludes_patterns(tmp_path):
    """Test that excluded patterns are properly skipped."""
    # Create excluded directories with proper parent creation
    (tmp_path / "node_modules" / "package").mkdir(parents=True)
    (tmp_path / "node_modules" / "package" / "index.js").write_text("// code")
    
    (tmp_path / ".git" / "hooks").mkdir(parents=True)
    (tmp_path / ".git" / "hooks" / "pre-commit").write_text("#!/bin/bash")
    
    (tmp_path / "venv" / "lib" / "python3.11").mkdir(parents=True)
    (tmp_path / "venv" / "lib" / "python3.11" / "site.py").write_text("# venv")
    
    # Create valid source folder
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hello')")

    analyzer = FolderAnalyzer()
    folders = analyzer.analyze_folders(tmp_path)

    folder_paths = [str(f.relative_path) for f in folders]
    
    # Should only find src
    assert "src" in folder_paths
    assert "node_modules" not in folder_paths
    assert ".git" not in folder_paths
    assert "venv" not in folder_paths


def test_folder_analyzer_detects_languages(tmp_path):
    """Test that primary language is correctly detected."""
    # TypeScript folder
    (tmp_path / "frontend").mkdir()
    (tmp_path / "frontend" / "app.tsx").write_text("const App = () => <div/>;")
    (tmp_path / "frontend" / "index.ts").write_text("export {};")
    
    # Python folder
    (tmp_path / "backend").mkdir()
    (tmp_path / "backend" / "main.py").write_text("print('hello')")

    analyzer = FolderAnalyzer()
    folders = analyzer.analyze_folders(tmp_path)

    folder_map = {str(f.relative_path): f for f in folders}
    
    assert folder_map["frontend"].primary_language == "typescript"
    assert folder_map["backend"].primary_language == "python"


def test_folder_analyzer_sort_by_score(tmp_path):
    """Test that folders are sorted by score (highest first)."""
    # High priority folder (has __init__.py and many files)
    (tmp_path / "core").mkdir()
    (tmp_path / "core" / "__init__.py").write_text("")
    (tmp_path / "core" / "config.py").write_text("")
    (tmp_path / "core" / "utils.py").write_text("")
    (tmp_path / "core" / "main.py").write_text("")
    
    # Low priority folder (single file)
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "run.py").write_text("")

    analyzer = FolderAnalyzer()
    folders = analyzer.analyze_folders(tmp_path)

    # Core should come first (higher score)
    assert str(folders[0].relative_path) == "core"
    assert folders[0].score > folders[1].score


def test_folder_analyzer_empty_project(tmp_path):
    """Test handling of project with no source files."""
    # Create only non-code files
    (tmp_path / "README.md").write_text("# Project")
    (tmp_path / "LICENSE").write_text("MIT")

    analyzer = FolderAnalyzer()
    folders = analyzer.analyze_folders(tmp_path)

    assert len(folders) == 0


def test_folder_info_dataclass():
    """Test FolderInfo dataclass fields."""
    folder_info = FolderInfo(
        path=Path("/project/src"),
        relative_path=Path("src"),
        score=15,
        file_count=10,
        has_subfolders=True,
        primary_language="python",
    )
    
    assert folder_info.path == Path("/project/src")
    assert folder_info.relative_path == Path("src")
    assert folder_info.score == 15
    assert folder_info.file_count == 10
    assert folder_info.has_subfolders is True
    assert folder_info.primary_language == "python"
