# src/agents/code_reviewer/reviewers/performance.py
"""Performance-focused code reviewer."""
from __future__ import annotations

import time
from typing import Any, Optional

from .base import BaseReviewer, ReviewResult


class PerformanceReviewer(BaseReviewer):
    """Reviews code for performance issues."""

    name = "performance"
    category = "performance"
    description = "Detects N+1 queries, inefficient loops, memory issues"

    async def review(
        self,
        file_path: str,
        diff: str,
        full_content: str,
        context: Optional[dict[str, Any]] = None,
    ) -> ReviewResult:
        """Perform performance review."""
        start_time = time.time()

        prompt = self._build_performance_prompt(file_path, diff, full_content)

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
            system_prompt="You are a performance engineer reviewing code for efficiency.",
        )

        comments = self._parse_response(response, file_path)
        duration_ms = int((time.time() - start_time) * 1000)

        return ReviewResult(
            reviewer_name=self.name,
            comments=comments,
            duration_ms=duration_ms,
        )

    def _build_performance_prompt(
        self,
        file_path: str,
        diff: str,
        full_content: str,
    ) -> str:
        """Build performance-focused review prompt."""
        return f"""You are a performance engineer. Review this code for efficiency issues.

File: {file_path}

Code changes (diff):
```
{diff}
```

Full file (for context):
```
{full_content[:4000] if full_content else "Not available"}
```

Check for these performance issues:
1. N+1 Queries - database queries inside loops
2. Missing Indexes - queries on unindexed columns (if SQL visible)
3. Inefficient Algorithms - O(n^2) when O(n) possible
4. Unnecessary Loops - operations that could be vectorized/batched
5. Memory Leaks - unbounded caches, unclosed resources
6. Blocking Operations - sync I/O in async context
7. Large Data Loading - fetching more data than needed
8. Missing Pagination - returning unbounded result sets
9. Repeated Computations - calculations that could be cached
10. String Concatenation - building strings in loops

For each issue found, provide:
- type: issue type (e.g., "n_plus_1")
- severity: "warning" for most, "blocker" if severe
- line: line number
- message: explanation with complexity analysis if applicable
- fix: optimized code suggestion

Return JSON: {{"issues": [...]}}

Focus on impactful issues. Ignore micro-optimizations.
"""
