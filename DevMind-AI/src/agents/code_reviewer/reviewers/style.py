# src/agents/code_reviewer/reviewers/style.py
"""Style and maintainability code reviewer."""
from __future__ import annotations

import time
from typing import Any, Optional

from .base import BaseReviewer, ReviewResult


class StyleReviewer(BaseReviewer):
    """Reviews code for style and maintainability."""

    name = "style"
    category = "style"
    description = "Checks naming, duplication, complexity, SOLID principles"

    async def review(
        self,
        file_path: str,
        diff: str,
        full_content: str,
        context: Optional[dict[str, Any]] = None,
    ) -> ReviewResult:
        """Perform style review."""
        start_time = time.time()

        prompt = self._build_style_prompt(file_path, diff, full_content, context)

        response = await self.llm_client.generate(
            prompt=prompt,
            system="You are a code quality expert reviewing for style and maintainability.",
            response_format={"type": "json_object"},
        )

        comments = self._parse_response(response, file_path)
        duration_ms = int((time.time() - start_time) * 1000)

        return ReviewResult(
            reviewer_name=self.name,
            comments=comments,
            duration_ms=duration_ms,
        )

    def _build_style_prompt(
        self,
        file_path: str,
        diff: str,
        full_content: str,
        context: Optional[dict[str, Any]] = None,
    ) -> str:
        """Build style-focused review prompt."""
        codebase_patterns = ""
        if context and context.get("codebase_patterns"):
            codebase_patterns = f"\nCodebase conventions:\n{context['codebase_patterns']}"

        return f"""You are a code quality expert. Review for style and maintainability.

File: {file_path}

Code changes (diff):
```
{diff}
```
{codebase_patterns}

Check for these style issues:
1. Naming Conventions - inconsistent naming, unclear names
2. Code Duplication - repeated logic that should be extracted
3. Function Length - functions doing too many things
4. Complexity - deeply nested code, complex conditionals
5. Magic Numbers - unexplained numeric constants
6. SOLID Violations - single responsibility, open/closed, etc.
7. Dead Code - unreachable or unused code
8. Inconsistent Formatting - mixed styles within the code
9. Import Organization - messy or circular imports
10. Code Smells - feature envy, god objects, etc.

For each issue found, provide:
- type: issue type (e.g., "naming_convention")
- severity: usually "suggestion" or "nit"
- line: line number
- message: clear explanation
- fix: improved code or pattern suggestion

Return JSON: {{"issues": [...]}}

Focus on maintainability. Be constructive, not pedantic.
"""
