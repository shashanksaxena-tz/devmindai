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
