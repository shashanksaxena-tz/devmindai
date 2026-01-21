# src/agents/code_reviewer/synthesizer.py
"""Synthesizes review results from multiple reviewers."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Optional

from .reviewers.base import ReviewResult, ReviewComment, CommentSeverity


@dataclass
class SynthesizedReview:
    """Combined review from all reviewers."""
    comments: list[ReviewComment] = field(default_factory=list)
    summary: str = ""
    verdict: str = "approve"  # approve, comment, request_changes
    blocker_count: int = 0
    warning_count: int = 0
    suggestion_count: int = 0
    praise_count: int = 0
    files_reviewed: int = 0
    reviewers_used: list[str] = field(default_factory=list)

    @property
    def total_comments(self) -> int:
        return len(self.comments)

    @property
    def has_blockers(self) -> bool:
        return self.blocker_count > 0


class ReviewSynthesizer:
    """Synthesizes and formats review results."""

    # Priority order for deduplication (prefer security findings)
    CATEGORY_PRIORITY = [
        "security",
        "correctness",
        "performance",
        "testing",
        "style",
        "documentation",
    ]

    SEVERITY_ORDER = [
        CommentSeverity.BLOCKER,
        CommentSeverity.WARNING,
        CommentSeverity.SUGGESTION,
        CommentSeverity.NIT,
        CommentSeverity.PRAISE,
    ]

    def __init__(self, llm_client: Any):
        """Initialize with LLM client for summary generation."""
        self.llm_client = llm_client

    def deduplicate(self, comments: list[ReviewComment]) -> list[ReviewComment]:
        """Remove duplicate comments, keeping highest priority."""
        # Group by file + line number
        grouped: dict[tuple, list[ReviewComment]] = defaultdict(list)
        for comment in comments:
            key = (comment.file_path, comment.line_number)
            grouped[key].append(comment)

        deduped = []
        for key, group in grouped.items():
            if len(group) == 1:
                deduped.append(group[0])
            else:
                # Check if they're about the same issue (similar messages)
                # Keep the one from highest priority category
                best = self._select_best_comment(group)
                deduped.append(best)

        return deduped

    def _select_best_comment(
        self,
        comments: list[ReviewComment],
    ) -> ReviewComment:
        """Select the best comment from duplicates."""
        # Sort by category priority, then severity
        def sort_key(c: ReviewComment) -> tuple:
            cat_idx = (
                self.CATEGORY_PRIORITY.index(c.category)
                if c.category in self.CATEGORY_PRIORITY
                else len(self.CATEGORY_PRIORITY)
            )
            sev_idx = (
                self.SEVERITY_ORDER.index(c.severity)
                if c.severity in self.SEVERITY_ORDER
                else len(self.SEVERITY_ORDER)
            )
            return (cat_idx, sev_idx)

        return sorted(comments, key=sort_key)[0]

    def prioritize(
        self,
        comments: list[ReviewComment],
    ) -> list[ReviewComment]:
        """Sort comments by severity (most important first)."""
        def severity_key(c: ReviewComment) -> int:
            try:
                return self.SEVERITY_ORDER.index(c.severity)
            except ValueError:
                return len(self.SEVERITY_ORDER)

        return sorted(comments, key=severity_key)

    def group_by_file(
        self,
        comments: list[ReviewComment],
    ) -> dict[str, list[ReviewComment]]:
        """Group comments by file path."""
        grouped: dict[str, list[ReviewComment]] = defaultdict(list)
        for comment in comments:
            grouped[comment.file_path].append(comment)
        return dict(grouped)

    async def synthesize(
        self,
        results: list[ReviewResult],
    ) -> SynthesizedReview:
        """Synthesize all review results into a single review."""
        # Collect all comments
        all_comments = []
        reviewers_used = []

        for result in results:
            all_comments.extend(result.comments)
            reviewers_used.append(result.reviewer_name)

        # Deduplicate and prioritize
        deduped = self.deduplicate(all_comments)
        prioritized = self.prioritize(deduped)

        # Count by severity
        blocker_count = sum(
            1 for c in prioritized if c.severity == CommentSeverity.BLOCKER
        )
        warning_count = sum(
            1 for c in prioritized if c.severity == CommentSeverity.WARNING
        )
        suggestion_count = sum(
            1 for c in prioritized if c.severity == CommentSeverity.SUGGESTION
        )
        praise_count = sum(
            1 for c in prioritized if c.severity == CommentSeverity.PRAISE
        )

        # Determine verdict
        if blocker_count > 0:
            verdict = "request_changes"
        elif warning_count > 0:
            verdict = "comment"
        else:
            verdict = "approve"

        # Generate summary
        summary_result = await self._generate_summary(prioritized)

        return SynthesizedReview(
            comments=prioritized,
            summary=summary_result.get("summary", "Review complete."),
            verdict=summary_result.get("verdict", verdict),
            blocker_count=blocker_count,
            warning_count=warning_count,
            suggestion_count=suggestion_count,
            praise_count=praise_count,
            files_reviewed=len(set(c.file_path for c in prioritized)),
            reviewers_used=reviewers_used,
        )

    async def _generate_summary(
        self,
        comments: list[ReviewComment],
    ) -> dict[str, str]:
        """Generate a human-readable summary of the review."""
        if not comments:
            return {
                "summary": "No issues found. Code looks good!",
                "verdict": "approve",
            }

        # Build summary prompt
        issues_text = "\n".join([
            f"- [{c.severity.value}] {c.category}: {c.title} ({c.file_path}:{c.line_number})"
            for c in comments[:20]  # Limit to first 20
        ])

        prompt = f"""Summarize this code review concisely (2-3 sentences):

