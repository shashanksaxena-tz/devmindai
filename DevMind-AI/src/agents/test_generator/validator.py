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
