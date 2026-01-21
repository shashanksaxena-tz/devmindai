"""Tests for TestGenerator agent."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.agents.test_generator.agent import TestGeneratorAgent
from src.agents.base import AgentContext, TaskComplexity


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

        func1 = MagicMock()
        func1.name = "add"
        func2 = MagicMock()
        func2.name = "subtract"

        agent.analyzer.analyze.return_value = MagicMock(
            functions=[func1, func2],
            classes=[],
        )

        agent.strategist.plan_tests = AsyncMock(return_value=MagicMock(
            prioritized_targets=[],
        ))

        test_mock = MagicMock(code="def test_add(): assert add(1,2)==3")
        test_mock.name = "test_add"
        test_mock.imports = []
        test_mock.description = "Test add"
        agent.generator.generate_tests = AsyncMock(return_value=[test_mock])

        context = AgentContext(repository_id="test-repo")
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
        context = AgentContext(repository_id="test-repo")

        test_mock = MagicMock(code="def test_process(): pass")
        test_mock.name = "test_process"
        test_mock.imports = []
        test_mock.description = "Test process"
        agent.generator.generate_tests = AsyncMock(return_value=[test_mock])

        agent.validator.validate_all = MagicMock(
            return_value=MagicMock(is_valid=True)
        )

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
