# DevMind AI Phase 4: TestGenerator Agent Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an intelligent test generation agent that analyzes code and generates comprehensive test suites including unit tests, integration tests, and edge cases.

**Architecture:** Multi-agent test generation pipeline with Analyzer (gap detection), Strategist (coverage planning), Generator (test writing), and Validator (test execution). Uses Claude for complex test generation and Gemini for analysis/validation.

**Tech Stack:** FastAPI, tree-sitter for AST parsing, pytest, Jest detection, Claude API, Gemini API, coverage.py integration

**Prerequisites:** Phase 1 (Foundation) completed

---

## Task 1: Code Analyzer and Coverage Gap Detection

**Files:**
- Create: `src/agents/test_generator/analyzer.py`
- Create: `src/agents/test_generator/coverage.py`
- Test: `tests/agents/test_generator/test_analyzer.py`

### Step 1: Write the failing tests

```python
# tests/agents/test_generator/test_analyzer.py
"""Tests for code analyzer and coverage detection."""
import pytest
from src.agents.test_generator.analyzer import (
    CodeAnalyzer,
    FunctionInfo,
    ClassInfo,
    ModuleAnalysis,
)
from src.agents.test_generator.coverage import (
    CoverageAnalyzer,
    CoverageGap,
    GapType,
)


class TestCodeAnalyzer:
    """Test CodeAnalyzer functionality."""

    @pytest.fixture
    def analyzer(self):
        """Create CodeAnalyzer instance."""
        return CodeAnalyzer()

    def test_extract_functions(self, analyzer):
        """Extract function definitions from Python code."""
        code = '''
def calculate_total(items: list[Item]) -> float:
    """Calculate total price."""
    return sum(item.price for item in items)

def apply_discount(total: float, discount: float) -> float:
    """Apply discount to total."""
    if discount < 0 or discount > 1:
        raise ValueError("Invalid discount")
    return total * (1 - discount)

async def fetch_prices(item_ids: list[int]) -> list[float]:
    """Fetch prices from API."""
    return await api.get_prices(item_ids)
'''
        result = analyzer.analyze(code, language="python")

        assert len(result.functions) == 3
        assert result.functions[0].name == "calculate_total"
        assert result.functions[0].is_async is False
        assert result.functions[1].name == "apply_discount"
        assert result.functions[2].name == "fetch_prices"
        assert result.functions[2].is_async is True

    def test_extract_classes(self, analyzer):
        """Extract class definitions with methods."""
        code = '''
class PaymentProcessor:
    """Process payments."""

    def __init__(self, gateway: Gateway):
        self.gateway = gateway

    def process(self, amount: float) -> Receipt:
        """Process a payment."""
        return self.gateway.charge(amount)

    async def refund(self, receipt_id: str) -> bool:
        """Refund a payment."""
        return await self.gateway.refund(receipt_id)
'''
        result = analyzer.analyze(code, language="python")

        assert len(result.classes) == 1
        cls = result.classes[0]
        assert cls.name == "PaymentProcessor"
        assert len(cls.methods) == 3  # __init__, process, refund
        assert cls.methods[1].name == "process"

    def test_extract_parameters(self, analyzer):
        """Extract function parameters with types."""
        code = '''
def create_user(
    email: str,
    name: str,
    age: int = 0,
    roles: list[str] | None = None,
) -> User:
    pass
'''
        result = analyzer.analyze(code, language="python")

        func = result.functions[0]
        assert len(func.parameters) == 4
        assert func.parameters[0].name == "email"
        assert func.parameters[0].type_hint == "str"
        assert func.parameters[2].name == "age"
        assert func.parameters[2].default == "0"
        assert func.return_type == "User"

    def test_detect_branches(self, analyzer):
        """Detect conditional branches for coverage."""
        code = '''
def categorize(value: int) -> str:
    if value < 0:
        return "negative"
    elif value == 0:
        return "zero"
    elif value < 100:
        return "small"
    else:
        return "large"
'''
        result = analyzer.analyze(code, language="python")

        func = result.functions[0]
        assert func.branch_count == 4
        assert func.complexity >= 4

    def test_analyze_javascript(self, analyzer):
        """Analyze JavaScript/TypeScript code."""
        code = '''
export function validateEmail(email: string): boolean {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

export async function sendEmail(to: string, subject: string): Promise<void> {
    await mailer.send({ to, subject });
}
'''
        result = analyzer.analyze(code, language="typescript")

        assert len(result.functions) == 2
        assert result.functions[0].name == "validateEmail"
        assert result.functions[1].is_async is True


class TestCoverageAnalyzer:
    """Test CoverageAnalyzer functionality."""

    @pytest.fixture
    def coverage_analyzer(self):
        """Create CoverageAnalyzer instance."""
        return CoverageAnalyzer()

    def test_identify_untested_functions(self, coverage_analyzer):
        """Find functions without any tests."""
        source_functions = [
            FunctionInfo(name="process_payment", file="payment.py", line=10),
            FunctionInfo(name="refund_payment", file="payment.py", line=30),
            FunctionInfo(name="validate_card", file="payment.py", line=50),
        ]
        test_coverage = {
            "payment.py::process_payment": True,
            "payment.py::validate_card": True,
        }

        gaps = coverage_analyzer.find_gaps(source_functions, test_coverage)

        assert len(gaps) == 1
        assert gaps[0].function_name == "refund_payment"
        assert gaps[0].gap_type == GapType.UNTESTED

    def test_identify_low_coverage(self, coverage_analyzer):
        """Find functions with low branch coverage."""
        coverage_data = {
            "payment.py::process_payment": {
                "line_coverage": 0.9,
                "branch_coverage": 0.3,
                "branches_covered": [1, 2],
                "branches_total": 6,
            },
        }

        gaps = coverage_analyzer.analyze_branch_coverage(coverage_data)

        assert len(gaps) >= 1
        assert gaps[0].gap_type == GapType.LOW_BRANCH_COVERAGE

    def test_identify_missing_edge_cases(self, coverage_analyzer):
        """Identify edge cases not covered by tests."""
        func_info = FunctionInfo(
            name="divide",
            parameters=[
                {"name": "a", "type": "float"},
                {"name": "b", "type": "float"},
            ],
            file="math_utils.py",
            line=5,
        )
        existing_tests = [
            {"name": "test_divide_positive", "inputs": [10, 2]},
            {"name": "test_divide_negative", "inputs": [-10, 2]},
        ]

        edge_cases = coverage_analyzer.suggest_edge_cases(func_info, existing_tests)

        assert any("zero" in ec.lower() for ec in edge_cases)  # Division by zero
        assert any("boundary" in ec.lower() or "large" in ec.lower() for ec in edge_cases)

    def test_parse_coverage_xml(self, coverage_analyzer):
        """Parse coverage.py XML output."""
        xml_content = '''<?xml version="1.0" ?>
<coverage version="7.0" timestamp="1234567890">
    <packages>
        <package name="src">
            <classes>
                <class name="payment.py" filename="src/payment.py" line-rate="0.85">
                    <methods>
                        <method name="process" line-rate="0.9"/>
                        <method name="refund" line-rate="0.5"/>
                    </methods>
                </class>
            </classes>
        </package>
    </packages>
</coverage>'''

        result = coverage_analyzer.parse_coverage_xml(xml_content)

        assert "src/payment.py" in result
        assert result["src/payment.py"]["line_rate"] == 0.85
```

### Step 2: Run tests to verify they fail

```bash
pytest tests/agents/test_generator/test_analyzer.py -v
```
Expected: FAIL with import errors

### Step 3: Implement the analyzer and coverage modules

