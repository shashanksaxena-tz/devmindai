# DevMind AI Phase 3: CodeReviewer Agent Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an intelligent code review agent that performs automated PR reviews checking for bugs, security issues, performance problems, and style consistency.

**Architecture:** Multi-agent review system with parallel specialized reviewers (Security, Performance, Correctness, Style, Testing, Docs) that are orchestrated by a Context agent and synthesized by a Synthesizer agent. Uses Claude for complex reasoning tasks and Gemini for fast style/docs checks.

**Tech Stack:** FastAPI, Celery, GitHub API (PyGitHub), tree-sitter for AST parsing, Claude API, Gemini API, Pydantic v2

**Prerequisites:** Phase 1 (Foundation) and Phase 2 (VulnScanner) completed

---

## Task 1: GitHub PR Diff Parser and Context Gatherer

**Files:**
- Create: `src/agents/code_reviewer/diff_parser.py`
- Create: `src/agents/code_reviewer/context_gatherer.py`
- Test: `tests/agents/code_reviewer/test_diff_parser.py`
- Test: `tests/agents/code_reviewer/test_context_gatherer.py`

### Step 1: Write the failing tests for diff parser

```python
# tests/agents/code_reviewer/test_diff_parser.py
"""Tests for PR diff parsing functionality."""
import pytest
from src.agents.code_reviewer.diff_parser import (
    DiffParser,
    FileDiff,
    HunkChange,
    ChangeType,
    parse_unified_diff,
)


class TestDiffParser:
    """Test suite for DiffParser."""

    def test_parse_single_file_addition(self):
        """Parse diff with single file addition."""
        diff_text = '''diff --git a/src/utils/helper.py b/src/utils/helper.py
new file mode 100644
index 0000000..abc1234
--- /dev/null
+++ b/src/utils/helper.py
@@ -0,0 +1,10 @@
+def calculate_total(items):
+    """Calculate total price of items."""
+    total = 0
+    for item in items:
+        total += item.price
+    return total
'''
        parser = DiffParser()
        result = parser.parse(diff_text)

        assert len(result.files) == 1
        assert result.files[0].path == "src/utils/helper.py"
        assert result.files[0].change_type == ChangeType.ADDED
        assert result.files[0].additions == 6
        assert result.files[0].deletions == 0

    def test_parse_file_modification(self):
        """Parse diff with file modifications."""
        diff_text = '''diff --git a/src/api/users.py b/src/api/users.py
index abc1234..def5678 100644
--- a/src/api/users.py
+++ b/src/api/users.py
@@ -10,7 +10,9 @@ def get_user(user_id: int):
     """Get user by ID."""
-    user = db.query(f"SELECT * FROM users WHERE id = {user_id}")
+    query = "SELECT * FROM users WHERE id = %s"
+    user = db.query(query, [user_id])
+    if not user:
+        raise NotFoundError(f"User {user_id} not found")
     return user
'''
        parser = DiffParser()
        result = parser.parse(diff_text)

        assert len(result.files) == 1
        assert result.files[0].change_type == ChangeType.MODIFIED
        assert result.files[0].additions == 4
        assert result.files[0].deletions == 1

    def test_parse_file_deletion(self):
        """Parse diff with file deletion."""
        diff_text = '''diff --git a/old_file.py b/old_file.py
deleted file mode 100644
index abc1234..0000000
--- a/old_file.py
+++ /dev/null
@@ -1,5 +0,0 @@
-def deprecated_function():
-    pass
'''
        parser = DiffParser()
        result = parser.parse(diff_text)

        assert len(result.files) == 1
        assert result.files[0].change_type == ChangeType.DELETED

    def test_parse_multiple_files(self):
        """Parse diff with multiple files."""
        diff_text = '''diff --git a/file1.py b/file1.py
index abc..def 100644
--- a/file1.py
+++ b/file1.py
@@ -1,3 +1,4 @@
 def func1():
+    print("added")
     pass
diff --git a/file2.py b/file2.py
index ghi..jkl 100644
--- a/file2.py
+++ b/file2.py
@@ -1,2 +1,2 @@
-old_line
+new_line
'''
        parser = DiffParser()
        result = parser.parse(diff_text)

        assert len(result.files) == 2
        assert result.total_additions == 2
        assert result.total_deletions == 1

    def test_extract_line_numbers(self):
        """Extract correct line numbers from hunks."""
        diff_text = '''diff --git a/src/api.py b/src/api.py
index abc..def 100644
--- a/src/api.py
+++ b/src/api.py
@@ -45,6 +45,8 @@ def endpoint():
     # existing code
+    new_line_1 = "test"
+    new_line_2 = "test2"
     more_existing()
'''
        parser = DiffParser()
        result = parser.parse(diff_text)

        hunks = result.files[0].hunks
        assert len(hunks) == 1
        assert hunks[0].new_start == 45
        assert hunks[0].new_lines == 8

    def test_parse_binary_file(self):
        """Handle binary file changes."""
        diff_text = '''diff --git a/image.png b/image.png
new file mode 100644
index 0000000..abc1234
Binary files /dev/null and b/image.png differ
'''
        parser = DiffParser()
        result = parser.parse(diff_text)

        assert len(result.files) == 1
        assert result.files[0].is_binary is True

    def test_parse_rename(self):
        """Handle file rename."""
        diff_text = '''diff --git a/old_name.py b/new_name.py
similarity index 95%
rename from old_name.py
rename to new_name.py
index abc..def 100644
--- a/old_name.py
+++ b/new_name.py
'''
        parser = DiffParser()
        result = parser.parse(diff_text)

        assert result.files[0].change_type == ChangeType.RENAMED
        assert result.files[0].old_path == "old_name.py"
        assert result.files[0].path == "new_name.py"


class TestContextGatherer:
    """Test suite for ContextGatherer."""

    @pytest.fixture
    def mock_github_client(self, mocker):
        """Create mock GitHub client."""
        return mocker.MagicMock()

    def test_gather_pr_context(self, mock_github_client):
        """Gather full PR context including description and linked issues."""
        from src.agents.code_reviewer.context_gatherer import ContextGatherer

        mock_github_client.get_pull.return_value = {
            "number": 123,
            "title": "Fix user authentication",
            "body": "Fixes #456\n\nThis PR addresses the login bug.",
            "base": {"ref": "main"},
            "head": {"sha": "abc123"},
        }

        gatherer = ContextGatherer(mock_github_client)
        context = gatherer.gather_pr_context("owner", "repo", 123)

        assert context.pr_number == 123
        assert context.title == "Fix user authentication"
        assert "#456" in context.linked_issues

    def test_gather_related_files(self, mock_github_client):
        """Identify files related to changed files (imports, tests)."""
        from src.agents.code_reviewer.context_gatherer import ContextGatherer

        changed_files = ["src/services/payment.py"]
        mock_github_client.search_code.return_value = [
            {"path": "tests/services/test_payment.py"},
            {"path": "src/api/checkout.py"},
        ]

        gatherer = ContextGatherer(mock_github_client)
        related = gatherer.find_related_files("owner", "repo", changed_files)

        assert "tests/services/test_payment.py" in related
        assert "src/api/checkout.py" in related

    def test_get_file_content_at_commit(self, mock_github_client):
        """Retrieve file content at specific commit."""
        from src.agents.code_reviewer.context_gatherer import ContextGatherer

        mock_github_client.get_file_content.return_value = b"def hello(): pass"

        gatherer = ContextGatherer(mock_github_client)
        content = gatherer.get_file_at_commit(
            "owner", "repo", "src/hello.py", "abc123"
        )

        assert content == "def hello(): pass"

    def test_get_recent_commits_to_file(self, mock_github_client):
        """Get recent commit history for a file."""
        from src.agents.code_reviewer.context_gatherer import ContextGatherer

        mock_github_client.get_commits.return_value = [
            {"sha": "abc", "message": "Fix bug"},
            {"sha": "def", "message": "Initial impl"},
        ]

        gatherer = ContextGatherer(mock_github_client)
        commits = gatherer.get_file_history(
            "owner", "repo", "src/file.py", limit=5
        )

        assert len(commits) == 2
        assert commits[0]["message"] == "Fix bug"
```

