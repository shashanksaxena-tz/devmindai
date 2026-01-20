# src/agents/code_reviewer/orchestrator.py
"""Orchestrates parallel code review across multiple specialized reviewers."""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Optional

from .reviewers import (
    SecurityReviewer,
    PerformanceReviewer,
    CorrectnessReviewer,
    StyleReviewer,
    TestingReviewer,
    DocumentationReviewer,
    ReviewResult,
    BaseReviewer,
)

logger = logging.getLogger(__name__)


@dataclass
class FileReviewInput:
    """Input for reviewing a single file."""
    path: str
    diff: str
    content: str
    context: Optional[dict[str, Any]] = None


class ReviewOrchestrator:
    """Orchestrates parallel code review execution."""

    def __init__(
        self,
        claude_client: Any,
        gemini_client: Any,
        enabled_reviewers: Optional[list[str]] = None,
    ):
        """Initialize with LLM clients.

        Args:
            claude_client: Client for complex reasoning (security, correctness, perf)
            gemini_client: Client for fast tasks (style, testing, docs)
            enabled_reviewers: List of reviewer names to enable (all if None)
        """
        self.claude_client = claude_client
        self.gemini_client = gemini_client

        # Initialize all reviewers with appropriate LLM clients
        # Claude for complex reasoning
        self._all_reviewers = {
            "security": SecurityReviewer(claude_client),
            "performance": PerformanceReviewer(claude_client),
            "correctness": CorrectnessReviewer(claude_client),
            # Gemini for faster, simpler tasks
            "style": StyleReviewer(gemini_client),
            "testing": TestingReviewer(gemini_client),
            "documentation": DocumentationReviewer(gemini_client),
        }

        # Filter to enabled reviewers
        if enabled_reviewers:
            self.reviewers = [
                r for name, r in self._all_reviewers.items()
                if name in enabled_reviewers
            ]
        else:
            self.reviewers = list(self._all_reviewers.values())

    async def review_file(
        self,
        file_path: str,
        diff: str,
        full_content: str,
        context: Optional[dict[str, Any]] = None,
    ) -> list[ReviewResult]:
        """Review a single file with all enabled reviewers in parallel.

        Args:
            file_path: Path to the file being reviewed
            diff: Unified diff of changes
            full_content: Full file content for context
            context: Additional context (PR info, related files, etc.)

        Returns:
            List of ReviewResult from each reviewer
        """
        tasks = [
            self._run_reviewer(reviewer, file_path, diff, full_content, context)
            for reviewer in self.reviewers
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and log them
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(
                    f"Reviewer {self.reviewers[i].name} failed: {result}"
                )
            else:
                valid_results.append(result)

        return valid_results

    async def _run_reviewer(
        self,
        reviewer: BaseReviewer,
        file_path: str,
        diff: str,
        full_content: str,
        context: Optional[dict[str, Any]] = None,
    ) -> ReviewResult:
        """Run a single reviewer with error handling."""
        try:
            return await reviewer.review(
                file_path=file_path,
                diff=diff,
                full_content=full_content,
                context=context,
            )
        except Exception as e:
            logger.error(f"Reviewer {reviewer.name} error: {e}")
            raise

    async def review_pr(
        self,
        files: list[dict[str, Any]],
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, list[ReviewResult]]:
        """Review all files in a PR.

        Args:
            files: List of file dicts with 'path', 'diff', 'content' keys
            context: PR context information

        Returns:
            Dict mapping file path to list of review results
        """
        results = {}

        # Process files in parallel batches to avoid overwhelming APIs
        batch_size = 3
        for i in range(0, len(files), batch_size):
            batch = files[i:i + batch_size]
            batch_tasks = [
                self.review_file(
                    file_path=f["path"],
                    diff=f["diff"],
                    full_content=f.get("content", ""),
                    context=context,
                )
                for f in batch
            ]

            batch_results = await asyncio.gather(*batch_tasks)

            for f, r in zip(batch, batch_results):
                results[f["path"]] = r

        return results

    def get_reviewer(self, name: str) -> Optional[BaseReviewer]:
        """Get a specific reviewer by name."""
        return self._all_reviewers.get(name)

    def enable_reviewer(self, name: str) -> None:
        """Enable a reviewer."""
        if name in self._all_reviewers:
            reviewer = self._all_reviewers[name]
            if reviewer not in self.reviewers:
                self.reviewers.append(reviewer)

    def disable_reviewer(self, name: str) -> None:
        """Disable a reviewer."""
        self.reviewers = [r for r in self.reviewers if r.name != name]