```python
# src/agents/test_generator/__init__.py
"""TestGenerator agent module."""

# src/agents/test_generator/analyzer.py
"""Code analysis for test generation."""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ParameterInfo:
    """Information about a function parameter."""
    name: str
    type_hint: Optional[str] = None
    default: Optional[str] = None
    is_optional: bool = False


@dataclass
class FunctionInfo:
    """Information about a function or method."""
    name: str
    file: str = ""
    line: int = 0
    parameters: list[ParameterInfo] = field(default_factory=list)
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    is_async: bool = False
    is_method: bool = False
    is_private: bool = False
    is_static: bool = False
    is_classmethod: bool = False
    branch_count: int = 0
    complexity: int = 1
    decorators: list[str] = field(default_factory=list)


@dataclass
class ClassInfo:
    """Information about a class."""
    name: str
    file: str = ""
    line: int = 0
    methods: list[FunctionInfo] = field(default_factory=list)
    base_classes: list[str] = field(default_factory=list)
    docstring: Optional[str] = None
    is_abstract: bool = False


@dataclass
class ModuleAnalysis:
    """Analysis result for a module."""
    file_path: str
    language: str
    functions: list[FunctionInfo] = field(default_factory=list)
    classes: list[ClassInfo] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    global_variables: list[str] = field(default_factory=list)


class CodeAnalyzer:
    """Analyzes source code to extract testable elements."""

    def analyze(self, code: str, language: str, file_path: str = "") -> ModuleAnalysis:
        """Analyze code and extract functions, classes, etc."""
        if language in ("python", "py"):
            return self._analyze_python(code, file_path)
        elif language in ("javascript", "typescript", "js", "ts"):
            return self._analyze_javascript(code, file_path, language)
        else:
            # Fallback to regex-based analysis
            return self._analyze_generic(code, file_path, language)

    def _analyze_python(self, code: str, file_path: str) -> ModuleAnalysis:
        """Analyze Python code using AST."""
        result = ModuleAnalysis(file_path=file_path, language="python")

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return result

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                # Check if it's a method (inside a class)
                is_method = self._is_inside_class(tree, node)
                if not is_method:
                    func_info = self._extract_function_info(node, file_path)
                    result.functions.append(func_info)

            elif isinstance(node, ast.ClassDef):
                class_info = self._extract_class_info(node, file_path)
                result.classes.append(class_info)

            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports = self._extract_imports(node)
                result.imports.extend(imports)

        return result

    def _is_inside_class(self, tree: ast.AST, func_node: ast.AST) -> bool:
        """Check if a function is defined inside a class."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if item is func_node:
                        return True
        return False

    def _extract_function_info(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: str,
    ) -> FunctionInfo:
        """Extract information from a function node."""
        params = []
        for arg in node.args.args:
            param = ParameterInfo(name=arg.arg)
            if arg.annotation:
                param.type_hint = ast.unparse(arg.annotation)
            params.append(param)

        # Handle defaults
        defaults_offset = len(params) - len(node.args.defaults)
        for i, default in enumerate(node.args.defaults):
            params[defaults_offset + i].default = ast.unparse(default)
            params[defaults_offset + i].is_optional = True

        return_type = None
        if node.returns:
            return_type = ast.unparse(node.returns)

        docstring = ast.get_docstring(node)

        # Calculate complexity (simplified)
        branch_count = sum(
            1 for n in ast.walk(node)
            if isinstance(n, (ast.If, ast.For, ast.While, ast.Try,
                             ast.ExceptHandler, ast.With))
        )

        decorators = [
            ast.unparse(d) if hasattr(ast, 'unparse') else str(d)
            for d in node.decorator_list
        ]

        return FunctionInfo(
            name=node.name,
            file=file_path,
            line=node.lineno,
            parameters=params,
            return_type=return_type,
            docstring=docstring,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            is_private=node.name.startswith('_'),
            branch_count=branch_count,
            complexity=branch_count + 1,
            decorators=decorators,
        )

    def _extract_class_info(self, node: ast.ClassDef, file_path: str) -> ClassInfo:
        """Extract information from a class node."""
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_info = self._extract_function_info(item, file_path)
                method_info.is_method = True

                # Check for static/class methods
                for decorator in item.decorator_list:
                    if isinstance(decorator, ast.Name):
                        if decorator.id == 'staticmethod':
                            method_info.is_static = True
                        elif decorator.id == 'classmethod':
                            method_info.is_classmethod = True

                methods.append(method_info)

        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(ast.unparse(base))

        return ClassInfo(
            name=node.name,
            file=file_path,
            line=node.lineno,
            methods=methods,
            base_classes=bases,
            docstring=ast.get_docstring(node),
            is_abstract='ABC' in bases or 'ABCMeta' in bases,
        )

    def _extract_imports(self, node: ast.Import | ast.ImportFrom) -> list[str]:
        """Extract import statements."""
        imports = []
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                imports.append(f"{module}.{alias.name}")
        return imports

    def _analyze_javascript(
        self,
        code: str,
        file_path: str,
        language: str,
    ) -> ModuleAnalysis:
        """Analyze JavaScript/TypeScript using regex patterns."""
        result = ModuleAnalysis(file_path=file_path, language=language)

        # Function patterns
        func_patterns = [
            # export function name(params): type
            r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)(?:\s*:\s*(\w+(?:<[^>]+>)?))?',
            # const name = (params) => or async (params) =>
            r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*(?::\s*(\w+(?:<[^>]+>)?))?\s*=>',
        ]

        for pattern in func_patterns:
            for match in re.finditer(pattern, code, re.MULTILINE):
                func_name = match.group(1)
                is_async = 'async' in match.group(0)

                result.functions.append(FunctionInfo(
                    name=func_name,
                    file=file_path,
                    line=code[:match.start()].count('\n') + 1,
                    is_async=is_async,
                ))

        return result

    def _analyze_generic(
        self,
        code: str,
        file_path: str,
        language: str,
    ) -> ModuleAnalysis:
        """Generic analysis using common patterns."""
        result = ModuleAnalysis(file_path=file_path, language=language)

        # Look for function-like patterns
        func_pattern = r'(?:def|func|function|fn)\s+(\w+)'
        for match in re.finditer(func_pattern, code):
            result.functions.append(FunctionInfo(
                name=match.group(1),
                file=file_path,
                line=code[:match.start()].count('\n') + 1,
            ))

        return result
```

```python
# src/agents/test_generator/coverage.py
"""Coverage analysis for identifying test gaps."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from .analyzer import FunctionInfo


class GapType(Enum):
    """Types of coverage gaps."""
    UNTESTED = "untested"
    LOW_LINE_COVERAGE = "low_line_coverage"
    LOW_BRANCH_COVERAGE = "low_branch_coverage"
    MISSING_EDGE_CASE = "missing_edge_case"
    MISSING_ERROR_CASE = "missing_error_case"


@dataclass
class CoverageGap:
    """Represents a gap in test coverage."""
    function_name: str
    file_path: str
    gap_type: GapType
    description: str
    priority: int = 1  # 1 = highest
    suggested_tests: list[str] = None

    def __post_init__(self):
        if self.suggested_tests is None:
            self.suggested_tests = []


class CoverageAnalyzer:
    """Analyzes test coverage to identify gaps."""

    # Edge case patterns by type
    EDGE_CASE_PATTERNS = {
        "int": ["zero", "negative", "max_int", "min_int"],
        "float": ["zero", "negative", "infinity", "nan", "very_small"],
        "str": ["empty_string", "whitespace", "unicode", "very_long"],
        "list": ["empty_list", "single_element", "large_list", "nested"],
        "dict": ["empty_dict", "missing_key", "nested_dict"],
        "Optional": ["none_value", "some_value"],
        "bool": ["true", "false"],
    }

    def find_gaps(
        self,
        source_functions: list[FunctionInfo],
        test_coverage: dict[str, bool],
    ) -> list[CoverageGap]:
        """Find functions that lack test coverage."""
        gaps = []

        for func in source_functions:
            coverage_key = f"{func.file}::{func.name}"

            if not test_coverage.get(coverage_key, False):
                gaps.append(CoverageGap(
                    function_name=func.name,
                    file_path=func.file,
                    gap_type=GapType.UNTESTED,
                    description=f"Function '{func.name}' has no tests",
                    priority=1 if not func.is_private else 3,
                ))

        return gaps

    def analyze_branch_coverage(
        self,
        coverage_data: dict[str, dict[str, Any]],
        threshold: float = 0.7,
    ) -> list[CoverageGap]:
        """Find functions with low branch coverage."""
        gaps = []

        for func_key, data in coverage_data.items():
            branch_coverage = data.get("branch_coverage", 1.0)

            if branch_coverage < threshold:
                file_path, func_name = func_key.split("::")
                gaps.append(CoverageGap(
                    function_name=func_name,
                    file_path=file_path,
                    gap_type=GapType.LOW_BRANCH_COVERAGE,
                    description=(
                        f"Function '{func_name}' has {branch_coverage:.0%} "
                        f"branch coverage (threshold: {threshold:.0%})"
                    ),
                    priority=2,
                ))

        return gaps

    def suggest_edge_cases(
        self,
        func_info: FunctionInfo,
        existing_tests: list[dict[str, Any]],
    ) -> list[str]:
        """Suggest edge cases not covered by existing tests."""
        suggestions = []
        covered_patterns = set()

        # Analyze existing test inputs
        for test in existing_tests:
            inputs = test.get("inputs", [])
            for inp in inputs:
                if inp == 0:
                    covered_patterns.add("zero")
                elif isinstance(inp, (int, float)) and inp < 0:
                    covered_patterns.add("negative")
                elif inp == "":
                    covered_patterns.add("empty_string")
                elif inp is None:
                    covered_patterns.add("none_value")

        # Suggest missing edge cases based on parameter types
        for param in func_info.parameters:
            param_dict = param if isinstance(param, dict) else {
                "name": param.name,
                "type": getattr(param, 'type_hint', None),
            }

            param_type = param_dict.get("type", "")
            param_name = param_dict.get("name", "")

            for base_type, cases in self.EDGE_CASE_PATTERNS.items():
                if base_type.lower() in str(param_type).lower():
                    for case in cases:
                        if case not in covered_patterns:
                            suggestions.append(
                                f"Test {param_name} with {case} "
                                f"(boundary/edge case for {base_type})"
                            )

        # Add common edge cases
        if "zero" not in covered_patterns:
            suggestions.append("Test with zero value (boundary condition)")
        if "negative" not in covered_patterns:
            suggestions.append("Test with negative value (boundary condition)")
        if "large" not in covered_patterns:
            suggestions.append("Test with large value (stress/boundary test)")

        return suggestions

    def parse_coverage_xml(self, xml_content: str) -> dict[str, dict[str, Any]]:
        """Parse coverage.py XML output."""
        result = {}

        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError:
            return result

        for package in root.findall(".//package"):
            for cls in package.findall(".//class"):
                filename = cls.get("filename", "")
                line_rate = float(cls.get("line-rate", 0))

                result[filename] = {
                    "line_rate": line_rate,
                    "methods": {},
                }

                for method in cls.findall(".//method"):
                    method_name = method.get("name", "")
                    method_rate = float(method.get("line-rate", 0))
                    result[filename]["methods"][method_name] = {
                        "line_rate": method_rate,
                    }

        return result

    def identify_error_paths(
        self,
        func_info: FunctionInfo,
        existing_tests: list[dict[str, Any]],
    ) -> list[CoverageGap]:
        """Identify error handling paths not covered by tests."""
        gaps = []

        # Check for exception testing
        has_error_test = any(
            "error" in t.get("name", "").lower() or
            "exception" in t.get("name", "").lower() or
            "raise" in t.get("name", "").lower() or
            "invalid" in t.get("name", "").lower()
            for t in existing_tests
        )

        if not has_error_test and func_info.complexity > 1:
            gaps.append(CoverageGap(
                function_name=func_info.name,
                file_path=func_info.file,
                gap_type=GapType.MISSING_ERROR_CASE,
                description=f"No error case tests for '{func_info.name}'",
                priority=2,
                suggested_tests=[
                    "Test with invalid input types",
                    "Test with values that trigger exceptions",
                    "Test error handling and recovery",
                ],
            ))

        return gaps
```