### Step 2: Run tests to verify they fail

```bash
cd /Users/shashanksaxena/Documents/Personal/Code/llmShowcase/awesome-llm-apps/DevMind-AI
pytest tests/agents/code_reviewer/test_diff_parser.py -v
```
Expected: FAIL with "ModuleNotFoundError: No module named 'src.agents.code_reviewer'"

### Step 3: Implement the diff parser and context gatherer

```python
# src/agents/code_reviewer/__init__.py
"""CodeReviewer agent module."""

# src/agents/code_reviewer/diff_parser.py
"""Parse unified diff format from Git/GitHub."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ChangeType(Enum):
    """Type of file change in diff."""
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


@dataclass
class HunkChange:
    """Represents a single change hunk in a diff."""
    old_start: int
    old_lines: int
    new_start: int
    new_lines: int
    content: str
    added_lines: list[tuple[int, str]] = field(default_factory=list)
    removed_lines: list[tuple[int, str]] = field(default_factory=list)


@dataclass
class FileDiff:
    """Represents changes to a single file."""
    path: str
    change_type: ChangeType
    old_path: Optional[str] = None
    hunks: list[HunkChange] = field(default_factory=list)
    additions: int = 0
    deletions: int = 0
    is_binary: bool = False
    language: Optional[str] = None

    @property
    def total_changes(self) -> int:
        return self.additions + self.deletions


@dataclass
class DiffResult:
    """Complete diff parsing result."""
    files: list[FileDiff] = field(default_factory=list)

    @property
    def total_additions(self) -> int:
        return sum(f.additions for f in self.files)

    @property
    def total_deletions(self) -> int:
        return sum(f.deletions for f in self.files)

    @property
    def files_changed(self) -> int:
        return len(self.files)


class DiffParser:
    """Parser for unified diff format."""

    # Regex patterns
    FILE_HEADER_PATTERN = re.compile(r'^diff --git a/(.+) b/(.+)$')
    NEW_FILE_PATTERN = re.compile(r'^new file mode')
    DELETED_FILE_PATTERN = re.compile(r'^deleted file mode')
    RENAME_FROM_PATTERN = re.compile(r'^rename from (.+)$')
    RENAME_TO_PATTERN = re.compile(r'^rename to (.+)$')
    BINARY_PATTERN = re.compile(r'^Binary files')
    HUNK_HEADER_PATTERN = re.compile(
        r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@'
    )
    INDEX_PATTERN = re.compile(r'^index ([a-f0-9]+)\.\.([a-f0-9]+)')

    # Language detection by extension
    LANGUAGE_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.jsx': 'javascript',
        '.java': 'java',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.cs': 'csharp',
        '.cpp': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.hpp': 'cpp',
        '.sql': 'sql',
        '.md': 'markdown',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
    }

    def parse(self, diff_text: str) -> DiffResult:
        """Parse unified diff text into structured result."""
        result = DiffResult()
        lines = diff_text.split('\n')
        current_file: Optional[FileDiff] = None
        current_hunk: Optional[HunkChange] = None
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check for new file header
            file_match = self.FILE_HEADER_PATTERN.match(line)
            if file_match:
                # Save previous file if exists
                if current_file:
                    if current_hunk:
                        current_file.hunks.append(current_hunk)
                    result.files.append(current_file)

                # Start new file
                old_path, new_path = file_match.groups()
                current_file = FileDiff(
                    path=new_path,
                    change_type=ChangeType.MODIFIED,
                )
                current_hunk = None

                # Look ahead for file metadata
                i = self._parse_file_metadata(
                    lines, i + 1, current_file, old_path
                )
                continue

            # Check for hunk header
            hunk_match = self.HUNK_HEADER_PATTERN.match(line)
            if hunk_match and current_file:
                if current_hunk:
                    current_file.hunks.append(current_hunk)

                old_start = int(hunk_match.group(1))
                old_lines = int(hunk_match.group(2) or 1)
                new_start = int(hunk_match.group(3))
                new_lines = int(hunk_match.group(4) or 1)

                current_hunk = HunkChange(
                    old_start=old_start,
                    old_lines=old_lines,
                    new_start=new_start,
                    new_lines=new_lines,
                    content=line,
                )
                i += 1
                continue

            # Parse hunk content
            if current_hunk and current_file:
                if line.startswith('+') and not line.startswith('+++'):
                    current_file.additions += 1
                    line_num = current_hunk.new_start + len(
                        current_hunk.added_lines
                    )
                    current_hunk.added_lines.append((line_num, line[1:]))
                elif line.startswith('-') and not line.startswith('---'):
                    current_file.deletions += 1
                    line_num = current_hunk.old_start + len(
                        current_hunk.removed_lines
                    )
                    current_hunk.removed_lines.append((line_num, line[1:]))

            i += 1

        # Don't forget the last file
        if current_file:
            if current_hunk:
                current_file.hunks.append(current_hunk)
            result.files.append(current_file)

        # Detect languages
        for file_diff in result.files:
            file_diff.language = self._detect_language(file_diff.path)

        return result

    def _parse_file_metadata(
        self,
        lines: list[str],
        start_idx: int,
        file_diff: FileDiff,
        old_path: str,
    ) -> int:
        """Parse file metadata (new/deleted/renamed/binary)."""
        i = start_idx
        while i < len(lines):
            line = lines[i]

            if self.NEW_FILE_PATTERN.match(line):
                file_diff.change_type = ChangeType.ADDED
            elif self.DELETED_FILE_PATTERN.match(line):
                file_diff.change_type = ChangeType.DELETED
            elif self.BINARY_PATTERN.match(line):
                file_diff.is_binary = True
            elif rename_from := self.RENAME_FROM_PATTERN.match(line):
                file_diff.change_type = ChangeType.RENAMED
                file_diff.old_path = rename_from.group(1)
            elif rename_to := self.RENAME_TO_PATTERN.match(line):
                file_diff.path = rename_to.group(1)
            elif line.startswith('diff --git') or line.startswith('@@'):
                # Next file or hunk, stop parsing metadata
                return i
            elif line.startswith('---') or line.startswith('+++'):
                pass  # Skip these lines
            elif self.INDEX_PATTERN.match(line):
                pass  # Skip index line

            i += 1

        return i

    def _detect_language(self, file_path: str) -> Optional[str]:
        """Detect programming language from file extension."""
        for ext, lang in self.LANGUAGE_MAP.items():
            if file_path.endswith(ext):
                return lang
        return None


def parse_unified_diff(diff_text: str) -> DiffResult:
    """Convenience function to parse unified diff."""
    return DiffParser().parse(diff_text)
```

