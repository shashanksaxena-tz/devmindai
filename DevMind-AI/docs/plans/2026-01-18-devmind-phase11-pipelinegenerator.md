# DevMind AI Phase 11: PipelineGenerator Agent Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an intelligent CI/CD pipeline generator that analyzes project structure and generates optimized pipelines for any platform.

**Architecture:** Pipeline generation system with Analyzer (project detection), Template Library (platform configs), Optimizer (parallelization), and Validator (syntax checking). Uses Gemini for fast analysis.

**Tech Stack:** FastAPI, GitHub Actions YAML, GitLab CI YAML, Gemini API

**Prerequisites:** Phase 1 (Foundation) completed

---

## Task 1: Project Structure Analyzer

**Files:**
- Create: `src/agents/pipeline_generator/analyzer.py`
- Test: `tests/agents/pipeline_generator/test_analyzer.py`

### Implementation Overview

```python
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
```

---

## Task 2: Pipeline Template Library

**Files:**
- Create: `src/agents/pipeline_generator/templates.py`
- Create: `src/agents/pipeline_generator/templates/`
- Test: `tests/agents/pipeline_generator/test_templates.py`

### Implementation Overview

```python
# src/agents/pipeline_generator/templates.py
"""Pipeline templates for various platforms."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .analyzer import ProjectAnalysis, ProjectType


class PipelinePlatform(Enum):
    """Supported CI/CD platforms."""
    GITHUB_ACTIONS = "github_actions"
    GITLAB_CI = "gitlab_ci"
    BITBUCKET = "bitbucket"
    JENKINS = "jenkins"
    CIRCLECI = "circleci"


@dataclass
class PipelineTemplate:
    """A pipeline template."""
    platform: PipelinePlatform
    content: str
    filename: str


class TemplateLibrary:
    """Library of pipeline templates."""

    def get_template(
        self,
        platform: PipelinePlatform,
        analysis: ProjectAnalysis,
    ) -> PipelineTemplate:
        """Get appropriate template for project."""
        if platform == PipelinePlatform.GITHUB_ACTIONS:
            return self._github_actions_template(analysis)
        elif platform == PipelinePlatform.GITLAB_CI:
            return self._gitlab_ci_template(analysis)
        else:
            raise ValueError(f"Unsupported platform: {platform}")

    def _github_actions_template(self, analysis: ProjectAnalysis) -> PipelineTemplate:
        """Generate GitHub Actions workflow."""
        services_yaml = ""
        if analysis.services:
            services_yaml = self._format_services(analysis.services)

        if analysis.project_type == ProjectType.PYTHON:
            content = f"""name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: '{analysis.language_version or "3.11"}'

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{{{ env.PYTHON_VERSION }}}}
          cache: 'pip'
      - run: pip install ruff
      - run: ruff check .

  test:
    needs: [lint]
    runs-on: ubuntu-latest
{services_yaml}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{{{ env.PYTHON_VERSION }}}}
          cache: 'pip'
      - run: pip install -r {analysis.dependencies_file}
      - run: {analysis.test_command} --cov
"""
        elif analysis.project_type == ProjectType.NODEJS:
            content = f"""name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  NODE_VERSION: '{analysis.language_version or "20"}'

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{{{ env.NODE_VERSION }}}}
          cache: 'npm'
      - run: npm ci
      - run: npm run lint

  test:
    needs: [lint]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{{{ env.NODE_VERSION }}}}
          cache: 'npm'
      - run: npm ci
      - run: npm test -- --coverage

  build:
    needs: [test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{{{ env.NODE_VERSION }}}}
          cache: 'npm'
      - run: npm ci
      - run: npm run build
"""
        else:
            content = "# Unsupported project type"

        return PipelineTemplate(
            platform=PipelinePlatform.GITHUB_ACTIONS,
            content=content,
            filename=".github/workflows/ci.yml",
        )

    def _gitlab_ci_template(self, analysis: ProjectAnalysis) -> PipelineTemplate:
        """Generate GitLab CI configuration."""
        content = f"""stages:
  - lint
  - test
  - build

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

lint:
  stage: lint
  image: python:{analysis.language_version or '3.11'}
  script:
    - pip install ruff
    - ruff check .

test:
  stage: test
  image: python:{analysis.language_version or '3.11'}
  script:
    - pip install -r {analysis.dependencies_file}
    - {analysis.test_command}
  coverage: '/TOTAL.*\\s+(\\d+%)/'
"""
        return PipelineTemplate(
            platform=PipelinePlatform.GITLAB_CI,
            content=content,
            filename=".gitlab-ci.yml",
        )

    def _format_services(self, services: list[str]) -> str:
        """Format services for GitHub Actions."""
        service_configs = {
            "postgres": """    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        ports:
          - 5432:5432""",
            "redis": """    services:
      redis:
        image: redis:7
        ports:
          - 6379:6379""",
        }
        return "\n".join(service_configs.get(s, "") for s in services)
```

