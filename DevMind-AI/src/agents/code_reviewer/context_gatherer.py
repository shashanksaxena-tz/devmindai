# src/agents/code_reviewer/context_gatherer.py
"""Gather context for code review from GitHub."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class PRContext:
    """Context information about a Pull Request."""
    pr_number: int
    title: str
    body: str
    base_branch: str
    head_sha: str
    linked_issues: list[str] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)
    author: Optional[str] = None
    reviewers: list[str] = field(default_factory=list)


@dataclass
class FileContext:
    """Context for a single file in the PR."""
    path: str
    content_before: Optional[str] = None
    content_after: Optional[str] = None
    related_files: list[str] = field(default_factory=list)
    recent_commits: list[dict[str, Any]] = field(default_factory=list)
    test_files: list[str] = field(default_factory=list)


class ContextGatherer:
    """Gathers context for code review from GitHub API."""

    ISSUE_PATTERN = re.compile(r'#(\d+)')
    FIXES_PATTERN = re.compile(
        r'(?:fix(?:es)?|close(?:s)?|resolve(?:s)?)\s+#(\d+)',
        re.IGNORECASE
    )

    def __init__(self, github_client: Any):
        """Initialize with GitHub client."""
        self.github = github_client

    def gather_pr_context(
        self,
        owner: str,
        repo: str,
        pr_number: int,
    ) -> PRContext:
        """Gather full context for a PR."""
        pr_data = self.github.get_pull(owner, repo, pr_number)

        body = pr_data.get("body") or ""
        linked_issues = self._extract_linked_issues(body)

        return PRContext(
            pr_number=pr_data["number"],
            title=pr_data["title"],
            body=body,
            base_branch=pr_data["base"]["ref"],
            head_sha=pr_data["head"]["sha"],
            linked_issues=linked_issues,
            labels=[l["name"] for l in pr_data.get("labels", [])],
            author=pr_data.get("user", {}).get("login"),
            reviewers=[
                r["login"]
                for r in pr_data.get("requested_reviewers", [])
            ],
        )

    def _extract_linked_issues(self, body: str) -> list[str]:
        """Extract issue references from PR body."""
        issues = set()

        # Find "Fixes #123" style references
        for match in self.FIXES_PATTERN.finditer(body):
            issues.add(f"#{match.group(1)}")

        # Find all #123 style references
        for match in self.ISSUE_PATTERN.finditer(body):
            issues.add(f"#{match.group(1)}")

        return sorted(issues)

    def find_related_files(
        self,
        owner: str,
        repo: str,
        changed_files: list[str],
    ) -> list[str]:
        """Find files related to the changed files."""
        related = set()

        for file_path in changed_files:
            # Search for imports of this file
            module_name = self._file_to_module(file_path)
            if module_name:
                results = self.github.search_code(
                    owner, repo, f"import {module_name}"
                )
                for r in results:
                    if r["path"] not in changed_files:
                        related.add(r["path"])

            # Find corresponding test files
            test_path = self._find_test_file(file_path)
            if test_path:
                related.add(test_path)

        return sorted(related)

    def _file_to_module(self, file_path: str) -> Optional[str]:
        """Convert file path to module name."""
        if not file_path.endswith('.py'):
            return None

        # Remove .py and convert / to .
        module = file_path[:-3].replace('/', '.')
        # Remove src. prefix if present
        if module.startswith('src.'):
            module = module[4:]
        return module

    def _find_test_file(self, file_path: str) -> Optional[str]:
        """Find test file for a given source file."""
        if file_path.startswith('tests/'):
            return None

        if file_path.endswith('.py'):
            # src/services/payment.py -> tests/services/test_payment.py
            parts = file_path.split('/')
            if parts[0] == 'src':
                parts[0] = 'tests'
            filename = parts[-1]
            parts[-1] = f"test_{filename}"
            return '/'.join(parts)

        return None

    def get_file_at_commit(
        self,
        owner: str,
        repo: str,
        file_path: str,
        commit_sha: str,
    ) -> str:
        """Get file content at a specific commit."""
        content_bytes = self.github.get_file_content(
            owner, repo, file_path, commit_sha
        )
        if isinstance(content_bytes, bytes):
            return content_bytes.decode('utf-8')
        return content_bytes

    def get_file_history(
        self,
        owner: str,
        repo: str,
        file_path: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Get recent commit history for a file."""
        commits = self.github.get_commits(
            owner, repo, path=file_path, per_page=limit
        )
        return [
            {
                "sha": c["sha"],
                "message": c.get("commit", {}).get("message", ""),
                "author": c.get("commit", {}).get("author", {}).get("name"),
                "date": c.get("commit", {}).get("author", {}).get("date"),
            }
            for c in commits
        ]

    def gather_file_context(
        self,
        owner: str,
        repo: str,
        file_path: str,
        base_sha: str,
        head_sha: str,
    ) -> FileContext:
        """Gather full context for a changed file."""
        context = FileContext(path=file_path)

        try:
            context.content_before = self.get_file_at_commit(
                owner, repo, file_path, base_sha
            )
        except Exception:
            context.content_before = None

        try:
            context.content_after = self.get_file_at_commit(
                owner, repo, file_path, head_sha
            )
        except Exception:
            context.content_after = None

        context.related_files = self.find_related_files(
            owner, repo, [file_path]
        )
        context.recent_commits = self.get_file_history(
            owner, repo, file_path, limit=5
        )

        # Find test files
        test_file = self._find_test_file(file_path)
        if test_file:
            context.test_files = [test_file]

        return context