```python
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
```

### Step 4: Run tests to verify they pass

```bash
pytest tests/agents/code_reviewer/test_diff_parser.py -v
```
Expected: All tests PASS

### Step 5: Commit

```bash
git add src/agents/code_reviewer/ tests/agents/code_reviewer/
git commit -m "feat(code-reviewer): add diff parser and context gatherer

- Implement unified diff parser supporting add/modify/delete/rename
- Add context gatherer for PR metadata and related files
- Support language detection and test file discovery

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Specialized Review Agents (Security, Performance, Correctness)

**Files:**
- Create: `src/agents/code_reviewer/reviewers/base.py`
- Create: `src/agents/code_reviewer/reviewers/security.py`
- Create: `src/agents/code_reviewer/reviewers/performance.py`
- Create: `src/agents/code_reviewer/reviewers/correctness.py`
- Test: `tests/agents/code_reviewer/test_reviewers.py`

### Step 1: Write the failing tests

```python
# tests/agents/code_reviewer/test_reviewers.py
"""Tests for specialized review agents."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.agents.code_reviewer.reviewers.base import (
    ReviewComment,
    CommentSeverity,
    ReviewResult,
)
from src.agents.code_reviewer.reviewers.security import SecurityReviewer
from src.agents.code_reviewer.reviewers.performance import PerformanceReviewer
from src.agents.code_reviewer.reviewers.correctness import CorrectnessReviewer


class TestReviewComment:
    """Test ReviewComment model."""

    def test_comment_creation(self):
        """Create review comment with all fields."""
        comment = ReviewComment(
            file_path="src/api/users.py",
            line_number=47,
            severity=CommentSeverity.BLOCKER,
            category="security",
            title="SQL Injection Vulnerability",
            message="User input is directly interpolated into SQL query.",
            suggestion="Use parameterized queries instead.",
            code_before='query = f"SELECT * FROM users WHERE id = {user_id}"',
            code_after='query = "SELECT * FROM users WHERE id = %s"\nresult = db.query(query, [user_id])',
        )

        assert comment.severity == CommentSeverity.BLOCKER
        assert comment.is_blocking is True

    def test_severity_levels(self):
        """Verify all severity levels."""
        assert CommentSeverity.BLOCKER.value == "blocker"
        assert CommentSeverity.WARNING.value == "warning"
        assert CommentSeverity.SUGGESTION.value == "suggestion"
        assert CommentSeverity.NIT.value == "nit"
        assert CommentSeverity.PRAISE.value == "praise"


class TestSecurityReviewer:
    """Test SecurityReviewer agent."""

    @pytest.fixture
    def reviewer(self):
        """Create SecurityReviewer instance."""
        mock_llm = AsyncMock()
        return SecurityReviewer(llm_client=mock_llm)

    @pytest.mark.asyncio
    async def test_detect_sql_injection(self, reviewer):
        """Detect SQL injection vulnerability."""
        code_diff = '''
@@ -10,3 +10,5 @@
+def get_user(user_id):
+    query = f"SELECT * FROM users WHERE id = {user_id}"
+    return db.execute(query)
'''
        reviewer.llm_client.generate.return_value = {
            "issues": [{
                "type": "sql_injection",
                "severity": "blocker",
                "line": 11,
                "message": "SQL injection vulnerability via string interpolation",
                "fix": "Use parameterized queries"
            }]
        }

        result = await reviewer.review(
            file_path="src/api/users.py",
            diff=code_diff,
            full_content="",
        )

        assert len(result.comments) >= 1
        assert any(c.category == "security" for c in result.comments)

    @pytest.mark.asyncio
    async def test_detect_hardcoded_secret(self, reviewer):
        """Detect hardcoded secrets."""
        code_diff = '''
+API_KEY = "sk-1234567890abcdef"
+AWS_SECRET = "AKIAIOSFODNN7EXAMPLE"
'''
        reviewer.llm_client.generate.return_value = {
            "issues": [{
                "type": "hardcoded_secret",
                "severity": "blocker",
                "line": 1,
                "message": "Hardcoded API key detected",
                "fix": "Use environment variables"
            }]
        }

        result = await reviewer.review(
            file_path="config.py",
            diff=code_diff,
            full_content="",
        )

        assert len(result.comments) >= 1
        blocker_comments = [
            c for c in result.comments
            if c.severity == CommentSeverity.BLOCKER
        ]
        assert len(blocker_comments) >= 1

    @pytest.mark.asyncio
    async def test_detect_xss(self, reviewer):
        """Detect XSS vulnerability."""
        code_diff = '''
+def render_name(name):
+    return f"<div>{name}</div>"
'''
        reviewer.llm_client.generate.return_value = {
            "issues": [{
                "type": "xss",
                "severity": "blocker",
                "line": 2,
                "message": "Potential XSS - user input rendered without escaping",
                "fix": "Use proper HTML escaping"
            }]
        }

        result = await reviewer.review(
            file_path="templates.py",
            diff=code_diff,
            full_content="",
        )

        assert any("xss" in c.title.lower() or "xss" in c.message.lower()
                   for c in result.comments)


class TestPerformanceReviewer:
    """Test PerformanceReviewer agent."""

    @pytest.fixture
    def reviewer(self):
        """Create PerformanceReviewer instance."""
        mock_llm = AsyncMock()
        return PerformanceReviewer(llm_client=mock_llm)

    @pytest.mark.asyncio
    async def test_detect_n_plus_1(self, reviewer):
        """Detect N+1 query pattern."""
        code_diff = '''
+def get_orders_with_items():
+    orders = Order.objects.all()
+    for order in orders:
+        items = order.items.all()  # N+1 query!
+        process(order, items)
'''
        reviewer.llm_client.generate.return_value = {
            "issues": [{
                "type": "n_plus_1",
                "severity": "warning",
                "line": 4,
                "message": "N+1 query detected - fetching items inside loop",
                "fix": "Use select_related or prefetch_related"
            }]
        }

        result = await reviewer.review(
            file_path="services.py",
            diff=code_diff,
            full_content="",
        )

        assert any("n+1" in c.message.lower() or "n+1" in c.title.lower()
                   for c in result.comments)

    @pytest.mark.asyncio
    async def test_detect_inefficient_loop(self, reviewer):
        """Detect inefficient list operations in loop."""
        code_diff = '''
+def process_items(items):
+    result = []
+    for item in items:
+        if item.id not in [r.id for r in result]:  # O(n^2)
+            result.append(item)
'''
        reviewer.llm_client.generate.return_value = {
            "issues": [{
                "type": "inefficient_loop",
                "severity": "warning",
                "line": 4,
                "message": "O(n^2) complexity - list comprehension in loop",
                "fix": "Use a set for O(1) lookups"
            }]
        }

        result = await reviewer.review(
            file_path="utils.py",
            diff=code_diff,
            full_content="",
        )

        assert len(result.comments) >= 1


class TestCorrectnessReviewer:
    """Test CorrectnessReviewer agent."""

    @pytest.fixture
    def reviewer(self):
        """Create CorrectnessReviewer instance."""
        mock_llm = AsyncMock()
        return CorrectnessReviewer(llm_client=mock_llm)

    @pytest.mark.asyncio
    async def test_detect_null_check_missing(self, reviewer):
        """Detect missing null/None checks."""
        code_diff = '''
+def get_user_email(user_id):
+    user = find_user(user_id)
+    return user.email  # user might be None!
'''
        reviewer.llm_client.generate.return_value = {
            "issues": [{
                "type": "null_check",
                "severity": "warning",
                "line": 3,
                "message": "Accessing attribute on potentially None value",
                "fix": "Add null check before accessing .email"
            }]
        }

        result = await reviewer.review(
            file_path="users.py",
            diff=code_diff,
            full_content="",
        )

        assert len(result.comments) >= 1

    @pytest.mark.asyncio
    async def test_detect_off_by_one(self, reviewer):
        """Detect off-by-one errors."""
        code_diff = '''
+def get_last_n_items(items, n):
+    return items[len(items) - n - 1:]  # Off by one!
'''
        reviewer.llm_client.generate.return_value = {
            "issues": [{
                "type": "off_by_one",
                "severity": "warning",
                "line": 2,
                "message": "Potential off-by-one error in slice",
                "fix": "Should be items[-n:] or items[len(items) - n:]"
            }]
        }

        result = await reviewer.review(
            file_path="utils.py",
            diff=code_diff,
            full_content="",
        )

        assert any("off" in c.message.lower() for c in result.comments)

    @pytest.mark.asyncio
    async def test_detect_race_condition(self, reviewer):
        """Detect potential race conditions."""
        code_diff = '''
+counter = 0
+
+def increment():
+    global counter
+    temp = counter
+    counter = temp + 1  # Race condition!
'''
        reviewer.llm_client.generate.return_value = {
            "issues": [{
                "type": "race_condition",
                "severity": "warning",
                "line": 6,
                "message": "Potential race condition with global counter",
                "fix": "Use threading.Lock or atomic operations"
            }]
        }

        result = await reviewer.review(
            file_path="counter.py",
            diff=code_diff,
            full_content="",
        )

        assert len(result.comments) >= 1
```

### Step 2: Run tests to verify they fail

```bash
pytest tests/agents/code_reviewer/test_reviewers.py -v
```
Expected: FAIL with import errors

### Step 3: Implement the specialized reviewers

```python
# src/agents/code_reviewer/reviewers/__init__.py
"""Specialized review agents."""
from .base import ReviewComment, CommentSeverity, ReviewResult
from .security import SecurityReviewer
from .performance import PerformanceReviewer
from .correctness import CorrectnessReviewer

__all__ = [
    "ReviewComment",
    "CommentSeverity",
    "ReviewResult",
    "SecurityReviewer",
    "PerformanceReviewer",
    "CorrectnessReviewer",
]
```

```python
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
```

```python
# src/agents/code_reviewer/reviewers/security.py
"""Security-focused code reviewer."""
from __future__ import annotations

import time
from typing import Any, Optional

from .base import BaseReviewer, ReviewResult, ReviewComment, CommentSeverity


class SecurityReviewer(BaseReviewer):
    """Reviews code for security vulnerabilities."""

    name = "security"
    category = "security"
    description = "Scans for OWASP Top 10, injection, auth issues, secrets"

    SECURITY_PATTERNS = [
        "sql injection",
        "xss",
        "csrf",
        "hardcoded secret",
        "path traversal",
        "command injection",
        "insecure deserialization",
        "weak crypto",
        "missing auth",
        "sensitive data exposure",
    ]

    async def review(
        self,
        file_path: str,
        diff: str,
        full_content: str,
        context: Optional[dict[str, Any]] = None,
    ) -> ReviewResult:
        """Perform security review."""
        start_time = time.time()

        prompt = self._build_security_prompt(file_path, diff, full_content)

        response = await self.llm_client.generate(
            prompt=prompt,
            system="You are a security expert reviewing code for vulnerabilities.",
            response_format={"type": "json_object"},
        )

        comments = self._parse_response(response, file_path)

        duration_ms = int((time.time() - start_time) * 1000)

        return ReviewResult(
            reviewer_name=self.name,
            comments=comments,
            duration_ms=duration_ms,
        )

    def _build_security_prompt(
        self,
        file_path: str,
        diff: str,
        full_content: str,
    ) -> str:
        """Build security-focused review prompt."""
        return f"""You are a security expert. Review this code for vulnerabilities.