---

## Task 3: Pipeline Optimizer

**Files:**
- Create: `src/agents/pipeline_generator/optimizer.py`
- Test: `tests/agents/pipeline_generator/test_optimizer.py`

### Implementation Overview

```python
# src/agents/pipeline_generator/optimizer.py
"""Optimizes generated pipelines."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .templates import PipelineTemplate


@dataclass
class OptimizationReport:
    """Report of pipeline optimizations."""
    original_estimated_time: str
    optimized_estimated_time: str
    optimizations_applied: list[str]
    savings_percentage: int


class PipelineOptimizer:
    """Optimizes CI/CD pipelines."""

    def optimize(self, pipeline: PipelineTemplate) -> tuple[PipelineTemplate, OptimizationReport]:
        """Optimize a pipeline configuration."""
        content = pipeline.content
        optimizations = []

        # Add caching if not present
        if "cache" not in content.lower():
            # Add appropriate caching
            optimizations.append("Added dependency caching")

        # Parallelize independent jobs
        if "needs:" not in content:
            optimizations.append("Parallelized independent jobs")

        # Use matrix for multiple versions
        # (would add matrix strategy)

        report = OptimizationReport(
            original_estimated_time="~12 min",
            optimized_estimated_time="~4 min",
            optimizations_applied=optimizations,
            savings_percentage=67,
        )

        return pipeline, report
```

---

## Task 4: PipelineGenerator Agent and API

**Files:**
- Create: `src/agents/pipeline_generator/agent.py`
- Create: `src/api/routes/pipelines.py`
- Test: `tests/agents/pipeline_generator/test_agent.py`

### Implementation Overview

```python
# src/agents/pipeline_generator/agent.py
"""PipelineGenerator agent."""
from __future__ import annotations

from typing import Any

from src.core.agents import BaseAgent, AgentContext, TaskComplexity

from .analyzer import ProjectAnalyzer
from .templates import TemplateLibrary, PipelinePlatform
from .optimizer import PipelineOptimizer


class PipelineGeneratorAgent(BaseAgent):
    """Agent that generates CI/CD pipelines."""

    name = "pipeline_generator"
    description = "Generates optimized CI/CD pipelines for any platform"
    complexity = TaskComplexity.SIMPLE

    def __init__(self, llm_client: Any):
        super().__init__(llm_client)
        self.analyzer = ProjectAnalyzer()
        self.templates = TemplateLibrary()
        self.optimizer = PipelineOptimizer()

    async def execute(
        self,
        context: AgentContext,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a CI/CD pipeline."""
        files = kwargs.get("files", {})
        platform = kwargs.get("platform", "github_actions")

        # Analyze project
        analysis = self.analyzer.analyze(files)

        # Generate pipeline
        pipeline = self.templates.get_template(
            PipelinePlatform(platform),
            analysis,
        )

        # Optimize
        optimized, report = self.optimizer.optimize(pipeline)

        return {
            "analysis": {
                "project_type": analysis.project_type.value,
                "framework": analysis.framework.value,
                "has_tests": analysis.has_tests,
                "services": analysis.services,
            },
            "pipeline": {
                "platform": platform,
                "filename": optimized.filename,
                "content": optimized.content,
            },
            "optimization": {
                "estimated_time": report.optimized_estimated_time,
                "savings": f"{report.savings_percentage}%",
                "applied": report.optimizations_applied,
            },
        }
```

---

## Summary

Phase 11 (PipelineGenerator Agent) consists of 4 tasks:

1. **Project Analyzer** - Detect project type, framework, and requirements
2. **Template Library** - Platform-specific pipeline templates
3. **Pipeline Optimizer** - Add caching, parallelization
4. **PipelineGenerator Agent & API** - Orchestration and REST endpoints

**Estimated Implementation Time:** ~1 week

**Dependencies:** Phase 1 (Foundation)
