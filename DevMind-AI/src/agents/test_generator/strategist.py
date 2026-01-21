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