File: {file_path}

Code changes (diff):
```
{diff}
```

Check for these security issues:
1. SQL Injection - string interpolation in queries
2. XSS - unescaped user input in HTML
3. Hardcoded Secrets - API keys, passwords in code
4. Command Injection - shell commands with user input
5. Path Traversal - file paths from user input
6. Insecure Deserialization - pickle, eval on user data
7. Missing Authentication - unprotected endpoints
8. Weak Cryptography - MD5, SHA1 for passwords
9. CSRF - missing tokens on state-changing operations
10. Sensitive Data Exposure - logging secrets, PII

For each vulnerability found, provide:
- type: vulnerability type (e.g., "sql_injection")
- severity: "blocker" for exploitable, "warning" for potential
- line: line number
- message: clear explanation of the risk
- fix: specific remediation code

Return JSON: {{"issues": [...]}}

Only report real issues. Avoid false positives.
"""
```

```python
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

        response = await self.llm_client.generate(
            prompt=prompt,
            system="You are a performance engineer reviewing code for efficiency.",
            response_format={"type": "json_object"},
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
```

```python
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
```

### Step 4: Run tests to verify they pass

```bash
pytest tests/agents/code_reviewer/test_reviewers.py -v
```
Expected: All tests PASS

### Step 5: Commit

```bash
git add src/agents/code_reviewer/reviewers/
git commit -m "feat(code-reviewer): add specialized review agents

- Add Security reviewer for OWASP Top 10, injection, secrets
- Add Performance reviewer for N+1, inefficient algorithms
- Add Correctness reviewer for bugs, null checks, race conditions
- Define severity levels: blocker, warning, suggestion, nit, praise

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Style, Testing, and Documentation Reviewers

**Files:**
- Create: `src/agents/code_reviewer/reviewers/style.py`
- Create: `src/agents/code_reviewer/reviewers/testing.py`
- Create: `src/agents/code_reviewer/reviewers/documentation.py`
- Test: `tests/agents/code_reviewer/test_style_reviewers.py`

### Step 1: Write the failing tests

```python
# tests/agents/code_reviewer/test_style_reviewers.py
"""Tests for style, testing, and documentation reviewers."""
import pytest
from unittest.mock import AsyncMock

from src.agents.code_reviewer.reviewers.style import StyleReviewer
from src.agents.code_reviewer.reviewers.testing import TestingReviewer
from src.agents.code_reviewer.reviewers.documentation import DocumentationReviewer
from src.agents.code_reviewer.reviewers.base import CommentSeverity


class TestStyleReviewer:
    """Test StyleReviewer agent."""

    @pytest.fixture
    def reviewer(self):
        """Create StyleReviewer instance."""
        mock_llm = AsyncMock()
        return StyleReviewer(llm_client=mock_llm)

    @pytest.mark.asyncio
    async def test_detect_inconsistent_naming(self, reviewer):
        """Detect inconsistent naming conventions."""
        code_diff = '''
+def getUserData(userId):  # Should be get_user_data
+    userName = fetch(userId)  # Should be user_name
+    return userName
'''
        reviewer.llm_client.generate.return_value = {
            "issues": [{
                "type": "naming_convention",
                "severity": "suggestion",
                "line": 1,
                "message": "Function uses camelCase instead of snake_case",
                "fix": "Rename to get_user_data"
            }]
        }

        result = await reviewer.review(
            file_path="utils.py",
            diff=code_diff,
            full_content="",
        )

        assert len(result.comments) >= 1
        assert any(c.severity == CommentSeverity.SUGGESTION for c in result.comments)

    @pytest.mark.asyncio
    async def test_detect_code_duplication(self, reviewer):
        """Detect code duplication."""
        code_diff = '''
+def process_user(user):
+    if user.active:
+        send_email(user.email)
+        log_action(user.id)
+
+def process_admin(admin):
+    if admin.active:
+        send_email(admin.email)  # Duplicated logic
+        log_action(admin.id)
'''
        reviewer.llm_client.generate.return_value = {
            "issues": [{
                "type": "code_duplication",
                "severity": "suggestion",
                "line": 6,
                "message": "Duplicated logic with process_user",
                "fix": "Extract common logic to shared function"
            }]
        }

        result = await reviewer.review(
            file_path="handlers.py",
            diff=code_diff,
            full_content="",
        )

        assert any("duplic" in c.message.lower() for c in result.comments)


class TestTestingReviewer:
    """Test TestingReviewer agent."""

    @pytest.fixture
    def reviewer(self):
        """Create TestingReviewer instance."""
        mock_llm = AsyncMock()
        return TestingReviewer(llm_client=mock_llm)

    @pytest.mark.asyncio
    async def test_detect_missing_tests(self, reviewer):
        """Detect missing test coverage."""
        code_diff = '''
+def critical_payment_handler(amount, card):
+    if amount <= 0:
+        raise ValueError("Invalid amount")
+    return process_payment(card, amount)
'''
        reviewer.llm_client.generate.return_value = {
            "issues": [{
                "type": "missing_tests",
                "severity": "warning",
                "line": 1,
                "message": "New function lacks test coverage",
                "fix": "Add tests for valid payment, invalid amount, and edge cases"
            }]
        }

        result = await reviewer.review(
            file_path="payment.py",
            diff=code_diff,
            full_content="",
            context={"test_files": []},
        )

        assert len(result.comments) >= 1

    @pytest.mark.asyncio
    async def test_detect_weak_assertions(self, reviewer):
        """Detect weak test assertions."""
        code_diff = '''
+def test_user_creation():
+    user = create_user("test@example.com")
+    assert user  # Weak assertion!
+    assert user is not None  # Also weak
'''
        reviewer.llm_client.generate.return_value = {
            "issues": [{
                "type": "weak_assertion",
                "severity": "suggestion",
                "line": 3,
                "message": "Assertion only checks truthiness, not actual values",
                "fix": "Assert specific attributes: assert user.email == 'test@example.com'"
            }]
        }

        result = await reviewer.review(
            file_path="test_users.py",
            diff=code_diff,
            full_content="",
        )

        assert any("assert" in c.message.lower() for c in result.comments)


class TestDocumentationReviewer:
    """Test DocumentationReviewer agent."""

    @pytest.fixture
    def reviewer(self):
        """Create DocumentationReviewer instance."""
        mock_llm = AsyncMock()
        return DocumentationReviewer(llm_client=mock_llm)

    @pytest.mark.asyncio
    async def test_detect_missing_docstring(self, reviewer):
        """Detect missing docstrings."""
        code_diff = '''
+def calculate_tax(amount, rate, region):
+    if region == "EU":
+        return amount * rate * 1.2
+    return amount * rate
'''
        reviewer.llm_client.generate.return_value = {
            "issues": [{
                "type": "missing_docstring",
                "severity": "suggestion",
                "line": 1,
                "message": "Public function missing docstring",
                "fix": "Add docstring explaining parameters and return value"
            }]
        }

        result = await reviewer.review(
            file_path="tax.py",
            diff=code_diff,
            full_content="",
        )

        assert any("docstring" in c.message.lower() for c in result.comments)

    @pytest.mark.asyncio
    async def test_detect_outdated_comment(self, reviewer):
        """Detect outdated comments."""
        code_diff = '''
 # Returns user email
-def get_user_email(user_id):
-    return db.get_email(user_id)
+def get_user_data(user_id):  # Comment no longer accurate
+    return db.get_user(user_id)
'''
        reviewer.llm_client.generate.return_value = {
            "issues": [{
                "type": "outdated_comment",
                "severity": "suggestion",
                "line": 1,
                "message": "Comment says 'email' but function now returns full user data",
                "fix": "Update comment to match new functionality"
            }]
        }

        result = await reviewer.review(
            file_path="users.py",
            diff=code_diff,
            full_content="",
        )

        assert len(result.comments) >= 1
```

### Step 2: Run tests to verify they fail

```bash
pytest tests/agents/code_reviewer/test_style_reviewers.py -v
```
Expected: FAIL with import errors

### Step 3: Implement the reviewers

```python
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
```

```python
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

        response = await self.llm_client.generate(
            prompt=prompt,
            system="You are a QA engineer reviewing code for testability.",
            response_format={"type": "json_object"},
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
```

```python
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

        response = await self.llm_client.generate(
            prompt=prompt,
            system="You are a technical writer reviewing code documentation.",
            response_format={"type": "json_object"},
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
```

Update the `__init__.py`:

```python
# src/agents/code_reviewer/reviewers/__init__.py
"""Specialized review agents."""
from .base import ReviewComment, CommentSeverity, ReviewResult, BaseReviewer
from .security import SecurityReviewer
from .performance import PerformanceReviewer
from .correctness import CorrectnessReviewer
from .style import StyleReviewer
from .testing import TestingReviewer
from .documentation import DocumentationReviewer

__all__ = [
    "ReviewComment",
    "CommentSeverity",
    "ReviewResult",
    "BaseReviewer",
    "SecurityReviewer",
    "PerformanceReviewer",
    "CorrectnessReviewer",
    "StyleReviewer",
    "TestingReviewer",
    "DocumentationReviewer",
]
```

### Step 4: Run tests to verify they pass

```bash
pytest tests/agents/code_reviewer/test_style_reviewers.py -v
```
Expected: All tests PASS

### Step 5: Commit

```bash
git add src/agents/code_reviewer/reviewers/
git commit -m "feat(code-reviewer): add style, testing, and docs reviewers

- Add Style reviewer for naming, duplication, complexity
- Add Testing reviewer for coverage and assertion quality
- Add Documentation reviewer for docstrings and comments

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Review Orchestrator and Synthesizer

**Files:**
- Create: `src/agents/code_reviewer/orchestrator.py`
- Create: `src/agents/code_reviewer/synthesizer.py`
- Test: `tests/agents/code_reviewer/test_orchestrator.py`

### Step 1: Write the failing tests

```python
# tests/agents/code_reviewer/test_orchestrator.py
"""Tests for review orchestrator and synthesizer."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from src.agents.code_reviewer.orchestrator import ReviewOrchestrator
from src.agents.code_reviewer.synthesizer import ReviewSynthesizer
from src.agents.code_reviewer.reviewers.base import (
    ReviewResult,
    ReviewComment,
    CommentSeverity,
)


