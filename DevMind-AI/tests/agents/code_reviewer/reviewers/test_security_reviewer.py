"""Tests for SecurityReviewer."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.agents.code_reviewer.reviewers.security import SecurityReviewer
from src.agents.code_reviewer.reviewers.base import ReviewResult, CommentSeverity


class TestSecurityReviewer:
    """Test suite for SecurityReviewer."""

    @pytest.fixture
    def mock_llm_client(self):
        """Create mock LLM client."""
        client = AsyncMock()
        return client

    @pytest.mark.asyncio
    async def test_review_detects_issues(self, mock_llm_client):
        """Should detect security issues using LLM."""
        # Setup mock response
        mock_response = {
            "issues": [
                {
                    "type": "sql_injection",
                    "severity": "blocker",
                    "line": 10,
                    "message": "Potential SQL injection in query construction",
                    "fix": "Use parameterized queries",
                }
            ]
        }
        mock_llm_client.generate_structured.return_value = mock_response

        reviewer = SecurityReviewer(mock_llm_client)

        # Execute
        result = await reviewer.review(
            file_path="src/db.py",
            diff="+ query = f'SELECT * FROM users WHERE name = {name}'",
            full_content="def get_user(name):\n    query = f'SELECT * FROM users WHERE name = {name}'"
        )

        # Assertions
        assert isinstance(result, ReviewResult)
        assert len(result.comments) == 1
        assert result.comments[0].category == "security"
        assert result.comments[0].severity == CommentSeverity.BLOCKER
        assert result.comments[0].line_number == 10

        # Verify generate_structured called
        mock_llm_client.generate_structured.assert_called_once()
        args, kwargs = mock_llm_client.generate_structured.call_args
        assert "schema" in kwargs
        assert "system_prompt" in kwargs
