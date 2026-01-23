import pytest
from unittest.mock import AsyncMock, MagicMock
from src.integrations.github.commenter import GitHubCommenter

@pytest.mark.asyncio
async def test_post_review_comment():
    mock_gh = MagicMock()
    mock_repo = MagicMock()
    mock_pr = MagicMock()
    mock_comment = MagicMock()

    mock_gh.get_repo.return_value = mock_repo
    mock_repo.get_pull.return_value = mock_pr
    mock_pr.create_issue_comment.return_value = mock_comment
    mock_comment.html_url = "http://github.com/comment/1"

    commenter = GitHubCommenter(mock_gh)

    review_summary = {
        "blocker_count": 0,
        "warning_count": 2,
        "suggestion_count": 1,
        "summary": "Good job but check warnings."
    }

    url = await commenter.post_review_comment("owner/repo", 1, review_summary)

    assert url == "http://github.com/comment/1"
    mock_pr.create_issue_comment.assert_called_once()
    args = mock_pr.create_issue_comment.call_args[0][0]
    assert "✅ Approved" in args
    assert "🟠 Warning | 2" in args

@pytest.mark.asyncio
async def test_post_inline_comments():
    mock_gh = MagicMock()
    mock_repo = MagicMock()
    mock_pr = MagicMock()
    mock_commit = MagicMock()

    mock_gh.get_repo.return_value = mock_repo
    mock_repo.get_pull.return_value = mock_pr
    mock_repo.get_commit.return_value = mock_commit

    commenter = GitHubCommenter(mock_gh)

    comments = [
        {
            "file_path": "src/main.py",
            "line_number": 10,
            "severity": "blocker",
            "title": "Bug",
            "message": "Fix this",
            "suggestion": "code"
        }
    ]

    count = await commenter.post_inline_comments("owner/repo", 1, comments, "sha123")

    assert count == 1
    mock_pr.create_review_comment.assert_called_once()
    call_args = mock_pr.create_review_comment.call_args[1]
    assert call_args["path"] == "src/main.py"
    assert "🔴 **Bug**" in call_args["body"]
    assert "```suggestion" in call_args["body"]

@pytest.mark.asyncio
async def test_create_check_run():
    mock_gh = MagicMock()
    mock_repo = MagicMock()
    mock_check_run = MagicMock()

    mock_gh.get_repo.return_value = mock_repo
    mock_repo.create_check_run.return_value = mock_check_run
    mock_check_run.html_url = "http://github.com/check/1"

    commenter = GitHubCommenter(mock_gh)

    url = await commenter.create_check_run("owner/repo", "sha123", "Security Scan", "success", "All good")

    assert url == "http://github.com/check/1"
    mock_repo.create_check_run.assert_called_once()
    assert mock_repo.create_check_run.call_args[1]["conclusion"] == "success"
