# DevMind AI Phase 5: DebtAnalyzer Agent Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an intelligent technical debt analyzer that continuously scans repositories, quantifies debt, tracks trends, and prioritizes refactoring efforts.

**Architecture:** Multi-metric analysis system with complexity analyzer, duplication detector, dependency checker, and trend tracker. Uses Gemini for fast analysis and Claude for refactoring recommendations.

**Tech Stack:** FastAPI, radon (Python complexity), tree-sitter, jscpd (duplication), Claude API, Gemini API

**Prerequisites:** Phase 1 (Foundation) completed

---

## Task 1: Code Complexity Analyzer

**Files:**
- Create: `src/agents/debt_analyzer/complexity.py`
- Test: `tests/agents/debt_analyzer/test_complexity.py`

### Step 1: Write the failing tests

```python
# tests/agents/debt_analyzer/test_complexity.py
"""Tests for code complexity analysis."""
import pytest
from src.agents.debt_analyzer.complexity import (
    ComplexityAnalyzer,
    ComplexityMetrics,
    FunctionComplexity,
)


class TestComplexityAnalyzer:
    """Test ComplexityAnalyzer."""

    @pytest.fixture
    def analyzer(self):
        return ComplexityAnalyzer()

    def test_calculate_cyclomatic_complexity(self, analyzer):
        """Calculate cyclomatic complexity."""
        code = '''
def process(x, y):
    if x > 0:
        if y > 0:
            return x + y
        else:
            return x - y
    elif x < 0:
        return -x
    else:
        return 0
'''
        result = analyzer.analyze(code, "python")
        func = result.functions[0]
        assert func.cyclomatic_complexity >= 4

    def test_detect_high_complexity_functions(self, analyzer):
        """Identify functions above complexity threshold."""
        code = '''
def simple(): return 1
def complex(a,b,c,d,e):
    if a: return 1
    elif b: return 2
    elif c: return 3
    elif d: return 4
    else: return 5
'''
        result = analyzer.analyze(code, "python")
        high = [f for f in result.functions if f.cyclomatic_complexity > 3]
        assert len(high) == 1
        assert high[0].name == "complex"

    def test_calculate_cognitive_complexity(self, analyzer):
        """Calculate cognitive complexity (nesting penalty)."""
        nested_code = '''
def deeply_nested(items):
    for item in items:
        if item.active:
            for sub in item.children:
                if sub.valid:
                    process(sub)
'''
        result = analyzer.analyze(nested_code, "python")
        assert result.functions[0].cognitive_complexity > result.functions[0].cyclomatic_complexity

    def test_file_level_metrics(self, analyzer):
        """Calculate file-level complexity metrics."""
        code = '''
def func1(): pass
def func2():
    if True: pass
class MyClass:
    def method1(self): pass
    def method2(self):
        for i in range(10):
            if i > 5: pass
'''
        result = analyzer.analyze(code, "python")

        assert result.total_functions >= 4
        assert result.average_complexity > 0
        assert result.max_complexity > 0
```

### Step 2: Run tests to verify they fail

```bash
pytest tests/agents/debt_analyzer/test_complexity.py -v
```

### Step 3: Implement the complexity analyzer

