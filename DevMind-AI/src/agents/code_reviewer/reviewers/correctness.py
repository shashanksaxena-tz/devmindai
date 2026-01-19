# src/agents/code_reviewer/reviewers/correctness.py
"""Correctness-focused code reviewer."""
from __future__ import annotations

import time
from typing import Any, Optional

from .base import BaseReviewer, ReviewResult


class CorrectnessReviewer(BaseReviewer):
    """Reviews code for logic errors and bugs."""

    name = "correctness"
    category = "correctness"
    description = "Finds bugs, logic errors, null checks, race conditions"

    async def review(
        self,
        file_path: str,
        diff: str,
        full_content: str,
        context: Optional[dict[str, Any]] = None,
    ) -> ReviewResult:
        """Perform correctness review."""
        start_time = time.time()

        prompt = self._build_correctness_prompt(file_path, diff, full_content)

        response = await self.llm_client.generate(
            prompt=prompt,
            system="You are a senior engineer reviewing code for correctness.",
            response_format={"type": "json_object"},
        )

        comments = self._parse_response(response, file_path)
        duration_ms = int((time.time() - start_time) * 1000)

        return ReviewResult(
            reviewer_name=self.name,
            comments=comments,
            duration_ms=duration_ms,
        )

    def _build_correctness_prompt(
        self,
        file_path: str,
        diff: str,
        full_content: str,
    ) -> str:
        """Build correctness-focused review prompt."""
        return f"""You are a senior engineer. Review this code for bugs and logic errors.

File: {file_path}

Code changes (diff):
```
{diff}
```

Full file (for context):
```
{full_content[:4000] if full_content else "Not available"}
```

Check for these correctness issues:
1. Null/None Checks - accessing attributes on potentially None values
2. Off-by-One Errors - incorrect loop bounds, slice indices
3. Type Errors - mismatched types, missing conversions
4. Logic Errors - incorrect conditionals, wrong operators
5. Race Conditions - shared mutable state without synchronization
6. Resource Leaks - files/connections not closed
7. Exception Handling - catching too broadly, swallowing errors
8. Edge Cases - empty lists, zero values, negative numbers
9. State Bugs - incorrect initialization, mutation issues
10. API Misuse - incorrect function arguments, wrong return handling

For each issue found, provide:
- type: issue type (e.g., "null_check", "off_by_one")
- severity: "blocker" if will cause crash/data loss, else "warning"
- line: line number
- message: clear explanation of the bug
- fix: corrected code

Return JSON: {{"issues": [...]}}

Be precise. Only report actual bugs, not style issues.
"""
