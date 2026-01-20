"""Technical debt scoring system."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class DebtCategory(Enum):
    """Categories of technical debt."""
    COMPLEXITY = "complexity"
    DUPLICATION = "duplication"
    OUTDATED_DEPS = "outdated_dependencies"
    MISSING_TESTS = "missing_tests"
    CODE_SMELLS = "code_smells"
    DOCUMENTATION = "documentation"


@dataclass
class DebtItem:
    """A single item of technical debt."""
    category: DebtCategory
    file_path: str
    description: str
    severity: str  # low, medium, high, critical
    estimated_hours: float
    line_number: Optional[int] = None
    suggested_fix: Optional[str] = None


@dataclass
class DebtScore:
    """Overall debt score for a repository."""
    score: int  # 0-100, higher is better
    grade: str  # A, B, C, D, F
    total_debt_hours: float
    debt_items: list[DebtItem] = field(default_factory=list)
    by_category: dict[str, int] = field(default_factory=dict)

    @property
    def estimated_cost(self) -> float:
        """Estimate cost assuming $150/hour."""
        return self.total_debt_hours * 150


class DebtScorer:
    """Calculates technical debt scores."""

    WEIGHTS = {
        DebtCategory.COMPLEXITY: 0.25,
        DebtCategory.DUPLICATION: 0.20,
        DebtCategory.OUTDATED_DEPS: 0.15,
        DebtCategory.MISSING_TESTS: 0.20,
        DebtCategory.CODE_SMELLS: 0.10,
        DebtCategory.DOCUMENTATION: 0.10,
    }

    SEVERITY_MULTIPLIERS = {
        "critical": 4.0,
        "high": 2.0,
        "medium": 1.0,
        "low": 0.5,
    }

    def calculate_score(
        self,
        complexity_metrics: Any,
        duplication_report: Any,
        coverage_data: dict | None = None,
        dependency_data: dict | None = None,
    ) -> DebtScore:
        """Calculate overall debt score."""
        debt_items = []
        category_scores = {}

        # Analyze complexity
        complexity_score, complexity_items = self._score_complexity(complexity_metrics)
        category_scores[DebtCategory.COMPLEXITY.value] = complexity_score
        debt_items.extend(complexity_items)

        # Analyze duplication
        duplication_score, dup_items = self._score_duplication(duplication_report)
        category_scores[DebtCategory.DUPLICATION.value] = duplication_score
        debt_items.extend(dup_items)

        # Calculate weighted score
        # Note: If we don't have data for a category, assume score 100? Or 0?
        # The plan implementation:
        weighted_score = sum(
            category_scores.get(cat.value, 100) * weight
            for cat, weight in self.WEIGHTS.items()
        )

        # Normalize to 0-100
        final_score = min(100, max(0, int(weighted_score)))

        # Determine grade
        grade = self._score_to_grade(final_score)

        # Calculate total debt hours
        total_hours = sum(item.estimated_hours for item in debt_items)

        return DebtScore(
            score=final_score,
            grade=grade,
            total_debt_hours=total_hours,
            debt_items=debt_items,
            by_category=category_scores,
        )

    def _score_complexity(self, metrics: Any) -> tuple[int, list[DebtItem]]:
        """Score based on complexity metrics."""
        items = []
        deductions = 0

        if metrics:
            for func in metrics.functions:
                if func.cyclomatic_complexity > 15:
                    items.append(DebtItem(
                        category=DebtCategory.COMPLEXITY,
                        file_path=func.file_path,
                        description=f"Function '{func.name}' has complexity {func.cyclomatic_complexity}",
                        severity="high" if func.cyclomatic_complexity > 20 else "medium",
                        estimated_hours=2.0,
                        line_number=func.line_number,
                        suggested_fix="Split into smaller functions",
                    ))
                    deductions += 5

        return max(0, 100 - deductions), items

    def _score_duplication(self, report: Any) -> tuple[int, list[DebtItem]]:
        """Score based on duplication."""
        items = []

        if report and report.duplication_percentage > 5:
            for block in report.duplicate_blocks[:10]:
                file_path = block.occurrences[0]["file"] if block.occurrences else "unknown"
                items.append(DebtItem(
                    category=DebtCategory.DUPLICATION,
                    file_path=file_path,
                    description=f"Duplicated code block ({block.lines} lines, {len(block.occurrences)} occurrences)",
                    severity="medium",
                    estimated_hours=1.0,
                    suggested_fix="Extract to shared function/module",
                ))

        score = max(0, 100 - int(report.duplication_percentage * 2)) if report else 100
        return score, items

    def _score_to_grade(self, score: int) -> str:
        """Convert score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        return "F"
