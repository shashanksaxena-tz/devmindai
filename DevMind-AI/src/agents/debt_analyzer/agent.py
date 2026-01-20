"""Technical Debt Analyzer Agent."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from src.agents.base import AgentContext, BaseAgent
from src.agents.debt_analyzer.complexity import ComplexityAnalyzer, ComplexityMetrics
from src.agents.debt_analyzer.duplication import DuplicationDetector, DuplicationReport
from src.agents.debt_analyzer.scorer import DebtScorer, DebtScore
from src.core.llm import TaskComplexity


class DebtAnalyzerAgent(BaseAgent):
    """Agent for analyzing technical debt in a repository."""

    name = "debt_analyzer"
    description = "Analyzes technical debt including complexity, duplication, and code smells."
    complexity = TaskComplexity.MODERATE

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.complexity_analyzer = ComplexityAnalyzer()
        self.duplication_detector = DuplicationDetector()
        self.scorer = DebtScorer()

    async def execute(self, context: AgentContext, **kwargs: Any) -> dict[str, Any]:
        """Execute the debt analysis.

        Args:
            context: Execution context containing repository info.
            **kwargs: Additional arguments.
                      - files: dict[str, str] (path -> content)
                      - file_paths: list[str] (list of file paths to read from disk if 'files' not provided)
                      - root_dir: str (root directory for file_paths)

        Returns:
            Analysis results including scores and identified debt items.
        """
        files = kwargs.get("files")

        # If files dictionary is not provided, try to read from disk
        if not files:
            file_paths = kwargs.get("file_paths", [])
            root_dir = kwargs.get("root_dir", ".")
            files = self._read_files(file_paths, root_dir)

        if not files:
            return {
                "success": False,
                "error": "No files provided for analysis",
                "score": None
            }

        # 1. Analyze Complexity (Python only for now)
        complexity_metrics = self._analyze_complexity(files)

        # 2. Detect Duplication (All text files)
        duplication_report = self.duplication_detector.detect(files)

        # 3. Calculate Score
        debt_score: DebtScore = self.scorer.calculate_score(
            complexity_metrics=complexity_metrics,
            duplication_report=duplication_report,
            # Placeholder for coverage and dependencies
            coverage_data=None,
            dependency_data=None,
        )

        return {
            "success": True,
            "data": {
                "score": debt_score.score,
                "grade": debt_score.grade,
                "total_debt_hours": debt_score.total_debt_hours,
                "estimated_cost": debt_score.estimated_cost,
                "metrics": {
                    "complexity": {
                        "average": complexity_metrics.average_complexity,
                        "max": complexity_metrics.max_complexity,
                        "total_lines": complexity_metrics.total_lines,
                        "total_functions": complexity_metrics.total_functions,
                    },
                    "duplication": {
                        "percentage": duplication_report.duplication_percentage,
                        "duplicated_lines": duplication_report.duplicated_lines,
                        "total_lines": duplication_report.total_lines,
                    }
                },
                "debt_items": [
                    {
                        "category": item.category.value,
                        "file_path": item.file_path,
                        "description": item.description,
                        "severity": item.severity,
                        "estimated_hours": item.estimated_hours,
                        "line_number": item.line_number,
                        "suggested_fix": item.suggested_fix,
                    }
                    for item in debt_score.debt_items
                ],
            }
        }

    def _read_files(self, file_paths: list[str], root_dir: str) -> dict[str, str]:
        """Read files from disk."""
        files = {}
        for path in file_paths:
            full_path = os.path.join(root_dir, path)
            try:
                if os.path.isfile(full_path):
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        files[path] = f.read()
            except Exception:
                continue
        return files

    def _analyze_complexity(self, files: dict[str, str]) -> ComplexityMetrics:
        """Aggregate complexity metrics across all Python files."""
        # Note: The current ComplexityMetrics is file-level, but also used as an aggregate in _score_complexity?
        # Let's check scorer.py:
        # def _score_complexity(self, metrics: Any) -> tuple[int, list[DebtItem]]:
        #     if metrics: for func in metrics.functions: ...
        #
        # So I need to combine all functions from all files into one "aggregate" metrics object
        # or change how scorer works.
        # Given ComplexityMetrics definition:
        # class ComplexityMetrics:
        #    file_path: str
        #    functions: list[FunctionComplexity] = field(default_factory=list)
        #    total_lines: int = 0

        all_functions = []
        total_lines = 0

        for file_path, content in files.items():
            if file_path.endswith(".py"):
                metrics = self.complexity_analyzer.analyze(content, "python", file_path)
                all_functions.extend(metrics.functions)
                total_lines += metrics.total_lines
            else:
                # Add lines for non-python files too? Or strictly Python complexity?
                # Usually complexity is language specific.
                pass

        return ComplexityMetrics(
            file_path="aggregate", # Placeholder
            functions=all_functions,
            total_lines=total_lines
        )
