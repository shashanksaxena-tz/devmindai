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
        imports_to_add: list[str] | None = None,
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

        # Add manual imports (e.g. source module functions)
        if imports_to_add:
            all_imports.update(imports_to_add)
        else:
            # Fallback heuristic (deprecated/unreliable)
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
