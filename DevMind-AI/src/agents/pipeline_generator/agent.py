# src/agents/pipeline_generator/agent.py
"""PipelineGenerator agent."""
from __future__ import annotations

from typing import Any

from src.agents.base import BaseAgent, AgentContext, TaskComplexity

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