```python
# src/agents/debt_analyzer/__init__.py
"""DebtAnalyzer agent module."""

# src/agents/debt_analyzer/complexity.py
"""Code complexity analysis."""
from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FunctionComplexity:
    """Complexity metrics for a function."""
    name: str
    file_path: str
    line_number: int
    cyclomatic_complexity: int = 1
    cognitive_complexity: int = 0
    lines_of_code: int = 0
    parameter_count: int = 0
    nesting_depth: int = 0

    @property
    def is_complex(self) -> bool:
        return self.cyclomatic_complexity > 10 or self.cognitive_complexity > 15


@dataclass
class ComplexityMetrics:
    """File-level complexity metrics."""
    file_path: str
    functions: list[FunctionComplexity] = field(default_factory=list)
    total_lines: int = 0

    @property
    def total_functions(self) -> int:
        return len(self.functions)

    @property
    def average_complexity(self) -> float:
        if not self.functions:
            return 0.0
        return sum(f.cyclomatic_complexity for f in self.functions) / len(self.functions)

    @property
    def max_complexity(self) -> int:
        if not self.functions:
            return 0
        return max(f.cyclomatic_complexity for f in self.functions)


class ComplexityAnalyzer:
    """Analyzes code complexity metrics."""

    def analyze(self, code: str, language: str, file_path: str = "") -> ComplexityMetrics:
        """Analyze code complexity."""
        if language == "python":
            return self._analyze_python(code, file_path)
        return ComplexityMetrics(file_path=file_path)

    def _analyze_python(self, code: str, file_path: str) -> ComplexityMetrics:
        """Analyze Python code complexity."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return ComplexityMetrics(file_path=file_path)

        metrics = ComplexityMetrics(
            file_path=file_path,
            total_lines=len(code.splitlines()),
        )

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_metrics = self._analyze_function(node, file_path)
                metrics.functions.append(func_metrics)

        return metrics

    def _analyze_function(self, node: ast.FunctionDef, file_path: str) -> FunctionComplexity:
        """Analyze a single function."""
        cyclomatic = self._calculate_cyclomatic(node)
        cognitive = self._calculate_cognitive(node)

        return FunctionComplexity(
            name=node.name,
            file_path=file_path,
            line_number=node.lineno,
            cyclomatic_complexity=cyclomatic,
            cognitive_complexity=cognitive,
            lines_of_code=node.end_lineno - node.lineno + 1 if node.end_lineno else 0,
            parameter_count=len(node.args.args),
            nesting_depth=self._max_nesting(node),
        )

    def _calculate_cyclomatic(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.comprehension,)):
                complexity += 1
        return complexity

    def _calculate_cognitive(self, node: ast.AST, depth: int = 0) -> int:
        """Calculate cognitive complexity (nesting penalty)."""
        complexity = 0
        nesting_nodes = (ast.If, ast.While, ast.For, ast.Try, ast.With)

        for child in ast.iter_child_nodes(node):
            increment = 0
            child_depth = depth

            if isinstance(child, nesting_nodes):
                increment = 1 + depth
                child_depth = depth + 1
            elif isinstance(child, ast.BoolOp):
                increment = len(child.values) - 1

            complexity += increment
            complexity += self._calculate_cognitive(child, child_depth)

        return complexity

    def _max_nesting(self, node: ast.AST, current: int = 0) -> int:
        """Calculate maximum nesting depth."""
        max_depth = current
        nesting_nodes = (ast.If, ast.While, ast.For, ast.With, ast.Try)

        for child in ast.iter_child_nodes(node):
            if isinstance(child, nesting_nodes):
                child_depth = self._max_nesting(child, current + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._max_nesting(child, current)
                max_depth = max(max_depth, child_depth)

        return max_depth
```

### Step 4: Run tests, commit