### Step 4: Run tests to verify they pass

```bash
pytest tests/agents/test_generator/test_analyzer.py -v
```
Expected: All tests PASS

### Step 5: Commit

```bash
git add src/agents/test_generator/ tests/agents/test_generator/
git commit -m "feat(test-generator): add code analyzer and coverage detection

- Implement Python AST-based code analysis
- Add JavaScript/TypeScript regex-based analysis
- Implement coverage gap detection
- Add edge case suggestion based on parameter types

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Test Strategy Planner

**Files:**
- Create: `src/agents/test_generator/strategist.py`
- Test: `tests/agents/test_generator/test_strategist.py`

### Step 1: Write the failing tests

```python
# tests/agents/test_generator/test_strategist.py
"""Tests for test strategy planner."""
import pytest
from unittest.mock import AsyncMock

from src.agents.test_generator.strategist import (
    TestStrategist,
    TestStrategy,
    TestPriority,
    TestType,
)
from src.agents.test_generator.analyzer import FunctionInfo, ClassInfo


class TestTestStrategist:
    """Test TestStrategist agent."""

    @pytest.fixture
    def strategist(self):
        """Create TestStrategist instance."""
        mock_llm = AsyncMock()
        return TestStrategist(llm_client=mock_llm)

    @pytest.mark.asyncio
    async def test_prioritize_critical_functions(self, strategist):
        """Critical functions should be prioritized."""
        functions = [
            FunctionInfo(name="process_payment", complexity=5),
            FunctionInfo(name="format_name", complexity=1),
            FunctionInfo(name="validate_auth", complexity=3),
        ]

        strategist.llm_client.generate.return_value = {
            "priorities": [
                {"name": "process_payment", "priority": "critical", "reason": "Handles money"},
                {"name": "validate_auth", "priority": "high", "reason": "Security"},
                {"name": "format_name", "priority": "low", "reason": "Simple utility"},
            ]
        }

        strategy = await strategist.plan_tests(functions)

        assert strategy.prioritized_targets[0].function_name == "process_payment"
        assert strategy.prioritized_targets[0].priority == TestPriority.CRITICAL

    @pytest.mark.asyncio
    async def test_determine_test_types(self, strategist):
        """Determine appropriate test types for each function."""
        func = FunctionInfo(
            name="save_user",
            parameters=[
                {"name": "user", "type": "User"},
                {"name": "db", "type": "Database"},
            ],
            is_async=True,
        )

        strategist.llm_client.generate.return_value = {
            "test_types": ["unit", "integration"],
            "reason": "Uses external database dependency",
        }

        test_types = await strategist.determine_test_types(func)

        assert TestType.UNIT in test_types
        assert TestType.INTEGRATION in test_types

    @pytest.mark.asyncio
    async def test_identify_edge_cases(self, strategist):
        """Identify edge cases for a function."""
        func = FunctionInfo(
            name="divide",
            parameters=[
                {"name": "a", "type": "float"},
                {"name": "b", "type": "float"},
            ],
            return_type="float",
        )

        strategist.llm_client.generate.return_value = {
            "edge_cases": [
                {"input": {"a": 0, "b": 5}, "expected": 0, "description": "Zero numerator"},
                {"input": {"a": 5, "b": 0}, "expected": "ZeroDivisionError", "description": "Division by zero"},
                {"input": {"a": float("inf"), "b": 2}, "expected": "inf", "description": "Infinity"},
            ]
        }

        edge_cases = await strategist.identify_edge_cases(func)

        assert len(edge_cases) >= 3
        assert any("zero" in ec["description"].lower() for ec in edge_cases)

    @pytest.mark.asyncio
    async def test_plan_class_tests(self, strategist):
        """Plan tests for a class with methods."""
        cls = ClassInfo(
            name="UserService",
            methods=[
                FunctionInfo(name="__init__"),
                FunctionInfo(name="create_user", complexity=3),
                FunctionInfo(name="delete_user", complexity=2),
                FunctionInfo(name="_validate", is_private=True),
            ],
        )

        strategist.llm_client.generate.return_value = {
            "class_strategy": {
                "test_fixture": "user_service",
                "shared_setup": "Create mock database",
                "methods_to_test": ["create_user", "delete_user"],
                "skip_private": True,
            }
        }

        strategy = await strategist.plan_class_tests(cls)

        assert strategy.fixture_name == "user_service"
        assert "create_user" in strategy.methods_to_test
        assert "_validate" not in strategy.methods_to_test

    @pytest.mark.asyncio
    async def test_estimate_coverage_impact(self, strategist):
        """Estimate coverage impact of planned tests."""
        strategy = TestStrategy(
            prioritized_targets=[
                {"function_name": "func1", "test_count": 5},
                {"function_name": "func2", "test_count": 3},
            ],
            total_functions=10,
            current_coverage=0.5,
        )

        estimated = strategist.estimate_coverage_impact(strategy)

        assert estimated > 0.5
        assert estimated <= 1.0
```

### Step 2: Run tests to verify they fail

```bash
pytest tests/agents/test_generator/test_strategist.py -v
```
Expected: FAIL

### Step 3: Implement the strategist

```python
# src/agents/test_generator/strategist.py
"""Test strategy planning agent."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from .analyzer import FunctionInfo, ClassInfo


class TestPriority(Enum):
    """Priority levels for testing."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TestType(Enum):
    """Types of tests to generate."""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PROPERTY = "property"
    REGRESSION = "regression"


@dataclass
class TestTarget:
    """A function/method targeted for testing."""
    function_name: str
    priority: TestPriority
    test_types: list[TestType] = field(default_factory=list)
    edge_cases: list[dict[str, Any]] = field(default_factory=list)
    reason: str = ""
    estimated_tests: int = 1


@dataclass
class ClassTestStrategy:
    """Strategy for testing a class."""
    class_name: str
    fixture_name: str
    shared_setup: str
    methods_to_test: list[str] = field(default_factory=list)
    isolation_required: bool = False


@dataclass
class TestStrategy:
    """Complete test strategy for a module."""
    prioritized_targets: list[TestTarget] = field(default_factory=list)
    total_functions: int = 0
    current_coverage: float = 0.0
    estimated_new_coverage: float = 0.0
    class_strategies: list[ClassTestStrategy] = field(default_factory=list)
    recommended_frameworks: list[str] = field(default_factory=list)