Issues found:
{issues_text}

Return JSON with:
- summary: brief summary of findings
- verdict: one of "approve", "comment", "request_changes"
"""

        return await self.llm_client.generate(
            prompt=prompt,
            system="You are a helpful code review assistant.",
            response_format={"type": "json_object"},
        )

    def format_github_comment(
        self,
        review: SynthesizedReview,
    ) -> str:
        """Format the review as a GitHub PR comment."""
        lines = ["## 🤖 DevMind Code Review", ""]

        # Summary table
        lines.append("### Summary")
        lines.append(f"Reviewed {review.files_reviewed} files.")
        lines.append("")
        lines.append("| Category | Count |")
        lines.append("|----------|-------|")
        lines.append(f"| 🔴 Blocker | {review.blocker_count} |")
        lines.append(f"| 🟠 Warning | {review.warning_count} |")
        lines.append(f"| 🟡 Suggestion | {review.suggestion_count} |")
        lines.append(f"| ✅ Looks Good | {review.praise_count} areas |")
        lines.append("")

        # Group comments by severity
        if review.blocker_count > 0:
            lines.append("### 🔴 Blockers")
            lines.append("")
            for c in review.comments:
                if c.severity == CommentSeverity.BLOCKER:
                    lines.extend(self._format_comment(c))
                    lines.append("")

        if review.warning_count > 0:
            lines.append("### 🟠 Warnings")
            lines.append("")
            for c in review.comments:
                if c.severity == CommentSeverity.WARNING:
                    lines.extend(self._format_comment(c))
                    lines.append("")

        if review.suggestion_count > 0:
            lines.append("### 🟡 Suggestions")
            lines.append("")
            for c in review.comments[:10]:  # Limit suggestions shown
                if c.severity == CommentSeverity.SUGGESTION:
                    lines.extend(self._format_comment(c))
                    lines.append("")

        # Praise section
        if review.praise_count > 0:
            lines.append("### ✅ What Looks Great")
            lines.append("")
            for c in review.comments:
                if c.severity == CommentSeverity.PRAISE:
                    lines.append(f"- {c.message}")
            lines.append("")

        return "\n".join(lines)

    def _format_comment(self, comment: ReviewComment) -> list[str]:
        """Format a single comment for GitHub."""
        lines = [
            f"**{comment.file_path}:{comment.line_number}** - {comment.title}",
        ]

        if comment.code_before:
            lines.append("```diff")
            lines.append(f"- {comment.code_before}")
            if comment.code_after:
                lines.append(f"+ {comment.code_after}")
            lines.append("```")

        lines.append(comment.message)

        if comment.suggestion and not comment.code_after:
            lines.append(f"💡 **Suggestion:** {comment.suggestion}")

        return lines
