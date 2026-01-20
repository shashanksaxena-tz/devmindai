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