class TestStrategist:
    """Plans test generation strategy."""

    PRIORITY_KEYWORDS = {
        TestPriority.CRITICAL: ["payment", "auth", "security", "password", "money", "transaction"],
        TestPriority.HIGH: ["user", "api", "validate", "process", "handle"],
        TestPriority.MEDIUM: ["format", "parse", "convert", "calculate"],
        TestPriority.LOW: ["log", "print", "debug", "helper"],
    }

    def __init__(self, llm_client: Any):
        """Initialize with LLM client."""
        self.llm_client = llm_client

    async def plan_tests(
        self,
        functions: list[FunctionInfo],
        classes: list[ClassInfo] | None = None,
        existing_coverage: dict[str, float] | None = None,
    ) -> TestStrategy:
        """Create a comprehensive test strategy."""
        # Get LLM-assisted prioritization
        priority_response = await self._get_priorities(functions)

        prioritized_targets = []
        for priority_info in priority_response.get("priorities", []):
            func_name = priority_info["name"]
            priority_str = priority_info.get("priority", "medium")

            try:
                priority = TestPriority(priority_str)
            except ValueError:
                priority = TestPriority.MEDIUM

            target = TestTarget(
                function_name=func_name,
                priority=priority,
                reason=priority_info.get("reason", ""),
            )
            prioritized_targets.append(target)

        # Sort by priority
        priority_order = [TestPriority.CRITICAL, TestPriority.HIGH,
                         TestPriority.MEDIUM, TestPriority.LOW]
        prioritized_targets.sort(
            key=lambda t: priority_order.index(t.priority)
        )

        strategy = TestStrategy(
            prioritized_targets=prioritized_targets,
            total_functions=len(functions),
            current_coverage=sum(existing_coverage.values()) / len(existing_coverage)
            if existing_coverage else 0.0,
        )

        # Plan class tests if provided
        if classes:
            for cls in classes:
                cls_strategy = await self.plan_class_tests(cls)
                strategy.class_strategies.append(cls_strategy)

        return strategy

    async def _get_priorities(
        self,
        functions: list[FunctionInfo],
    ) -> dict[str, Any]:
        """Get LLM-assisted function prioritization."""
        func_descriptions = "\n".join([
            f"- {f.name}: complexity={f.complexity}, async={f.is_async}"
            for f in functions[:20]  # Limit for context
        ])

        prompt = f"""Prioritize these functions for testing:

{func_descriptions}

For each function, assign a priority:
- critical: Security, payments, data integrity
- high: Core business logic, user-facing
- medium: Important utilities
- low: Simple helpers, logging

Return JSON: {{"priorities": [{{"name": "...", "priority": "...", "reason": "..."}}]}}
"""

        return await self.llm_client.generate(
            prompt=prompt,
            system="You are a QA expert prioritizing test coverage.",
            response_format={"type": "json_object"},
        )

    async def determine_test_types(
        self,
        func: FunctionInfo,
    ) -> list[TestType]:
        """Determine appropriate test types for a function."""
        prompt = f"""Determine test types for this function:

Name: {func.name}
Parameters: {[(p.name, p.type_hint) for p in func.parameters]}
Async: {func.is_async}
Complexity: {func.complexity}

Choose from: unit, integration, e2e, property, regression
Return JSON: {{"test_types": [...], "reason": "..."}}
"""

        response = await self.llm_client.generate(
            prompt=prompt,
            system="You are a QA expert.",
            response_format={"type": "json_object"},
        )

        test_types = []
        for type_str in response.get("test_types", ["unit"]):
            try:
                test_types.append(TestType(type_str))
            except ValueError:
                pass

        return test_types or [TestType.UNIT]

    async def identify_edge_cases(
        self,
        func: FunctionInfo,
    ) -> list[dict[str, Any]]:
        """Identify edge cases for a function."""
        params_str = ", ".join([
            f"{p.name}: {p.type_hint or 'any'}"
            for p in func.parameters
        ])

        prompt = f"""Identify edge cases for testing:

Function: {func.name}({params_str}) -> {func.return_type or 'any'}
Docstring: {func.docstring or 'None'}

List edge cases with:
- input: parameter values
- expected: expected result or exception
- description: what this tests

Return JSON: {{"edge_cases": [...]}}
"""

        response = await self.llm_client.generate(
            prompt=prompt,
            system="You are a QA expert finding edge cases.",
            response_format={"type": "json_object"},
        )

        return response.get("edge_cases", [])

    async def plan_class_tests(self, cls: ClassInfo) -> ClassTestStrategy:
        """Plan tests for a class."""
        public_methods = [m.name for m in cls.methods if not m.is_private]

        prompt = f"""Plan tests for this class:

Class: {cls.name}
Methods: {public_methods}
Base classes: {cls.base_classes}

Return JSON:
- fixture_name: pytest fixture name
- shared_setup: setup description
- methods_to_test: list of public method names
- skip_private: boolean
"""

        response = await self.llm_client.generate(
            prompt=prompt,
            system="You are a QA expert planning class tests.",
            response_format={"type": "json_object"},
        )

        strategy_data = response.get("class_strategy", response)

        return ClassTestStrategy(
            class_name=cls.name,
            fixture_name=strategy_data.get("fixture_name", cls.name.lower()),
            shared_setup=strategy_data.get("shared_setup", ""),
            methods_to_test=strategy_data.get("methods_to_test", public_methods),
        )

    def estimate_coverage_impact(self, strategy: TestStrategy) -> float:
        """Estimate new coverage after implementing the strategy."""
        if strategy.total_functions == 0:
            return strategy.current_coverage

        # Estimate based on targets and their priority
        new_covered = 0
        for target in strategy.prioritized_targets:
            weight = {
                TestPriority.CRITICAL: 1.0,
                TestPriority.HIGH: 0.8,
                TestPriority.MEDIUM: 0.6,
                TestPriority.LOW: 0.4,
            }.get(target.priority, 0.5)

            new_covered += weight

        # Calculate estimated coverage
        current_covered = strategy.current_coverage * strategy.total_functions
        estimated_covered = min(
            current_covered + new_covered,
            strategy.total_functions
        )

        return estimated_covered / strategy.total_functions
```

### Step 4: Run tests to verify they pass

```bash
pytest tests/agents/test_generator/test_strategist.py -v
```
Expected: All tests PASS

### Step 5: Commit

```bash
git add src/agents/test_generator/strategist.py tests/agents/test_generator/
git commit -m "feat(test-generator): add test strategy planner

- Implement priority-based test planning
- Add test type determination (unit, integration, e2e)
- Add edge case identification
- Add class test strategy planning

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Test Code Generator

**Files:**
- Create: `src/agents/test_generator/generator.py`
- Create: `src/agents/test_generator/templates/`
- Test: `tests/agents/test_generator/test_generator.py`

### Step 1: Write the failing tests

