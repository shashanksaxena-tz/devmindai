"""Tests for CodebaseAnalyzer."""

import os
import tempfile
from pathlib import Path

import pytest

from src.agents.project_documenter.analyzer import CodebaseAnalyzer, CodebaseProfile


class TestCodebaseAnalyzer:
    """Test suite for CodebaseAnalyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create an analyzer instance."""
        return CodebaseAnalyzer()

    @pytest.fixture
    def python_project(self, tmp_path):
        """Create a mock Python project."""
        # Create project structure
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "__init__.py").write_text("")
        (tmp_path / "src" / "main.py").write_text(
            """
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello"}
"""
        )
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "__init__.py").write_text("")
        (tmp_path / "tests" / "test_main.py").write_text(
            """
import pytest

def test_example():
    assert True
"""
        )

        # Create config files
        (tmp_path / "pyproject.toml").write_text(
            """
[project]
name = "test-project"
version = "0.1.0"

[project.dependencies]
fastapi = ">=0.100.0"
uvicorn = ">=0.20.0"

[tool.ruff]
line-length = 100

[tool.pytest.ini_options]
testpaths = ["tests"]
"""
        )

        (tmp_path / "README.md").write_text(
            """
# Test Project

A test project for documentation generation.

## Features
- Feature 1
- Feature 2
"""
        )

        # Create git directory (mock)
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "HEAD").write_text("ref: refs/heads/main")

        return tmp_path

    @pytest.fixture
    def javascript_project(self, tmp_path):
        """Create a mock JavaScript project."""
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "index.js").write_text(
            """
const express = require('express');
const app = express();

app.get('/', (req, res) => {
    res.json({ message: 'Hello' });
});

module.exports = app;
"""
        )

        (tmp_path / "package.json").write_text(
            """
{
    "name": "test-js-project",
    "version": "1.0.0",
    "scripts": {
        "start": "node src/index.js",
        "test": "jest",
        "lint": "eslint src/"
    },
    "dependencies": {
        "express": "^4.18.0"
    },
    "devDependencies": {
        "jest": "^29.0.0",
        "eslint": "^8.0.0"
    }
}
"""
        )

        return tmp_path

    def test_analyze_nonexistent_path(self, analyzer):
        """Should raise error for nonexistent path."""
        with pytest.raises(ValueError, match="Path does not exist"):
            analyzer.analyze("/nonexistent/path/12345")

    def test_analyze_python_project(self, analyzer, python_project):
        """Should correctly analyze a Python project."""
        profile = analyzer.analyze(str(python_project))

        assert profile.name == python_project.name
        assert profile.primary_language == "python"
        assert "fastapi" in profile.frameworks
        assert profile.has_git is True
        assert profile.default_branch == "main"
        assert profile.has_readme is True

    def test_analyze_detects_dependencies(self, analyzer, python_project):
        """Should detect Python dependencies."""
        profile = analyzer.analyze(str(python_project))

        assert len(profile.dependencies) > 0
        pip_deps = next((d for d in profile.dependencies if d.package_manager == "pip"), None)
        assert pip_deps is not None
        assert "fastapi" in pip_deps.dependencies

    def test_analyze_detects_commands(self, analyzer, python_project):
        """Should detect test and lint commands."""
        profile = analyzer.analyze(str(python_project))

        assert "pytest" in profile.test_commands
        # Ruff detected in pyproject.toml
        assert any("ruff" in cmd for cmd in profile.lint_commands)

    def test_analyze_javascript_project(self, analyzer, javascript_project):
        """Should correctly analyze a JavaScript project."""
        profile = analyzer.analyze(str(javascript_project))

        assert profile.primary_language == "javascript"
        assert "express" in profile.frameworks

    def test_analyze_detects_npm_dependencies(self, analyzer, javascript_project):
        """Should detect npm dependencies."""
        profile = analyzer.analyze(str(javascript_project))

        npm_deps = next((d for d in profile.dependencies if d.package_manager == "npm"), None)
        assert npm_deps is not None
        assert "express" in npm_deps.dependencies
        assert "jest" in npm_deps.dev_dependencies

    def test_analyze_detects_npm_scripts(self, analyzer, javascript_project):
        """Should detect npm scripts as commands."""
        profile = analyzer.analyze(str(javascript_project))

        assert any("npm run test" in cmd for cmd in profile.test_commands)
        assert any("npm run lint" in cmd for cmd in profile.lint_commands)

    def test_analyze_extracts_description(self, analyzer, python_project):
        """Should extract description from README."""
        profile = analyzer.analyze(str(python_project))

        assert "test project" in profile.description.lower()

    def test_analyze_detects_test_directories(self, analyzer, python_project):
        """Should detect test directories."""
        profile = analyzer.analyze(str(python_project))

        assert "tests" in profile.structure.test_directories

    def test_analyze_detects_code_style_tools(self, analyzer, python_project):
        """Should detect code style tools from config."""
        profile = analyzer.analyze(str(python_project))

        assert "ruff" in profile.code_style

    def test_analyzer_respects_max_files(self, tmp_path):
        """Should respect max_files limit."""
        # Create many files
        for i in range(50):
            (tmp_path / f"file_{i}.py").write_text(f"# File {i}")

        analyzer = CodebaseAnalyzer(max_files=10)
        profile = analyzer.analyze(str(tmp_path))

        assert len(profile.structure.files) <= 10

    def test_analyzer_ignores_node_modules(self, analyzer, javascript_project):
        """Should ignore node_modules directory."""
        # Create node_modules
        (javascript_project / "node_modules").mkdir()
        (javascript_project / "node_modules" / "express").mkdir()
        (javascript_project / "node_modules" / "express" / "index.js").write_text("module.exports = {};")

        profile = analyzer.analyze(str(javascript_project))

        # No files from node_modules should be in the profile
        assert not any("node_modules" in f.relative_path for f in profile.structure.files)

    def test_profile_to_dict_conversion(self, analyzer, python_project):
        """Should be able to serialize profile."""
        profile = analyzer.analyze(str(python_project))

        # Profile should have all required attributes
        assert hasattr(profile, "name")
        assert hasattr(profile, "primary_language")
        assert hasattr(profile, "frameworks")
        assert hasattr(profile, "dependencies")
        assert hasattr(profile, "structure")


class TestCodebaseProfile:
    """Tests for CodebaseProfile dataclass."""

    def test_default_values(self):
        """Profile should have sensible defaults."""
        profile = CodebaseProfile(root_path="/test", name="test")

        assert profile.primary_language == "unknown"
        assert profile.frameworks == []
        assert profile.dependencies == []
        assert profile.has_git is False
        assert profile.default_branch == "main"