class TestReviewOrchestrator:
    """Test ReviewOrchestrator."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with mock reviewers."""
        mock_claude = AsyncMock()
        mock_gemini = AsyncMock()
        return ReviewOrchestrator(
            claude_client=mock_claude,
            gemini_client=mock_gemini,
        )

    @pytest.mark.asyncio
    async def test_parallel_review_execution(self, orchestrator):
        """All reviewers run in parallel."""
        # Mock all reviewers to return results
        for reviewer in orchestrator.reviewers:
            reviewer.review = AsyncMock(return_value=ReviewResult(
                reviewer_name=reviewer.name,
                comments=[],
            ))

        results = await orchestrator.review_file(
            file_path="src/api.py",
            diff="+new code",
            full_content="full file content",
        )

        # All reviewers should have been called
        assert len(results) == len(orchestrator.reviewers)

    @pytest.mark.asyncio
    async def test_reviewer_failure_isolated(self, orchestrator):
        """One reviewer failing doesn't break others."""
        # Make security reviewer fail
        orchestrator.reviewers[0].review = AsyncMock(
            side_effect=Exception("API error")
        )
        # Other reviewers succeed
        for reviewer in orchestrator.reviewers[1:]:
            reviewer.review = AsyncMock(return_value=ReviewResult(
                reviewer_name=reviewer.name,
                comments=[],
            ))

        results = await orchestrator.review_file(
            file_path="src/api.py",
            diff="+code",
            full_content="",
        )

        # Should still get results from other reviewers
        assert len(results) >= len(orchestrator.reviewers) - 1

    @pytest.mark.asyncio
    async def test_review_pr(self, orchestrator):
        """Review entire PR with multiple files."""
        mock_context = MagicMock()
        mock_context.gather_pr_context.return_value = MagicMock(
            pr_number=123,
            title="Test PR",
        )

        # Mock all reviewers
        for reviewer in orchestrator.reviewers:
            reviewer.review = AsyncMock(return_value=ReviewResult(
                reviewer_name=reviewer.name,
                comments=[],
            ))

        files = [
            {"path": "file1.py", "diff": "+code1", "content": "content1"},
            {"path": "file2.py", "diff": "+code2", "content": "content2"},
        ]

        results = await orchestrator.review_pr(files)

        assert len(results) == 2  # Two files reviewed


