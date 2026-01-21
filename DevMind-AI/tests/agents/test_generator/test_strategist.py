"""Tests for test strategy planner."""
import pytest
from unittest.mock import AsyncMock

from src.agents.test_generator.strategist import (
    TestStrategist,
    TestStrategy,
    TestPriority,
    TestType,
    TestTarget,
)
from src.agents.test_generator.analyzer import FunctionInfo, ClassInfo, ParameterInfo


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
                ParameterInfo(name="user", type_hint="User"),
                ParameterInfo(name="db", type_hint="Database"),
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
                ParameterInfo(name="a", type_hint="float"),
                ParameterInfo(name="b", type_hint="float"),
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
                "fixture_name": "user_service",
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
                TestTarget(function_name="func1", priority=TestPriority.CRITICAL),
                TestTarget(function_name="func2", priority=TestPriority.MEDIUM),
            ],
            total_functions=10,
            current_coverage=0.5,
        )

        estimated = strategist.estimate_coverage_impact(strategy)

        assert estimated > 0.5
        assert estimated <= 1.0
