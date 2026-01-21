"""Tests for test code generator."""
import pytest
from unittest.mock import AsyncMock

from src.agents.test_generator.generator import (
    TestGenerator,
    GeneratedTest,
    TestFramework,
)
from src.agents.test_generator.analyzer import FunctionInfo, ParameterInfo
from src.agents.test_generator.strategist import TestType


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