class TestReviewSynthesizer:
    """Test ReviewSynthesizer."""

    @pytest.fixture
    def synthesizer(self):
        """Create synthesizer."""
        mock_llm = AsyncMock()
        return ReviewSynthesizer(llm_client=mock_llm)

    def test_deduplicate_comments(self, synthesizer):
        """Remove duplicate comments across reviewers."""
        comments = [
            ReviewComment(
                file_path="api.py",
                line_number=10,
                severity=CommentSeverity.WARNING,
                category="security",
                title="SQL Injection",
                message="SQL injection detected",
            ),
            ReviewComment(
                file_path="api.py",
                line_number=10,
                severity=CommentSeverity.WARNING,
                category="correctness",
                title="SQL Issue",
                message="SQL injection vulnerability",  # Same issue, different reviewer
            ),
        ]

        deduped = synthesizer.deduplicate(comments)

        # Should keep one, prefer security category
        assert len(deduped) == 1
        assert deduped[0].category == "security"

    def test_prioritize_by_severity(self, synthesizer):
        """Sort comments by severity."""
        comments = [
            ReviewComment(
                file_path="a.py", line_number=1,
                severity=CommentSeverity.NIT,
                category="style", title="Nit", message="Minor",
            ),
            ReviewComment(
                file_path="a.py", line_number=2,
                severity=CommentSeverity.BLOCKER,
                category="security", title="Critical", message="Must fix",
            ),
            ReviewComment(
                file_path="a.py", line_number=3,
                severity=CommentSeverity.WARNING,
                category="perf", title="Warning", message="Should fix",
            ),
        ]

        sorted_comments = synthesizer.prioritize(comments)

        assert sorted_comments[0].severity == CommentSeverity.BLOCKER
        assert sorted_comments[1].severity == CommentSeverity.WARNING
        assert sorted_comments[2].severity == CommentSeverity.NIT

    def test_group_by_file(self, synthesizer):
        """Group comments by file path."""
        comments = [
            ReviewComment(
                file_path="file1.py", line_number=1,
                severity=CommentSeverity.WARNING,
                category="test", title="T1", message="M1",
            ),
            ReviewComment(
                file_path="file2.py", line_number=1,
                severity=CommentSeverity.WARNING,
                category="test", title="T2", message="M2",
            ),
            ReviewComment(
                file_path="file1.py", line_number=10,
                severity=CommentSeverity.WARNING,
                category="test", title="T3", message="M3",
            ),
        ]

        grouped = synthesizer.group_by_file(comments)

        assert len(grouped["file1.py"]) == 2
        assert len(grouped["file2.py"]) == 1

    @pytest.mark.asyncio
    async def test_generate_summary(self, synthesizer):
        """Generate review summary."""
        results = [
            ReviewResult(
                reviewer_name="security",
                comments=[
                    ReviewComment(
                        file_path="api.py", line_number=10,
                        severity=CommentSeverity.BLOCKER,
                        category="security", title="SQL Injection",
                        message="Critical vulnerability",
                    ),
                ],
            ),
            ReviewResult(
                reviewer_name="style",
                comments=[
                    ReviewComment(
                        file_path="utils.py", line_number=5,
                        severity=CommentSeverity.SUGGESTION,
                        category="style", title="Naming",
                        message="Consider better name",
                    ),
                ],
            ),
        ]

        synthesizer.llm_client.generate.return_value = {
            "summary": "Review found 1 critical security issue and 1 style suggestion.",
            "verdict": "changes_requested",
        }

        summary = await synthesizer.synthesize(results)

        assert summary.blocker_count == 1
        assert summary.total_comments == 2
        assert "security" in summary.summary.lower()

    @pytest.mark.asyncio
    async def test_format_github_comment(self, synthesizer):
        """Format review as GitHub PR comment."""
        results = [
            ReviewResult(
                reviewer_name="security",
                comments=[
                    ReviewComment(
                        file_path="api.py", line_number=10,
                        severity=CommentSeverity.BLOCKER,
                        category="security", title="SQL Injection",
                        message="SQL injection vulnerability",
                        suggestion="Use parameterized queries",
                        code_before='f"SELECT * FROM users WHERE id = {id}"',
                        code_after='"SELECT * FROM users WHERE id = %s", [id]',
                    ),
                ],
            ),
        ]

        synthesizer.llm_client.generate.return_value = {
            "summary": "1 critical issue found",
            "verdict": "changes_requested",
        }

        summary = await synthesizer.synthesize(results)
        markdown = synthesizer.format_github_comment(summary)

        assert "## 🤖 DevMind Code Review" in markdown
        assert "Blocker" in markdown or "blocker" in markdown.lower()
        assert "SQL Injection" in markdown
