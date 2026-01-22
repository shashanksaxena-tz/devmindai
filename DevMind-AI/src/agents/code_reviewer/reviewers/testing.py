# src/agents/code_reviewer/reviewers/testing.py
"""Testing quality code reviewer."""
from __future__ import annotations

import time
from typing import Any, Optional

from .base import BaseReviewer, ReviewResult


class TestingReviewer(BaseReviewer):
    """Reviews code for test coverage and quality."""

    name = "testing"
    category = "testing"
    description = "Checks test coverage, assertion quality, edge cases"

    async def review(
        self,
        file_path: str,
        diff: str,
        full_content: str,
        context: Optional[dict[str, Any]] = None,
    ) -> ReviewResult:
        """Perform testing review."""
        start_time = time.time()

        prompt = self._build_testing_prompt(file_path, diff, full_content, context)

        schema = {
            "type": "object",
            "properties": {
                "issues": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "severity": {
                                "type": "string",
                                "enum": ["blocker", "warning", "suggestion", "nit"],
                            },
                            "line": {"type": "integer"},
                            "message": {"type": "string"},
                            "fix": {"type": "string"},
                        },
                        "required": ["type", "severity", "line", "message"],
                    },
                }
            },
            "required": ["issues"],
        }

        response = await self.llm_client.generate_structured(
            prompt=prompt,
            schema=schema,
            system_prompt="You are a QA engineer reviewing code for testability.",
        )

        comments = self._parse_response(response, file_path)
        duration_ms = int((time.time() - start_time) * 1000)

        return ReviewResult(
            reviewer_name=self.name,
            comments=comments,
            duration_ms=duration_ms,
        )

    def _build_testing_prompt(
        self,
        file_path: str,
        diff: str,
        full_content: str,
        context: Optional[dict[str, Any]] = None,
    ) -> str:
        """Build testing-focused review prompt."""
        test_info = ""
        if context:
            if context.get("test_files"):
                test_info = f"\nExisting test files: {context['test_files']}"
            if context.get("coverage"):
                test_info += f"\nCurrent coverage: {context['coverage']}%"

        is_test_file = "test_" in file_path or "_test." in file_path

        if is_test_file:
            focus = """
Focus on test quality:
1. Weak Assertions - assert True, assert x (without specific checks)
2. Missing Edge Cases - only happy path tested
3. Flaky Tests - time-dependent, order-dependent
4. Poor Test Names - unclear what's being tested
5. Missing Mocks - real external calls in unit tests
6. Test Duplication - repeated setup, similar tests
7. Assertion Messages - missing helpful failure messages
"""
        else:
            focus = """
Focus on testability:
1. Missing Tests - new functions without tests
2. Untestable Code - hard dependencies, global state
3. Complex Branches - paths that are hard to test
4. Missing Error Cases - error paths without tests
"""

        return f"""You are a QA engineer. Review for test coverage and quality.

File: {file_path}

Code changes (diff):
```
{diff}
```
{test_info}
{focus}

For each issue found, provide:
- type: issue type (e.g., "missing_tests", "weak_assertion")
- severity: "warning" for missing coverage, "suggestion" for quality
- line: line number
- message: clear explanation
- fix: example test or improvement

Return JSON: {{"issues": [...]}}
"""
