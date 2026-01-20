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