```bash
pytest tests/agents/debt_analyzer/test_complexity.py -v
git add src/agents/debt_analyzer/ tests/agents/debt_analyzer/
git commit -m "feat(debt-analyzer): add complexity analyzer

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Code Duplication Detector

**Files:**
- Create: `src/agents/debt_analyzer/duplication.py`
- Test: `tests/agents/debt_analyzer/test_duplication.py`

### Implementation

```python
# src/agents/debt_analyzer/duplication.py
"""Code duplication detection."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DuplicateBlock:
    """A block of duplicated code."""
    content_hash: str
    lines: int
    occurrences: list[dict] = field(default_factory=list)  # [{file, start_line, end_line}]

    @property
    def total_duplicated_lines(self) -> int:
        return self.lines * (len(self.occurrences) - 1)


@dataclass
class DuplicationReport:
    """Report of code duplication."""
    duplicate_blocks: list[DuplicateBlock] = field(default_factory=list)
    total_lines: int = 0
    duplicated_lines: int = 0

    @property
    def duplication_percentage(self) -> float:
        if self.total_lines == 0:
            return 0.0
        return (self.duplicated_lines / self.total_lines) * 100


class DuplicationDetector:
    """Detects code duplication using content hashing."""

    def __init__(self, min_lines: int = 5, min_tokens: int = 50):
        self.min_lines = min_lines
        self.min_tokens = min_tokens

    def detect(self, files: dict[str, str]) -> DuplicationReport:
        """Detect duplication across multiple files."""
        # Extract code blocks
        blocks: dict[str, list[dict]] = {}  # hash -> occurrences

        for file_path, content in files.items():
            lines = content.splitlines()
            for i in range(len(lines) - self.min_lines + 1):
                block = "\n".join(lines[i:i + self.min_lines])
                normalized = self._normalize(block)

                if len(normalized.split()) < self.min_tokens:
                    continue

                block_hash = hashlib.md5(normalized.encode()).hexdigest()

                if block_hash not in blocks:
                    blocks[block_hash] = []

                blocks[block_hash].append({
                    "file": file_path,
                    "start_line": i + 1,
                    "end_line": i + self.min_lines,
                })

        # Build report
        duplicates = []
        for block_hash, occurrences in blocks.items():
            if len(occurrences) > 1:
                duplicates.append(DuplicateBlock(
                    content_hash=block_hash,
                    lines=self.min_lines,
                    occurrences=occurrences,
                ))

        total_lines = sum(len(c.splitlines()) for c in files.values())
        duplicated_lines = sum(d.total_duplicated_lines for d in duplicates)

        return DuplicationReport(
            duplicate_blocks=duplicates,
            total_lines=total_lines,
            duplicated_lines=duplicated_lines,
        )

    def _normalize(self, code: str) -> str:
        """Normalize code for comparison."""
        # Remove whitespace variations
        lines = [line.strip() for line in code.splitlines()]
        return "\n".join(line for line in lines if line)
```

---

## Task 3: Technical Debt Scorer

**Files:**
- Create: `src/agents/debt_analyzer/scorer.py`
- Test: `tests/agents/debt_analyzer/test_scorer.py`

### Implementation

```python
# src/agents/debt_analyzer/scorer.py
"""Technical debt scoring system."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


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
        DebtCategory.COMPLEXITY: 0.20,
        DebtCategory.DUPLICATION: 0.15,
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
                items.append(DebtItem(
                    category=DebtCategory.DUPLICATION,
                    file_path=block.occurrences[0]["file"],
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
```

---

## Task 4: DebtAnalyzer Agent and API

**Files:**
- Create: `src/agents/debt_analyzer/agent.py`
- Create: `src/api/routes/debt.py`
- Test: `tests/agents/debt_analyzer/test_agent.py`

### Implementation

```python
# src/agents/debt_analyzer/agent.py
"""DebtAnalyzer agent."""
from __future__ import annotations

from typing import Any

from src.core.agents import BaseAgent, AgentContext, TaskComplexity

from .complexity import ComplexityAnalyzer
from .duplication import DuplicationDetector
from .scorer import DebtScorer


class DebtAnalyzerAgent(BaseAgent):
    """Agent that analyzes technical debt in repositories."""

    name = "debt_analyzer"
    description = "Analyzes technical debt and provides refactoring priorities"
    complexity = TaskComplexity.MODERATE

    def __init__(self, llm_client: Any):
        super().__init__(llm_client)
        self.complexity_analyzer = ComplexityAnalyzer()
        self.duplication_detector = DuplicationDetector()
        self.scorer = DebtScorer()

    async def execute(
        self,
        context: AgentContext,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Analyze technical debt."""
        files = kwargs.get("files", {})  # {path: content}

        # Analyze complexity
        all_complexity = []
        for path, content in files.items():
            if path.endswith(".py"):
                metrics = self.complexity_analyzer.analyze(content, "python", path)
                all_complexity.append(metrics)

        # Detect duplication
        duplication = self.duplication_detector.detect(files)

        # Calculate score
        # Combine all function metrics
        combined_metrics = type('Metrics', (), {
            'functions': [f for m in all_complexity for f in m.functions]
        })()

        score = self.scorer.calculate_score(
            complexity_metrics=combined_metrics,
            duplication_report=duplication,
        )

        # Get AI-powered recommendations
        recommendations = await self._generate_recommendations(score)

        return {
            "score": score.score,
            "grade": score.grade,
            "total_debt_hours": score.total_debt_hours,
            "estimated_cost": score.estimated_cost,
            "debt_items": [
                {
                    "category": item.category.value,
                    "file": item.file_path,
                    "description": item.description,
                    "severity": item.severity,
                    "hours": item.estimated_hours,
                }
                for item in score.debt_items[:20]
            ],
            "duplication_percentage": duplication.duplication_percentage,
            "recommendations": recommendations,
        }

    async def _generate_recommendations(self, score: Any) -> list[str]:
        """Generate AI-powered refactoring recommendations."""
        if not score.debt_items:
            return ["Codebase is in good health!"]

        top_items = score.debt_items[:5]
        prompt = f"""Given these technical debt items, provide 3 prioritized recommendations:

{[f"- {item.description} ({item.severity})" for item in top_items]}

Return JSON: {{"recommendations": ["...", "...", "..."]}}
"""

        response = await self.llm_client.generate(
            prompt=prompt,
            system="You are a senior engineer prioritizing refactoring.",
            response_format={"type": "json_object"},
        )

        return response.get("recommendations", [])
```

---

## Summary

Phase 5 (DebtAnalyzer Agent) consists of 4 tasks:

1. **Code Complexity Analyzer** - Cyclomatic and cognitive complexity metrics
2. **Code Duplication Detector** - Hash-based duplicate detection
3. **Technical Debt Scorer** - Weighted scoring system with cost estimation
4. **DebtAnalyzer Agent & API** - Orchestration and REST endpoints

**Estimated Implementation Time:** ~1.5 weeks

**Dependencies:** Phase 1 (Foundation)