```python
# tests/agents/test_generator/test_generator.py
"""Tests for test code generator."""
import pytest
from unittest.mock import AsyncMock

from src.agents.test_generator.generator import (
    TestGenerator,
    GeneratedTest,
    TestFramework,
)
from src.agents.test_generator.analyzer import FunctionInfo, ParameterInfo
from src.agents.test_generator.strategist import TestTarget, TestPriority, TestType


class TestTestGenerator:
    """Test TestGenerator agent."""

    @pytest.fixture
    def generator(self):
        """Create TestGenerator instance."""
        mock_llm = AsyncMock()
        return TestGenerator(llm_client=mock_llm)

    @pytest.mark.asyncio
    async def test_generate_unit_test_python(self, generator):
        """Generate pytest unit test."""
        func = FunctionInfo(
            name="calculate_total",
            file="src/cart.py",
            parameters=[
                ParameterInfo(name="items", type_hint="list[Item]"),
                ParameterInfo(name="discount", type_hint="float", default="0.0"),
            ],
            return_type="float",
            docstring="Calculate total price with optional discount.",
        )

        generator.llm_client.generate.return_value = {
            "tests": [
                {
                    "name": "test_calculate_total_basic",
                    "code": '''def test_calculate_total_basic():
    items = [Item(price=10.0), Item(price=20.0)]
    result = calculate_total(items)
    assert result == 30.0''',
                    "description": "Basic calculation without discount",
                },
                {
                    "name": "test_calculate_total_with_discount",
                    "code": '''def test_calculate_total_with_discount():
    items = [Item(price=100.0)]
    result = calculate_total(items, discount=0.1)
    assert result == 90.0''',
                    "description": "Calculation with 10% discount",
                },
            ]
        }

        tests = await generator.generate_tests(
            func,
            framework=TestFramework.PYTEST,
            test_types=[TestType.UNIT],
        )

        assert len(tests) >= 2
        assert "def test_" in tests[0].code
        assert "assert" in tests[0].code

    @pytest.mark.asyncio
    async def test_generate_test_with_mocks(self, generator):
        """Generate test with proper mocking."""
        func = FunctionInfo(
            name="send_notification",
            file="src/notifications.py",
            parameters=[
                ParameterInfo(name="user_id", type_hint="int"),
                ParameterInfo(name="message", type_hint="str"),
            ],
            is_async=True,
        )

        generator.llm_client.generate.return_value = {
            "tests": [{
                "name": "test_send_notification",
                "code": '''@pytest.mark.asyncio
async def test_send_notification():
    with patch("src.notifications.email_service") as mock_email:
        mock_email.send.return_value = True
        result = await send_notification(123, "Hello")
        mock_email.send.assert_called_once()''',
                "imports": ["from unittest.mock import patch"],
            }]
        }

        tests = await generator.generate_tests(func, framework=TestFramework.PYTEST)

        assert "patch" in tests[0].code or "mock" in tests[0].code.lower()

    @pytest.mark.asyncio
    async def test_generate_edge_case_tests(self, generator):
        """Generate tests for edge cases."""
        func = FunctionInfo(
            name="divide",
            parameters=[
                ParameterInfo(name="a", type_hint="float"),
                ParameterInfo(name="b", type_hint="float"),
            ],
            return_type="float",
        )

        edge_cases = [
            {"input": {"a": 0, "b": 5}, "expected": 0},
            {"input": {"a": 5, "b": 0}, "expected": "raises ZeroDivisionError"},
            {"input": {"a": -10, "b": 2}, "expected": -5},
        ]

        generator.llm_client.generate.return_value = {
            "tests": [
                {
                    "name": "test_divide_zero_numerator",
                    "code": "def test_divide_zero_numerator():\n    assert divide(0, 5) == 0",
                },
                {
                    "name": "test_divide_by_zero_raises",
                    "code": "def test_divide_by_zero_raises():\n    with pytest.raises(ZeroDivisionError):\n        divide(5, 0)",
                },
            ]
        }

        tests = await generator.generate_edge_case_tests(func, edge_cases)

        assert len(tests) >= 2
        assert any("raises" in t.code.lower() for t in tests)

    @pytest.mark.asyncio
    async def test_generate_jest_test(self, generator):
        """Generate Jest test for JavaScript."""
        func = FunctionInfo(
            name="validateEmail",
            file="src/validators.ts",
            parameters=[ParameterInfo(name="email", type_hint="string")],
            return_type="boolean",
        )

        generator.llm_client.generate.return_value = {
            "tests": [{
                "name": "validateEmail returns true for valid email",
                "code": '''test('validateEmail returns true for valid email', () => {
    expect(validateEmail('test@example.com')).toBe(true);
});''',
            }]
        }

        tests = await generator.generate_tests(
            func,
            framework=TestFramework.JEST,
        )

        assert "test(" in tests[0].code or "it(" in tests[0].code
        assert "expect" in tests[0].code

    @pytest.mark.asyncio
    async def test_generate_parametrized_test(self, generator):
        """Generate parametrized test."""
        func = FunctionInfo(
            name="is_valid_age",
            parameters=[ParameterInfo(name="age", type_hint="int")],
            return_type="bool",
        )

        test_cases = [
            (0, False),
            (17, False),
            (18, True),
            (100, True),
            (150, False),
        ]

        generator.llm_client.generate.return_value = {
            "tests": [{
                "name": "test_is_valid_age_parametrized",
                "code": '''@pytest.mark.parametrize("age,expected", [
    (0, False),
    (17, False),
    (18, True),
    (100, True),
    (150, False),
])
def test_is_valid_age_parametrized(age, expected):
    assert is_valid_age(age) == expected''',
            }]
        }

        tests = await generator.generate_parametrized_test(func, test_cases)

        assert "@pytest.mark.parametrize" in tests[0].code

    def test_format_test_file(self, generator):
        """Format multiple tests into a complete test file."""
        tests = [
            GeneratedTest(
                name="test_func1",
                code="def test_func1():\n    assert True",
                imports=["import pytest"],
            ),
            GeneratedTest(
                name="test_func2",
                code="def test_func2():\n    assert True",
                imports=["from unittest.mock import patch"],
            ),
        ]

        file_content = generator.format_test_file(
            tests,
            source_module="src.mymodule",
            framework=TestFramework.PYTEST,
        )

        assert "import pytest" in file_content
        assert "from unittest.mock import patch" in file_content
        assert "from src.mymodule import" in file_content
        assert "def test_func1" in file_content
        assert "def test_func2" in file_content
```

### Step 2: Run tests to verify they fail

```bash
pytest tests/agents/test_generator/test_generator.py -v
```
Expected: FAIL

### Step 3: Implement the generator

```python
# src/agents/test_generator/generator.py
"""Test code generation agent."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from .analyzer import FunctionInfo, ClassInfo
from .strategist import TestType


class TestFramework(Enum):
    """Supported test frameworks."""
    PYTEST = "pytest"
    UNITTEST = "unittest"
    JEST = "jest"
    VITEST = "vitest"
    MOCHA = "mocha"
    JUNIT = "junit"
    GO_TEST = "go_test"


@dataclass
class GeneratedTest:
    """A generated test case."""
    name: str
    code: str
    description: str = ""
    imports: list[str] = field(default_factory=list)
    fixtures: list[str] = field(default_factory=list)
    test_type: TestType = TestType.UNIT


class TestGenerator:
    """Generates test code using LLM."""

    FRAMEWORK_TEMPLATES = {
        TestFramework.PYTEST: {
            "test_prefix": "def test_",
            "async_prefix": "async def test_",
            "async_decorator": "@pytest.mark.asyncio",
            "parametrize": "@pytest.mark.parametrize",
            "raises": "pytest.raises",
            "imports": ["import pytest"],
        },
        TestFramework.JEST: {
            "test_prefix": "test('",
            "async_prefix": "test('",
            "describe": "describe('",
            "expect": "expect(",
            "imports": [],
        },
    }

    def __init__(self, llm_client: Any):
        """Initialize with LLM client."""
        self.llm_client = llm_client

    async def generate_tests(
        self,
        func: FunctionInfo,
        framework: TestFramework = TestFramework.PYTEST,
        test_types: list[TestType] | None = None,
        context: Optional[str] = None,
    ) -> list[GeneratedTest]:
        """Generate tests for a function."""
        test_types = test_types or [TestType.UNIT]
        template = self.FRAMEWORK_TEMPLATES.get(framework, {})

        params_str = ", ".join([
            f"{p.name}: {p.type_hint or 'any'}"
            + (f" = {p.default}" if p.default else "")
            for p in func.parameters
        ])

        prompt = f"""Generate tests for this function:

```python
def {func.name}({params_str}) -> {func.return_type or 'any'}:
    \"\"\"{func.docstring or 'No docstring'}\"\"\"
    ...
