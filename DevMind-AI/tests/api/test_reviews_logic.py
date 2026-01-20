"""Tests for review logic."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.api.routes.reviews import _execute_pr_review
from src.db.models import Repository

class MockSession:
    def __init__(self):
        self.add = MagicMock()
        self.commit = AsyncMock()
        self.execute = AsyncMock()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

@pytest.mark.asyncio
async def test_execute_pr_review_success():
    """Test successful execution of PR review."""
    job_id = "job-123"
    repo_id = "test-repo"
    pr_number = 1

    # Mocks
    mock_repo = MagicMock(spec=Repository)
    mock_repo.id = "repo-uuid"
    mock_repo.full_name = "owner/repo"

    mock_github = MagicMock()
    mock_github.get_pr_files.return_value = [
        {"filename": "file.py", "status": "modified", "patch": "diff"}
    ]

    mock_context_gatherer = MagicMock()
    mock_context_gatherer.gather_pr_context.return_value = MagicMock(
        base_branch="main", head_sha="sha"
    )
    mock_context_gatherer.gather_file_context.return_value = MagicMock(
        content_after="content"
    )

    mock_orchestrator = AsyncMock()
    mock_orchestrator.review_file.return_value = []

    mock_synthesizer = AsyncMock()
    mock_synthesizer.synthesize.return_value = MagicMock(
        summary="Summary", comments=[], blocker_count=0, warning_count=0
    )

    # Setup session result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_repo

    mock_session = MockSession()
    mock_session.execute.return_value = mock_result

    # Patches
    with patch("src.api.routes.reviews.async_session", return_value=mock_session), \
         patch("src.api.routes.reviews.get_github_client", return_value=mock_github), \
         patch("src.api.routes.reviews.ContextGatherer", return_value=mock_context_gatherer), \
         patch("src.api.routes.reviews.DiffParser"), \
         patch("src.api.routes.reviews.ReviewOrchestrator", return_value=mock_orchestrator), \
         patch("src.api.routes.reviews.get_claude_client"), \
         patch("src.api.routes.reviews.get_gemini_client"), \
         patch("src.api.routes.reviews.ReviewSynthesizer", return_value=mock_synthesizer), \
         patch("src.api.routes.reviews._review_jobs", {job_id: {}}):

        # Execute
        await _execute_pr_review(job_id, repo_id, pr_number)

        # Verify
        mock_session.add.assert_called_once() # Should add PRReview
        mock_session.commit.assert_called_once()
        assert mock_orchestrator.review_file.called
