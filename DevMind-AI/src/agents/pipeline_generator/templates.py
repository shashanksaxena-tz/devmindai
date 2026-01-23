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
