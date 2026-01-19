# tests/agents/code_reviewer/test_context_gatherer.py
"""Tests for ContextGatherer."""
import pytest
from src.agents.code_reviewer.context_gatherer import ContextGatherer


class TestContextGatherer:
    """Test suite for ContextGatherer."""

    @pytest.fixture
    def mock_github_client(self, mocker):
        """Create mock GitHub client."""
        return mocker.MagicMock()

    def test_gather_pr_context(self, mock_github_client):
        """Gather full PR context including description and linked issues."""
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
        mock_github_client.get_file_content.return_value = b"def hello(): pass"

        gatherer = ContextGatherer(mock_github_client)
        content = gatherer.get_file_at_commit(
            "owner", "repo", "src/hello.py", "abc123"
        )

        assert content == "def hello(): pass"

    def test_get_recent_commits_to_file(self, mock_github_client):
        """Get recent commit history for a file."""
        mock_github_client.get_commits.return_value = [
            {
                "sha": "abc",
                "commit": {
                    "message": "Fix bug",
                    "author": {"name": "Dev", "date": "2024-01-01"},
                },
            },
            {
                "sha": "def",
                "commit": {
                    "message": "Initial impl",
                    "author": {"name": "Dev", "date": "2024-01-01"},
                },
            },
        ]

        gatherer = ContextGatherer(mock_github_client)
        commits = gatherer.get_file_history(
            "owner", "repo", "src/file.py", limit=5
        )

        assert len(commits) == 2
        assert commits[0]["message"] == "Fix bug"
