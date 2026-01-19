# src/agents/code_reviewer/reviewers/base.py
"""Base classes for review agents."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class CommentSeverity(Enum):
    """Severity level for review comments."""
    BLOCKER = "blocker"    # Must fix before merge
    WARNING = "warning"    # Should fix, may approve with justification
    SUGGESTION = "suggestion"  # Consider improving
    NIT = "nit"           # Optional polish
    PRAISE = "praise"     # Positive feedback


@dataclass
class ReviewComment:
    """A single review comment."""
    file_path: str
    line_number: int
    severity: CommentSeverity
    category: str
    title: str
    message: str
    suggestion: Optional[str] = None
    code_before: Optional[str] = None
    code_after: Optional[str] = None
    end_line: Optional[int] = None
    confidence: float = 1.0

    @property
    def is_blocking(self) -> bool:
        """Check if this comment blocks merge."""
        return self.severity == CommentSeverity.BLOCKER


@dataclass
class ReviewResult:
    """Result from a review agent."""
    reviewer_name: str
    comments: list[ReviewComment] = field(default_factory=list)
    summary: Optional[str] = None
    tokens_used: int = 0
    duration_ms: int = 0

    @property
    def blocker_count(self) -> int:
        return sum(1 for c in self.comments if c.is_blocking)

    @property
    def warning_count(self) -> int:
        return sum(1 for c in self.comments
                   if c.severity == CommentSeverity.WARNING)

    @property
    def has_blockers(self) -> bool:
        return self.blocker_count > 0


class BaseReviewer(ABC):
    """Base class for specialized reviewers."""

    name: str = "base"
    category: str = "general"
    description: str = "Base reviewer"

    def __init__(self, llm_client: Any):
        """Initialize with LLM client."""
        self.llm_client = llm_client

    @abstractmethod
    async def review(
        self,
        file_path: str,
        diff: str,
        full_content: str,
        context: Optional[dict[str, Any]] = None,
    ) -> ReviewResult:
        """Perform review and return comments."""
        pass

    def _build_prompt(
        self,
        file_path: str,
        diff: str,
        full_content: str,
        context: Optional[dict[str, Any]] = None,
    ) -> str:
        """Build the review prompt."""
        return f"""Review the following code changes for {self.category} issues.

File: {file_path}

Diff:
```
{diff}
```

Full file content (for context):
```
{full_content[:5000] if full_content else "Not available"}
```

Analyze the changes and identify any {self.category} issues.
For each issue found, provide:
- type: specific issue type
- severity: one of (blocker, warning, suggestion, nit)
- line: line number in the new file
- message: clear description of the issue
- fix: suggested fix

Return a JSON object with an "issues" array.
"""

    def _parse_response(
        self,
        response: dict[str, Any],
        file_path: str,
    ) -> list[ReviewComment]:
        """Parse LLM response into ReviewComment objects."""
        comments = []
        issues = response.get("issues", [])

        for issue in issues:
            severity_str = issue.get("severity", "suggestion").lower()
            try:
                severity = CommentSeverity(severity_str)
            except ValueError:
                severity = CommentSeverity.SUGGESTION

            comment = ReviewComment(
                file_path=file_path,
                line_number=issue.get("line", 1),
                severity=severity,
                category=self.category,
                title=f"{self.category.title()}: {issue.get('type', 'Issue')}",
                message=issue.get("message", "Issue detected"),
                suggestion=issue.get("fix"),
                confidence=issue.get("confidence", 0.8),
            )
            comments.append(comment)

        return comments