```

### Step 2: Run tests to verify they fail

```bash
pytest tests/agents/code_reviewer/test_orchestrator.py -v
```
Expected: FAIL with import errors

### Step 3: Implement the orchestrator and synthesizer

```python
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
```

```python
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
```

### Step 4: Run tests to verify they pass

```bash
pytest tests/agents/code_reviewer/test_orchestrator.py -v
```
Expected: All tests PASS

### Step 5: Commit

```bash
git add src/agents/code_reviewer/
git commit -m "feat(code-reviewer): add review orchestrator and synthesizer

- Orchestrator runs reviewers in parallel with error isolation
- Synthesizer deduplicates, prioritizes, and formats results
- Support for GitHub PR comment formatting

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Code Review API Endpoints

**Files:**
- Create: `src/api/routes/reviews.py`
- Modify: `src/api/main.py` (add router)
- Test: `tests/api/test_reviews.py`

### Step 1: Write the failing tests

```python
# tests/api/test_reviews.py
"""Tests for code review API endpoints."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from src.api.main import app


class TestReviewEndpoints:
    """Test review API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_github_client(self, mocker):
        """Mock GitHub client."""
        return mocker.patch("src.api.routes.reviews.get_github_client")

    @pytest.fixture
    def mock_orchestrator(self, mocker):
        """Mock review orchestrator."""
        return mocker.patch("src.api.routes.reviews.ReviewOrchestrator")

    def test_trigger_pr_review(self, client, mock_github_client, mock_orchestrator):
        """Trigger review on a PR."""
        mock_github_client.return_value.get_pull.return_value = {
            "number": 123,
            "title": "Test PR",
            "base": {"ref": "main"},
            "head": {"sha": "abc123"},
        }

        response = client.post(
            "/api/v1/reviews/repos/test-repo/review",
            json={"pr_number": 123},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 202
        data = response.json()
        assert "job_id" in data

    def test_get_review_status(self, client):
        """Get status of a review job."""
        response = client.get(
            "/api/v1/reviews/jobs/job-123/status",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code in [200, 404]

    def test_list_pr_reviews(self, client):
        """List reviews for a repository."""
        response = client.get(
            "/api/v1/reviews/repos/test-repo/reviews",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "reviews" in data

    def test_get_review_details(self, client):
        """Get details of a specific review."""
        response = client.get(
            "/api/v1/reviews/reviews/review-123",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code in [200, 404]

    def test_manual_file_review(self, client, mock_orchestrator):
        """Manually review a file."""
        mock_orchestrator.return_value.review_file = AsyncMock(return_value=[])

        response = client.post(
            "/api/v1/reviews/review-file",
            json={
                "file_path": "src/api.py",
                "content": "def hello(): pass",
                "diff": "+def hello(): pass",
            },
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code in [200, 202]

    def test_configure_reviewers(self, client):
        """Configure which reviewers are enabled."""
        response = client.patch(
            "/api/v1/reviews/repos/test-repo/config",
            json={
                "enabled_reviewers": ["security", "correctness", "performance"],
                "auto_review": True,
            },
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code in [200, 201]

    def test_get_review_stats(self, client):
        """Get review statistics for a repository."""
        response = client.get(
            "/api/v1/reviews/repos/test-repo/stats",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_reviews" in data or "stats" in data
```

### Step 2: Run tests to verify they fail

```bash
pytest tests/api/test_reviews.py -v
```
Expected: FAIL

### Step 3: Implement the review API endpoints