```

Framework: {framework.value}
Test types needed: {[t.value for t in test_types]}
Function is async: {func.is_async}

Generate comprehensive tests including:
1. Happy path with typical inputs
2. Edge cases (empty, zero, negative, etc.)
3. Error cases if applicable

Return JSON:
{{
  "tests": [
    {{
      "name": "test_function_name_scenario",
      "code": "complete test function code",
      "description": "what this test verifies",
      "imports": ["any additional imports needed"]
    }}
  ]
}}
"""

        response = await self.llm_client.generate(
            prompt=prompt,
            system=f"You are a test engineer generating {framework.value} tests.",
            response_format={"type": "json_object"},
        )

        tests = []
        for test_data in response.get("tests", []):
            test = GeneratedTest(
                name=test_data.get("name", "test_unnamed"),
                code=test_data.get("code", ""),
                description=test_data.get("description", ""),
                imports=test_data.get("imports", []),
            )
            tests.append(test)

        return tests

    async def generate_edge_case_tests(
        self,
        func: FunctionInfo,
        edge_cases: list[dict[str, Any]],
        framework: TestFramework = TestFramework.PYTEST,
    ) -> list[GeneratedTest]:
        """Generate tests specifically for edge cases."""
        cases_str = "\n".join([
            f"- Input: {ec.get('input')}, Expected: {ec.get('expected')}"
            for ec in edge_cases
        ])

        prompt = f"""Generate edge case tests for {func.name}:

Edge cases to test:
{cases_str}

Framework: {framework.value}

For exception cases, use pytest.raises or equivalent.
Return JSON with "tests" array.
"""

        response = await self.llm_client.generate(
            prompt=prompt,
            system="You are a test engineer focusing on edge cases.",
            response_format={"type": "json_object"},
        )

        tests = []
        for test_data in response.get("tests", []):
            test = GeneratedTest(
                name=test_data.get("name", "test_edge_case"),
                code=test_data.get("code", ""),
                description=test_data.get("description", ""),
                imports=test_data.get("imports", []),
            )
            tests.append(test)

        return tests

    async def generate_parametrized_test(
        self,
        func: FunctionInfo,
        test_cases: list[tuple],
        framework: TestFramework = TestFramework.PYTEST,
    ) -> list[GeneratedTest]:
        """Generate a parametrized test."""
        cases_str = str(test_cases)

        prompt = f"""Generate a parametrized test for {func.name}:

Test cases (input, expected):
{cases_str}

Framework: {framework.value}

Use @pytest.mark.parametrize for pytest.
Return JSON with single test in "tests" array.
"""

        response = await self.llm_client.generate(
            prompt=prompt,
            system="You are a test engineer.",
            response_format={"type": "json_object"},
        )

        tests = []
        for test_data in response.get("tests", []):
            test = GeneratedTest(
                name=test_data.get("name", "test_parametrized"),
                code=test_data.get("code", ""),
                imports=["import pytest"],
            )
            tests.append(test)

        return tests

    async def generate_class_tests(
        self,
        cls: ClassInfo,
        framework: TestFramework = TestFramework.PYTEST,
    ) -> list[GeneratedTest]:
        """Generate tests for a class."""
        methods_str = "\n".join([
            f"- {m.name}({', '.join([p.name for p in m.parameters])})"
            for m in cls.methods
            if not m.is_private
        ])

        prompt = f"""Generate tests for this class:

Class: {cls.name}
Base classes: {cls.base_classes}
Methods:
{methods_str}

Framework: {framework.value}

Include:
1. Fixture for class instantiation
2. Tests for each public method
3. Integration between methods if applicable

Return JSON with "tests" array.
"""

        response = await self.llm_client.generate(
            prompt=prompt,
            system="You are a test engineer.",
            response_format={"type": "json_object"},
        )

        tests = []
        for test_data in response.get("tests", []):
            test = GeneratedTest(
                name=test_data.get("name", "test_class"),
                code=test_data.get("code", ""),
                description=test_data.get("description", ""),
                imports=test_data.get("imports", []),
                fixtures=test_data.get("fixtures", []),
            )
            tests.append(test)

        return tests

    def format_test_file(
        self,
        tests: list[GeneratedTest],
        source_module: str,
        framework: TestFramework = TestFramework.PYTEST,
    ) -> str:
        """Format tests into a complete test file."""
        lines = []

        # Collect unique imports
        all_imports = set()
        for test in tests:
            all_imports.update(test.imports)

        # Add framework imports
        template = self.FRAMEWORK_TEMPLATES.get(framework, {})
        all_imports.update(template.get("imports", []))

        # Add source import
        module_name = source_module.replace("/", ".").replace(".py", "")
        func_names = [t.name.replace("test_", "").split("_")[0] for t in tests]
        all_imports.add(f"from {module_name} import {', '.join(set(func_names))}")

        # Write imports
        for imp in sorted(all_imports):
            lines.append(imp)

        lines.append("")
        lines.append("")

        # Write tests
        for test in tests:
            if test.description:
                lines.append(f"# {test.description}")
            lines.append(test.code)
            lines.append("")
            lines.append("")

        return "\n".join(lines).strip() + "\n"
```

### Step 4: Run tests to verify they pass

```bash
pytest tests/agents/test_generator/test_generator.py -v
```
Expected: All tests PASS

### Step 5: Commit

```bash
git add src/agents/test_generator/generator.py tests/agents/test_generator/
git commit -m "feat(test-generator): add test code generator

- Implement LLM-powered test generation
- Support pytest and Jest frameworks
- Add edge case and parametrized test generation
- Add test file formatting

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Test Validator and Runner

**Files:**
- Create: `src/agents/test_generator/validator.py`
- Test: `tests/agents/test_generator/test_validator.py`

### Step 1: Write the failing tests

```python
# tests/agents/test_generator/test_validator.py
"""Tests for test validator."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.agents.test_generator.validator import (
    TestValidator,
    ValidationResult,
    TestExecutionResult,
)
from src.agents.test_generator.generator import GeneratedTest


class TestTestValidator:
    """Test TestValidator functionality."""

    @pytest.fixture
    def validator(self):
        """Create TestValidator instance."""
        return TestValidator()

    def test_validate_syntax_python(self, validator):
        """Validate Python test syntax."""
        valid_test = GeneratedTest(
            name="test_valid",
            code='''def test_valid():
    result = 1 + 1
    assert result == 2''',
        )

        result = validator.validate_syntax(valid_test, language="python")

        assert result.is_valid is True
        assert result.errors == []

    def test_detect_syntax_error(self, validator):
        """Detect syntax errors in tests."""
        invalid_test = GeneratedTest(
            name="test_invalid",
            code='''def test_invalid()
    assert True''',  # Missing colon
        )

        result = validator.validate_syntax(invalid_test, language="python")

        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_validate_assertions_present(self, validator):
        """Ensure tests have assertions."""
        no_assertion_test = GeneratedTest(
            name="test_no_assert",
            code='''def test_no_assert():
    result = calculate(1, 2)
    print(result)''',
        )

        result = validator.validate_assertions(no_assertion_test)

        assert result.is_valid is False
        assert "assertion" in result.errors[0].lower()

    def test_detect_flaky_patterns(self, validator):
        """Detect potentially flaky test patterns."""
        flaky_test = GeneratedTest(
            name="test_flaky",
            code='''def test_flaky():
    import time
    time.sleep(1)
    assert datetime.now().second == 30''',
        )

        result = validator.detect_flaky_patterns(flaky_test)

        assert len(result.warnings) > 0
        assert any("time" in w.lower() or "flaky" in w.lower() for w in result.warnings)

    @pytest.mark.asyncio
    async def test_run_test(self, validator):
        """Execute a test and get results."""
        test = GeneratedTest(
            name="test_passes",
            code='''def test_passes():
    assert 1 + 1 == 2''',
        )

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="1 passed",
                stderr="",
            )

            result = await validator.run_test(test, temp_dir="/tmp/tests")

            assert result.passed is True

    @pytest.mark.asyncio
    async def test_run_failing_test(self, validator):
        """Handle failing test execution."""
        test = GeneratedTest(
            name="test_fails",
            code='''def test_fails():
    assert 1 == 2''',
        )

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout="1 failed",
                stderr="AssertionError",
            )

            result = await validator.run_test(test, temp_dir="/tmp/tests")

            assert result.passed is False
            assert "AssertionError" in result.error_message

    def test_validate_mocking_usage(self, validator):
        """Validate proper mock usage."""
        improper_mock = GeneratedTest(
            name="test_bad_mock",
            code='''def test_bad_mock():
    api.get_data()  # Direct call without mocking
    assert True''',
        )

        result = validator.validate_mocking(
            improper_mock,
            external_calls=["api.get_data"],
        )

        assert result.is_valid is False

    def test_comprehensive_validation(self, validator):
        """Run all validations on a test."""
        test = GeneratedTest(
            name="test_comprehensive",
            code='''def test_comprehensive():
    result = process(10)
    assert result > 0
    assert isinstance(result, int)''',
        )

        result = validator.validate_all(test, language="python")

        assert result.syntax_valid is True
        assert result.has_assertions is True
        assert result.flaky_risk == "low"
```

### Step 2: Run tests to verify they fail

```bash
pytest tests/agents/test_generator/test_validator.py -v
```
Expected: FAIL

### Step 3: Implement the validator

```python
# src/agents/test_generator/validator.py
"""Test validation and execution."""
from __future__ import annotations

import ast
import re
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from .generator import GeneratedTest


@dataclass
class ValidationResult:
    """Result of test validation."""
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class TestExecutionResult:
    """Result of test execution."""
    test_name: str
    passed: bool
    duration_ms: int = 0
    error_message: str = ""
    stdout: str = ""
    stderr: str = ""


@dataclass
class ComprehensiveValidation:
    """Comprehensive validation results."""
    syntax_valid: bool
    has_assertions: bool
    flaky_risk: str  # low, medium, high
    mocking_valid: bool
    all_errors: list[str] = field(default_factory=list)
    all_warnings: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return self.syntax_valid and self.has_assertions


class TestValidator:
    """Validates and executes generated tests."""

    # Patterns that suggest flaky tests
    FLAKY_PATTERNS = [
        r"time\.sleep",
        r"datetime\.now",
        r"random\.",
        r"os\.getenv",
        r"socket\.",
        r"requests\.(get|post|put|delete)",
        r"\.second\s*==",
        r"\.microsecond",
    ]

    # Assertion patterns
    ASSERTION_PATTERNS = [
        r"\bassert\b",
        r"\.assert",
        r"expect\(",
        r"should\.",
        r"assertEqual",
        r"assertTrue",
        r"assertFalse",
        r"assertRaises",
    ]

    def validate_syntax(
        self,
        test: GeneratedTest,
        language: str = "python",
    ) -> ValidationResult:
        """Validate test syntax."""
        if language == "python":
            return self._validate_python_syntax(test)
        elif language in ("javascript", "typescript"):
            return self._validate_js_syntax(test)
        else:
            # Can't validate, assume valid
            return ValidationResult(is_valid=True)

    def _validate_python_syntax(self, test: GeneratedTest) -> ValidationResult:
        """Validate Python syntax using AST."""
        try:
            ast.parse(test.code)
            return ValidationResult(is_valid=True)
        except SyntaxError as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Syntax error at line {e.lineno}: {e.msg}"],
            )

    def _validate_js_syntax(self, test: GeneratedTest) -> ValidationResult:
        """Basic JavaScript syntax validation."""
        # Check for balanced braces/brackets
        code = test.code
        stack = []
        pairs = {')': '(', ']': '[', '}': '{'}

        for char in code:
            if char in '([{':
                stack.append(char)
            elif char in ')]}':
                if not stack or stack[-1] != pairs[char]:
                    return ValidationResult(
                        is_valid=False,
                        errors=["Unbalanced brackets/braces"],
                    )
                stack.pop()

        if stack:
            return ValidationResult(
                is_valid=False,
                errors=["Unclosed brackets/braces"],
            )

        return ValidationResult(is_valid=True)

    def validate_assertions(self, test: GeneratedTest) -> ValidationResult:
        """Check that test has assertions."""
        has_assertion = any(
            re.search(pattern, test.code)
            for pattern in self.ASSERTION_PATTERNS
        )

        if not has_assertion:
            return ValidationResult(
                is_valid=False,
                errors=["Test has no assertions - it will always pass"],
            )

        return ValidationResult(is_valid=True)

    def detect_flaky_patterns(self, test: GeneratedTest) -> ValidationResult:
        """Detect patterns that might make tests flaky."""
        warnings = []

        for pattern in self.FLAKY_PATTERNS:
            if re.search(pattern, test.code):
                warnings.append(
                    f"Potentially flaky pattern detected: {pattern}"
                )

        # Check for global state
        if "global " in test.code:
            warnings.append("Test modifies global state - may cause flakiness")

        return ValidationResult(
            is_valid=True,  # Warnings don't fail validation
            warnings=warnings,
        )

    def validate_mocking(
        self,
        test: GeneratedTest,
        external_calls: list[str],
    ) -> ValidationResult:
        """Validate that external calls are properly mocked."""
        errors = []

        for call in external_calls:
            # Check if the call appears but isn't mocked
            if call in test.code:
                # Look for mock/patch around it
                mock_patterns = [
                    f"patch.*{call.split('.')[0]}",
                    f"mock.*{call.split('.')[0]}",
                    f"Mock.*{call.split('.')[0]}",
                ]
                is_mocked = any(
                    re.search(p, test.code, re.IGNORECASE)
                    for p in mock_patterns
                )
                if not is_mocked:
                    errors.append(
                        f"External call '{call}' is not mocked"
                    )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
        )

    async def run_test(
        self,
        test: GeneratedTest,
        temp_dir: str,
        timeout: int = 30,
    ) -> TestExecutionResult:
        """Execute a test and return results."""
        # Create temp file
        test_file = Path(temp_dir) / f"test_{test.name}.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)

        # Write test with imports
        content = "import pytest\n\n" + test.code
        test_file.write_text(content)

        try:
            result = subprocess.run(
                ["pytest", str(test_file), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=temp_dir,
            )

            return TestExecutionResult(
                test_name=test.name,
                passed=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                error_message=result.stderr if result.returncode != 0 else "",
            )

        except subprocess.TimeoutExpired:
            return TestExecutionResult(
                test_name=test.name,
                passed=False,
                error_message=f"Test timed out after {timeout}s",
            )
        except Exception as e:
            return TestExecutionResult(
                test_name=test.name,
                passed=False,
                error_message=str(e),
            )
        finally:
            # Cleanup
            if test_file.exists():
                test_file.unlink()

    def validate_all(
        self,
        test: GeneratedTest,
        language: str = "python",
        external_calls: list[str] | None = None,
    ) -> ComprehensiveValidation:
        """Run all validations."""
        syntax_result = self.validate_syntax(test, language)
        assertion_result = self.validate_assertions(test)
        flaky_result = self.detect_flaky_patterns(test)

        mocking_valid = True
        if external_calls:
            mock_result = self.validate_mocking(test, external_calls)
            mocking_valid = mock_result.is_valid

        # Determine flaky risk level
        flaky_risk = "low"
        if len(flaky_result.warnings) > 2:
            flaky_risk = "high"
        elif len(flaky_result.warnings) > 0:
            flaky_risk = "medium"

        all_errors = syntax_result.errors + assertion_result.errors
        all_warnings = flaky_result.warnings

        return ComprehensiveValidation(
            syntax_valid=syntax_result.is_valid,
            has_assertions=assertion_result.is_valid,
            flaky_risk=flaky_risk,
            mocking_valid=mocking_valid,
            all_errors=all_errors,
            all_warnings=all_warnings,
        )
```

### Step 4: Run tests to verify they pass

```bash
pytest tests/agents/test_generator/test_validator.py -v
```
Expected: All tests PASS

### Step 5: Commit

```bash
git add src/agents/test_generator/validator.py tests/agents/test_generator/
git commit -m "feat(test-generator): add test validator and runner

- Implement syntax validation for Python and JavaScript
- Add assertion presence checking
- Detect flaky test patterns
- Add test execution with subprocess

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 5: TestGenerator Agent and API Endpoints

**Files:**
- Create: `src/agents/test_generator/agent.py`
- Create: `src/api/routes/tests.py`
- Test: `tests/agents/test_generator/test_agent.py`
- Test: `tests/api/test_tests.py`

### Step 1: Write the failing tests

```python
# tests/agents/test_generator/test_agent.py
"""Tests for TestGenerator agent."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.agents.test_generator.agent import TestGeneratorAgent
from src.core.agents import AgentContext, TaskComplexity


