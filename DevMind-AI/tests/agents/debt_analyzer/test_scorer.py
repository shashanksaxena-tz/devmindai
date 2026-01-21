# tests/agents/debt_analyzer/test_scorer.py
"""Tests for technical debt scorer."""
import pytest
from src.agents.debt_analyzer.scorer import (
    DebtScorer,
    DebtCategory,
    DebtScore,
    DebtItem,
)
from src.agents.debt_analyzer.complexity import ComplexityMetrics, FunctionComplexity
from src.agents.debt_analyzer.duplication import DuplicationReport, DuplicateBlock


class TestDebtScorer:
    """Test DebtScorer."""

    @pytest.fixture
    def scorer(self):
        return DebtScorer()

    def test_calculate_score_perfect(self, scorer):
        """Calculate score for perfect code."""
        complexity = ComplexityMetrics(file_path="clean.py")
        duplication = DuplicationReport()

        score = scorer.calculate_score(complexity, duplication)
        assert score.score == 100
        assert score.grade == "A"
        assert score.total_debt_hours == 0

    def test_calculate_score_high_complexity(self, scorer):
        """Score penalizes high complexity."""
        complexity = ComplexityMetrics(
            file_path="complex.py",
            functions=[
                FunctionComplexity(
                    name="bad", file_path="complex.py", line_number=1,
                    cyclomatic_complexity=25,  # High
                    cognitive_complexity=30,
                )
            ]
        )
        duplication = DuplicationReport()

        score = scorer.calculate_score(complexity, duplication)
        assert score.score < 100
        assert any(i.category == DebtCategory.COMPLEXITY for i in score.debt_items)

    def test_calculate_score_duplication(self, scorer):
        """Score penalizes duplication."""
        complexity = ComplexityMetrics(file_path="dup.py")
        duplication = DuplicationReport(
            duplicate_blocks=[
                DuplicateBlock(content_hash="abc", lines=10, occurrences=[{"file": "f1.py"}, {"file": "f2.py"}])
            ],
            total_lines=100,
            duplicated_lines=10,
        )
        # 10% duplication

        score = scorer.calculate_score(complexity, duplication)
        assert score.score < 100
        assert any(i.category == DebtCategory.DUPLICATION for i in score.debt_items)

    def test_calculate_estimated_cost(self, scorer):
        """Calculate financial cost of debt."""
        complexity = ComplexityMetrics(
            file_path="complex.py",
            functions=[
                FunctionComplexity(
                    name="bad", file_path="complex.py", line_number=1,
                    cyclomatic_complexity=25,
                )
            ]
        )

        score = scorer.calculate_score(complexity, None)
        assert score.estimated_cost > 0
        assert score.total_debt_hours > 0
