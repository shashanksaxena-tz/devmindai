# src/agents/pipeline_generator/analyzer.py
"""Analyzes project structure for pipeline generation."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class ProjectType(Enum):
    """Detected project types."""
    PYTHON = "python"
    NODEJS = "nodejs"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    MONOREPO = "monorepo"
    UNKNOWN = "unknown"


class Framework(Enum):
    """Detected frameworks."""
    FASTAPI = "fastapi"
    DJANGO = "django"
    FLASK = "flask"
    REACT = "react"
    NEXTJS = "nextjs"
    VUE = "vue"
    EXPRESS = "express"
    SPRING = "spring"
    NONE = "none"


@dataclass
class ProjectAnalysis:
    """Analysis of project structure."""
    project_type: ProjectType
    framework: Framework
    language_version: str
    has_tests: bool
    test_framework: str
    has_docker: bool
    has_linting: bool
    dependencies_file: str
    build_command: str
    test_command: str
    services: list[str] = field(default_factory=list)  # postgres, redis, etc.


class ProjectAnalyzer:
    """Analyzes project structure."""

    FILE_INDICATORS = {
        "pyproject.toml": ProjectType.PYTHON,
        "requirements.txt": ProjectType.PYTHON,
        "package.json": ProjectType.NODEJS,
        "pom.xml": ProjectType.JAVA,
        "build.gradle": ProjectType.JAVA,
        "go.mod": ProjectType.GO,
        "Cargo.toml": ProjectType.RUST,
    }

    FRAMEWORK_INDICATORS = {
        "fastapi": Framework.FASTAPI,
        "django": Framework.DJANGO,
        "flask": Framework.FLASK,
        "react": Framework.REACT,
        "next": Framework.NEXTJS,
        "vue": Framework.VUE,
        "express": Framework.EXPRESS,
        "spring": Framework.SPRING,
    }

    def analyze(self, files: dict[str, str]) -> ProjectAnalysis:
        """Analyze project files."""
        project_type = self._detect_project_type(files)
        framework = self._detect_framework(files, project_type)

        return ProjectAnalysis(
            project_type=project_type,
            framework=framework,
            language_version=self._detect_version(files, project_type),
            has_tests=self._has_tests(files),
            test_framework=self._detect_test_framework(files, project_type),
            has_docker="Dockerfile" in files or "docker-compose.yml" in files,
            has_linting=self._has_linting(files, project_type),
            dependencies_file=self._get_deps_file(project_type),
            build_command=self._get_build_command(project_type, framework),
            test_command=self._get_test_command(project_type),
            services=self._detect_services(files),
        )

    def _detect_project_type(self, files: dict[str, str]) -> ProjectType:
        """Detect project type from files."""
        for filename, proj_type in self.FILE_INDICATORS.items():
            if filename in files:
                return proj_type
        return ProjectType.UNKNOWN

    def _detect_framework(self, files: dict[str, str], proj_type: ProjectType) -> Framework:
        """Detect framework from dependencies."""
        if proj_type == ProjectType.PYTHON:
            deps_content = files.get("pyproject.toml", "") + files.get("requirements.txt", "")
            for name, fw in self.FRAMEWORK_INDICATORS.items():
                if name in deps_content.lower():
                    return fw
        elif proj_type == ProjectType.NODEJS:
            pkg = files.get("package.json", "")
            for name, fw in self.FRAMEWORK_INDICATORS.items():
                if name in pkg.lower():
                    return fw
        return Framework.NONE

    def _detect_version(self, files: dict[str, str], proj_type: ProjectType) -> str:
        """Detect language version."""
        if proj_type == ProjectType.PYTHON:
            if "pyproject.toml" in files:
                # Parse python version
                return "3.11"
        elif proj_type == ProjectType.NODEJS:
            return "20"
        return ""

    def _has_tests(self, files: dict[str, str]) -> bool:
        """Check if project has tests."""
        return any(
            "test" in f.lower() or "spec" in f.lower()
            for f in files.keys()
        )

    def _detect_test_framework(self, files: dict[str, str], proj_type: ProjectType) -> str:
        """Detect test framework."""
        if proj_type == ProjectType.PYTHON:
            if "pytest" in str(files.values()):
                return "pytest"
            return "unittest"
        elif proj_type == ProjectType.NODEJS:
            if "jest" in files.get("package.json", ""):
                return "jest"
            if "vitest" in files.get("package.json", ""):
                return "vitest"
            return "jest"
        return ""

    def _has_linting(self, files: dict[str, str], proj_type: ProjectType) -> bool:
        """Check for linting configuration."""
        lint_files = [".eslintrc", "ruff.toml", ".flake8", "pylintrc"]
        return any(f in files for f in lint_files)

    def _get_deps_file(self, proj_type: ProjectType) -> str:
        """Get dependencies file name."""
        mapping = {
            ProjectType.PYTHON: "requirements.txt",
            ProjectType.NODEJS: "package.json",
            ProjectType.JAVA: "pom.xml",
            ProjectType.GO: "go.mod",
            ProjectType.RUST: "Cargo.toml",
        }
        return mapping.get(proj_type, "")

    def _get_build_command(self, proj_type: ProjectType, framework: Framework) -> str:
        """Get build command."""
        if proj_type == ProjectType.NODEJS:
            return "npm run build"
        elif proj_type == ProjectType.JAVA:
            return "mvn package"
        return ""

    def _get_test_command(self, proj_type: ProjectType) -> str:
        """Get test command."""
        mapping = {
            ProjectType.PYTHON: "pytest",
            ProjectType.NODEJS: "npm test",
            ProjectType.JAVA: "mvn test",
            ProjectType.GO: "go test ./...",
            ProjectType.RUST: "cargo test",
        }
        return mapping.get(proj_type, "")

    def _detect_services(self, files: dict[str, str]) -> list[str]:
        """Detect required services (databases, etc.)."""
        services = []
        all_content = " ".join(files.values()).lower()

        if "postgres" in all_content or "psycopg" in all_content:
            services.append("postgres")
        if "redis" in all_content:
            services.append("redis")
        if "mongodb" in all_content or "pymongo" in all_content:
            services.append("mongodb")

        return services