class TestTestGeneratorAgent:
    """Test TestGeneratorAgent."""

    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        mock_llm = AsyncMock()
        return TestGeneratorAgent(llm_client=mock_llm)

    @pytest.mark.asyncio
    async def test_generate_tests_for_file(self, agent):
        """Generate tests for an entire file."""
        code = '''
def add(a: int, b: int) -> int:
    return a + b

def subtract(a: int, b: int) -> int:
    return a - b
'''
        agent.analyzer = MagicMock()
        agent.analyzer.analyze.return_value = MagicMock(
            functions=[
                MagicMock(name="add"),
                MagicMock(name="subtract"),
            ],
            classes=[],
        )

        agent.strategist.plan_tests = AsyncMock(return_value=MagicMock(
            prioritized_targets=[],
        ))

        agent.generator.generate_tests = AsyncMock(return_value=[
            MagicMock(name="test_add", code="def test_add(): assert add(1,2)==3"),
        ])

        context = AgentContext(repo_id="test-repo")
        result = await agent.execute(
            context,
            code=code,
            file_path="math_utils.py",
        )

        assert "tests" in result
        assert len(result["tests"]) > 0

    @pytest.mark.asyncio
    async def test_generate_tests_for_function(self, agent):
        """Generate tests for a specific function."""
        context = AgentContext(repo_id="test-repo")

        agent.generator.generate_tests = AsyncMock(return_value=[
            MagicMock(name="test_process", code="def test_process(): pass"),
        ])

        result = await agent.generate_for_function(
            context,
            function_code="def process(x): return x * 2",
            function_name="process",
        )

        assert len(result["tests"]) > 0

    @pytest.mark.asyncio
    async def test_validate_and_filter(self, agent):
        """Validate generated tests and filter invalid ones."""
        tests = [
            MagicMock(code="def test_valid(): assert True", name="test_valid"),
            MagicMock(code="def test_invalid( assert True", name="test_invalid"),  # Syntax error
        ]

        valid_tests = agent.validator.validate_all = MagicMock(
            side_effect=[
                MagicMock(is_valid=True),
                MagicMock(is_valid=False),
            ]
        )

        filtered = agent._filter_valid_tests(tests)

        # Only valid test should remain
        assert len(filtered) == 1

    def test_agent_properties(self, agent):
        """Verify agent properties."""
        assert agent.name == "test_generator"
        assert agent.complexity == TaskComplexity.MODERATE
```

### Step 2: Run tests to verify they fail

```bash
pytest tests/agents/test_generator/test_agent.py -v
```
Expected: FAIL

### Step 3: Implement the agent and API

```python
# src/agents/test_generator/agent.py
"""TestGenerator agent orchestrating test generation pipeline."""
from __future__ import annotations

from typing import Any, Optional

from src.core.agents import BaseAgent, AgentContext, AgentResult, TaskComplexity

from .analyzer import CodeAnalyzer, ModuleAnalysis
from .coverage import CoverageAnalyzer
from .strategist import TestStrategist, TestStrategy
from .generator import TestGenerator, GeneratedTest, TestFramework
from .validator import TestValidator