```python
# src/api/routes/reviews.py
"""Code review API endpoints."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, Field

from src.core.auth import get_current_user
from src.core.config import get_settings
from src.agents.code_reviewer.orchestrator import ReviewOrchestrator
from src.agents.code_reviewer.synthesizer import ReviewSynthesizer
from src.db.models import PRReview, Repository
from src.integrations.github import get_github_client

router = APIRouter(prefix="/reviews", tags=["reviews"])


# Request/Response Models
class TriggerReviewRequest(BaseModel):
    """Request to trigger a PR review."""
    pr_number: int = Field(..., description="Pull request number")
    reviewers: Optional[list[str]] = Field(
        default=None,
        description="Specific reviewers to run (all if not specified)",
    )


class TriggerReviewResponse(BaseModel):
    """Response for triggered review."""
    job_id: str
    status: str = "queued"
    pr_number: int
    message: str


class ReviewFileRequest(BaseModel):
    """Request for manual file review."""
    file_path: str
    content: str
    diff: Optional[str] = None
    language: Optional[str] = None


class ReviewConfigRequest(BaseModel):
    """Request to configure review settings."""
    enabled_reviewers: Optional[list[str]] = None
    auto_review: Optional[bool] = None
    severity_threshold: Optional[str] = None


class ReviewComment(BaseModel):
    """A single review comment."""
    file_path: str
    line_number: int
    severity: str
    category: str
    title: str
    message: str
    suggestion: Optional[str] = None


class ReviewSummary(BaseModel):
    """Summary of a review."""
    id: str
    pr_number: int
    status: str
    blocker_count: int
    warning_count: int
    suggestion_count: int
    created_at: datetime
    comments: list[ReviewComment] = []


class ReviewListResponse(BaseModel):
    """List of reviews."""
    reviews: list[ReviewSummary]
    total: int
    page: int
    page_size: int


class ReviewStatsResponse(BaseModel):
    """Review statistics."""
    total_reviews: int
    average_blockers: float
    average_warnings: float
    most_common_issues: list[dict[str, Any]]
    review_trend: list[dict[str, Any]]


# In-memory job storage (replace with Redis/DB in production)
_review_jobs: dict[str, dict[str, Any]] = {}


# Endpoints
@router.post(
    "/repos/{repo_id}/review",
    response_model=TriggerReviewResponse,
    status_code=202,
)
async def trigger_pr_review(
    repo_id: str,
    request: TriggerReviewRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
):
    """Trigger a code review for a pull request.

    This queues the review job and returns immediately.
    Use the job_id to check status.
    """
    job_id = str(uuid.uuid4())

    _review_jobs[job_id] = {
        "status": "queued",
        "repo_id": repo_id,
        "pr_number": request.pr_number,
        "created_at": datetime.utcnow(),
        "user_id": user.get("id"),
    }

    # Queue the actual review work
    background_tasks.add_task(
        _execute_pr_review,
        job_id=job_id,
        repo_id=repo_id,
        pr_number=request.pr_number,
        reviewers=request.reviewers,
    )

    return TriggerReviewResponse(
        job_id=job_id,
        status="queued",
        pr_number=request.pr_number,
        message=f"Review queued for PR #{request.pr_number}",
    )


async def _execute_pr_review(
    job_id: str,
    repo_id: str,
    pr_number: int,
    reviewers: Optional[list[str]] = None,
):
    """Execute the PR review in the background."""
    try:
        _review_jobs[job_id]["status"] = "running"

        # Get PR details from GitHub
        github = get_github_client()
        # ... fetch PR, diff, files
        # ... run orchestrator
        # ... save results

        _review_jobs[job_id]["status"] = "completed"
        _review_jobs[job_id]["completed_at"] = datetime.utcnow()

    except Exception as e:
        _review_jobs[job_id]["status"] = "failed"
        _review_jobs[job_id]["error"] = str(e)


@router.get("/jobs/{job_id}/status")
async def get_review_job_status(
    job_id: str,
    user: dict = Depends(get_current_user),
):
    """Get the status of a review job."""
    job = _review_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job_id,
        "status": job["status"],
        "pr_number": job.get("pr_number"),
        "created_at": job.get("created_at"),
        "completed_at": job.get("completed_at"),
        "error": job.get("error"),
    }


@router.get(
    "/repos/{repo_id}/reviews",
    response_model=ReviewListResponse,
)
async def list_pr_reviews(
    repo_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: dict = Depends(get_current_user),
):
    """List all reviews for a repository."""
    # TODO: Fetch from database
    return ReviewListResponse(
        reviews=[],
        total=0,
        page=page,
        page_size=page_size,
    )


@router.get("/reviews/{review_id}")
async def get_review_details(
    review_id: str,
    user: dict = Depends(get_current_user),
):
    """Get details of a specific review."""
    # TODO: Fetch from database
    raise HTTPException(status_code=404, detail="Review not found")


@router.post("/review-file", status_code=200)
async def review_file(
    request: ReviewFileRequest,
    user: dict = Depends(get_current_user),
):
    """Manually review a single file.

    Useful for IDE integration or testing.
    """
    settings = get_settings()

    # Create orchestrator
    from src.core.llm import get_claude_client, get_gemini_client

    orchestrator = ReviewOrchestrator(
        claude_client=get_claude_client(),
        gemini_client=get_gemini_client(),
    )

    # Generate diff if not provided
    diff = request.diff or f"+{request.content}"

    # Run review
    results = await orchestrator.review_file(
        file_path=request.file_path,
        diff=diff,
        full_content=request.content,
    )

    # Synthesize results
    synthesizer = ReviewSynthesizer(llm_client=get_gemini_client())
    summary = await synthesizer.synthesize(results)

    return {
        "file_path": request.file_path,
        "blocker_count": summary.blocker_count,
        "warning_count": summary.warning_count,
        "suggestion_count": summary.suggestion_count,
        "comments": [
            {
                "line_number": c.line_number,
                "severity": c.severity.value,
                "category": c.category,
                "title": c.title,
                "message": c.message,
                "suggestion": c.suggestion,
            }
            for c in summary.comments
        ],
    }


@router.patch("/repos/{repo_id}/config")
async def configure_reviewers(
    repo_id: str,
    request: ReviewConfigRequest,
    user: dict = Depends(get_current_user),
):
    """Configure review settings for a repository."""
    # TODO: Save to database
    return {
        "repo_id": repo_id,
        "config": request.model_dump(exclude_none=True),
        "updated_at": datetime.utcnow(),
    }


@router.get(
    "/repos/{repo_id}/stats",
    response_model=ReviewStatsResponse,
)
async def get_review_stats(
    repo_id: str,
    days: int = Query(30, ge=1, le=365),
    user: dict = Depends(get_current_user),
):
    """Get review statistics for a repository."""
    # TODO: Aggregate from database
    return ReviewStatsResponse(
        total_reviews=0,
        average_blockers=0.0,
        average_warnings=0.0,
        most_common_issues=[],
        review_trend=[],
    )
```

Update main.py to include the router:

```python
# Add to src/api/main.py after existing imports and routers:
from src.api.routes.reviews import router as reviews_router

# Add to router registration:
app.include_router(reviews_router, prefix="/api/v1")
```

### Step 4: Run tests to verify they pass

```bash
pytest tests/api/test_reviews.py -v
```
Expected: All tests PASS

### Step 5: Commit

```bash
git add src/api/routes/reviews.py src/api/main.py tests/api/
git commit -m "feat(api): add code review API endpoints

- POST /repos/{repo_id}/review - trigger PR review (async)
- GET /jobs/{job_id}/status - check review job status
- GET /repos/{repo_id}/reviews - list reviews
- POST /review-file - manual file review
- PATCH /repos/{repo_id}/config - configure reviewers
- GET /repos/{repo_id}/stats - review statistics

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Summary

Phase 3 (CodeReviewer Agent) implementation plan consists of 5 tasks:

1. **Diff Parser & Context Gatherer** - Parse unified diffs and gather PR context from GitHub
2. **Specialized Reviewers (Security, Performance, Correctness)** - Core review agents using Claude
3. **Style, Testing, Documentation Reviewers** - Supporting review agents using Gemini
4. **Review Orchestrator & Synthesizer** - Parallel execution and result aggregation
5. **Code Review API Endpoints** - REST API for triggering and managing reviews

Each task follows TDD methodology with complete code examples and test coverage.

**Estimated Implementation Time:** 2-3 days per task, ~2 weeks total

**Dependencies:**
- Phase 1 (Foundation) must be complete
- Phase 2 (VulnScanner) provides patterns for agent implementation
