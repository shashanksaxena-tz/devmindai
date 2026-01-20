# src/agents/code_reviewer/reviewers/documentation.py
"""Documentation code reviewer."""
from __future__ import annotations

import time
from typing import Any, Optional

from .base import BaseReviewer, ReviewResult


class DocumentationReviewer(BaseReviewer):
    """Reviews code for documentation quality."""

    name = "documentation"
    category = "documentation"
    description = "Checks docstrings, comments, type hints"

    async def review(
        self,
        file_path: str,
        diff: str,
        full_content: str,
        context: Optional[dict[str, Any]] = None,
    ) -> ReviewResult:
        """Perform documentation review."""
        start_time = time.time()

        prompt = self._build_documentation_prompt(file_path, diff, full_content)

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
            system_prompt="You are a technical writer reviewing code documentation.",
        )

        comments = self._parse_response(response, file_path)
        duration_ms = int((time.time() - start_time) * 1000)

        return ReviewResult(
            reviewer_name=self.name,
            comments=comments,
            duration_ms=duration_ms,
        )

    def _build_documentation_prompt(
        self,
        file_path: str,
        diff: str,
        full_content: str,
    ) -> str:
        """Build documentation-focused review prompt."""
        return f"""You are a technical writer. Review documentation quality.

File: {file_path}

Code changes (diff):
```
{diff}
```

Check for these documentation issues:
1. Missing Docstrings - public functions/classes without documentation
2. Outdated Comments - comments that don't match the code
3. Missing Type Hints - parameters and returns without types
4. Unclear Descriptions - vague or unhelpful docstrings
5. Missing Examples - complex functions without usage examples
6. TODO/FIXME - unresolved markers that should be addressed
7. Commented Code - dead code that should be removed
8. Missing Parameter Docs - parameters not documented
9. Missing Return Docs - return values not documented
10. Missing Raises Docs - exceptions not documented

For each issue found, provide:
- type: issue type (e.g., "missing_docstring")
- severity: "suggestion" for most, "nit" for minor
- line: line number
- message: clear explanation
- fix: example docstring or type hint

Return JSON: {{"issues": [...]}}

Be helpful, not pedantic. Focus on public APIs.
"""