class TestGeneratorAgent(BaseAgent):
    """Agent that generates comprehensive test suites."""

    name = "test_generator"
    description = "Generates unit tests, integration tests, and edge cases"
    complexity = TaskComplexity.MODERATE

    def __init__(self, llm_client: Any):
        """Initialize with LLM client."""
        super().__init__(llm_client)
        self.analyzer = CodeAnalyzer()
        self.coverage_analyzer = CoverageAnalyzer()
        self.strategist = TestStrategist(llm_client)
        self.generator = TestGenerator(llm_client)
        self.validator = TestValidator()

    async def execute(
        self,
        context: AgentContext,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate tests for code.

        Args:
            context: Agent execution context
            code: Source code to generate tests for
            file_path: Path to the source file
            framework: Test framework to use (default: pytest)
            coverage_data: Optional existing coverage data

        Returns:
            Dict with generated tests and metadata
        """
        code = kwargs.get("code", "")
        file_path = kwargs.get("file_path", "unknown.py")
        framework_str = kwargs.get("framework", "pytest")
        coverage_data = kwargs.get("coverage_data")

        # Detect language from file extension
        language = self._detect_language(file_path)

        # Map framework string to enum
        try:
            framework = TestFramework(framework_str)
        except ValueError:
            framework = TestFramework.PYTEST

        # Analyze the code
        analysis = self.analyzer.analyze(code, language, file_path)

        # Find coverage gaps if coverage data provided
        gaps = []
        if coverage_data:
            gaps = self.coverage_analyzer.find_gaps(
                analysis.functions,
                coverage_data,
            )

        # Plan test strategy
        strategy = await self.strategist.plan_tests(
            analysis.functions,
            analysis.classes,
        )

        # Generate tests
        all_tests = []

        for func in analysis.functions:
            func_tests = await self.generator.generate_tests(
                func,
                framework=framework,
            )
            all_tests.extend(func_tests)

        for cls in analysis.classes:
            class_tests = await self.generator.generate_class_tests(
                cls,
                framework=framework,
            )
            all_tests.extend(class_tests)

        # Validate and filter
        valid_tests = self._filter_valid_tests(all_tests, language)

        # Format as test file
        test_file_content = self.generator.format_test_file(
            valid_tests,
            source_module=file_path,
            framework=framework,
        )

        return {
            "tests": [
                {
                    "name": t.name,
                    "code": t.code,
                    "description": t.description,
                }
                for t in valid_tests
            ],
            "test_file_content": test_file_content,
            "test_file_path": self._generate_test_path(file_path),
            "functions_analyzed": len(analysis.functions),
            "classes_analyzed": len(analysis.classes),
            "tests_generated": len(valid_tests),
            "coverage_gaps": [
                {"function": g.function_name, "type": g.gap_type.value}
                for g in gaps
            ],
        }

    async def generate_for_function(
        self,
        context: AgentContext,
        function_code: str,
        function_name: str,
        framework: str = "pytest",
    ) -> dict[str, Any]:
        """Generate tests for a single function."""
        # Parse the function
        analysis = self.analyzer.analyze(
            function_code,
            language="python",
            file_path="inline.py",
        )

        if not analysis.functions:
            return {"error": "Could not parse function", "tests": []}

        func = analysis.functions[0]

        # Generate tests
        try:
            fw = TestFramework(framework)
        except ValueError:
            fw = TestFramework.PYTEST

        tests = await self.generator.generate_tests(func, framework=fw)
        valid_tests = self._filter_valid_tests(tests)

        return {
            "tests": [
                {"name": t.name, "code": t.code, "description": t.description}
                for t in valid_tests
            ],
            "function_name": function_name,
        }

    def _filter_valid_tests(
        self,
        tests: list[GeneratedTest],
        language: str = "python",
    ) -> list[GeneratedTest]:
        """Filter out invalid tests."""
        valid = []
        for test in tests:
            validation = self.validator.validate_all(test, language)
            if validation.is_valid:
                valid.append(test)
        return valid

    def _detect_language(self, file_path: str) -> str:
        """Detect language from file extension."""
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".jsx": "javascript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
        }
        for ext, lang in ext_map.items():
            if file_path.endswith(ext):
                return lang
        return "python"

    def _generate_test_path(self, source_path: str) -> str:
        """Generate test file path from source path."""
        # src/services/payment.py -> tests/services/test_payment.py
        parts = source_path.split("/")

        if parts[0] == "src":
            parts[0] = "tests"
        elif not parts[0].startswith("test"):
            parts.insert(0, "tests")

        filename = parts[-1]
        if not filename.startswith("test_"):
            name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "py")
            parts[-1] = f"test_{name}.{ext}"

        return "/".join(parts)
```

```python
# src/api/routes/tests.py
"""Test generation API endpoints."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from src.core.auth import get_current_user
from src.agents.test_generator.agent import TestGeneratorAgent
from src.core.llm import get_claude_client

router = APIRouter(prefix="/tests", tags=["tests"])


class GenerateTestsRequest(BaseModel):
    """Request to generate tests."""
    code: str = Field(..., description="Source code to generate tests for")
    file_path: str = Field(..., description="Path to source file")
    framework: str = Field(default="pytest", description="Test framework")
    focus: Optional[str] = Field(
        default=None,
        description="Focus on specific function/class",
    )


class GenerateTestsResponse(BaseModel):
    """Response with generated tests."""
    tests: list[dict[str, Any]]
    test_file_content: str
    test_file_path: str
    functions_analyzed: int
    tests_generated: int


class GenerateFunctionTestsRequest(BaseModel):
    """Request to generate tests for a single function."""
    function_code: str
    function_name: str
    framework: str = "pytest"


class CoverageReportRequest(BaseModel):
    """Request for coverage analysis."""
    repo_id: str
    coverage_xml: Optional[str] = None


@router.post("/generate", response_model=GenerateTestsResponse)
async def generate_tests(
    request: GenerateTestsRequest,
    user: dict = Depends(get_current_user),
):
    """Generate tests for source code."""
    agent = TestGeneratorAgent(llm_client=get_claude_client())

    from src.core.agents import AgentContext
    context = AgentContext(
        repo_id="inline",
        user_id=user.get("id"),
    )

    result = await agent.execute(
        context,
        code=request.code,
        file_path=request.file_path,
        framework=request.framework,
    )

    return GenerateTestsResponse(
        tests=result["tests"],
        test_file_content=result["test_file_content"],
        test_file_path=result["test_file_path"],
        functions_analyzed=result["functions_analyzed"],
        tests_generated=result["tests_generated"],
    )


@router.post("/generate-function")
async def generate_function_tests(
    request: GenerateFunctionTestsRequest,
    user: dict = Depends(get_current_user),
):
    """Generate tests for a single function."""
    agent = TestGeneratorAgent(llm_client=get_claude_client())

    from src.core.agents import AgentContext
    context = AgentContext(
        repo_id="inline",
        user_id=user.get("id"),
    )

    result = await agent.generate_for_function(
        context,
        function_code=request.function_code,
        function_name=request.function_name,
        framework=request.framework,
    )

    return result


@router.get("/repos/{repo_id}/coverage")
async def get_coverage_report(
    repo_id: str,
    user: dict = Depends(get_current_user),
):
    """Get test coverage report for a repository."""
    # TODO: Fetch from database
    return {
        "repo_id": repo_id,
        "overall_coverage": 0.0,
        "files": [],
        "gaps": [],
    }


@router.post("/repos/{repo_id}/generate", status_code=202)
async def trigger_repo_test_generation(
    repo_id: str,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
):
    """Trigger test generation for entire repository."""
    job_id = str(uuid.uuid4())

    # TODO: Queue background job
    background_tasks.add_task(
        _generate_repo_tests,
        job_id=job_id,
        repo_id=repo_id,
    )

    return {
        "job_id": job_id,
        "status": "queued",
        "message": f"Test generation queued for repository {repo_id}",
    }


async def _generate_repo_tests(job_id: str, repo_id: str):
    """Background task to generate tests for a repository."""
    # TODO: Implement full repo scanning and test generation
    pass
```

### Step 4: Run tests to verify they pass

```bash
pytest tests/agents/test_generator/ tests/api/test_tests.py -v
```
Expected: All tests PASS

### Step 5: Commit

```bash
git add src/agents/test_generator/ src/api/routes/tests.py tests/
git commit -m "feat(test-generator): add TestGenerator agent and API

- Implement TestGeneratorAgent orchestrating full pipeline
- Add API endpoints for test generation
- Support single function and full file test generation
- Add coverage gap detection integration

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Summary

Phase 4 (TestGenerator Agent) implementation plan consists of 5 tasks:

1. **Code Analyzer & Coverage Gap Detection** - AST-based code parsing and coverage analysis
2. **Test Strategy Planner** - Priority-based test planning with LLM assistance
3. **Test Code Generator** - LLM-powered test generation for multiple frameworks
4. **Test Validator & Runner** - Syntax validation, flaky detection, test execution
5. **TestGenerator Agent & API** - Orchestration agent and REST API endpoints

**Estimated Implementation Time:** 2-3 days per task, ~2 weeks total

**Dependencies:**
- Phase 1 (Foundation) must be complete
- Benefits from Phase 3 (CodeReviewer) patterns
