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
        # Print routes for debugging
        # for route in app.routes:
        #     print(f"Route: {route.path} {route.methods}")
        return TestClient(app)

    def test_trigger_pr_review(self, client):
        """Trigger review on a PR."""
        with patch("src.api.routes.reviews.get_github_client") as mock_github_client:
            mock_github_client.return_value.get_pull.return_value = {
                "number": 123,
                "title": "Test PR",
                "base": {"ref": "main"},
                "head": {"sha": "abc123"},
            }

            with patch("src.api.routes.reviews.ReviewOrchestrator"):
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

    def test_manual_file_review(self, client):
        """Manually review a file."""
        with patch("src.api.routes.reviews.ReviewOrchestrator") as mock_orchestrator, \
             patch("src.api.routes.reviews.ReviewSynthesizer") as mock_synthesizer:

            # Configure mock orchestrator
            mock_instance = mock_orchestrator.return_value
            mock_instance.review_file = AsyncMock(return_value=[])

            # Configure mock synthesizer
            mock_synth_instance = mock_synthesizer.return_value
            mock_synth_instance.synthesize = AsyncMock(return_value=MagicMock(
                blocker_count=0,
                warning_count=0,
                suggestion_count=0,
                comments=[]
            ))

            response = client.post(
                "/api/v1/reviews/review-file",
                json={
                    "file_path": "src/api.py",
                    "content": "def hello(): pass",
                    "diff": "+def hello(): pass",
                },
                headers={"Authorization": "Bearer test-token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert "blocker_count" in data

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

        assert response.status_code == 200

    def test_get_review_stats(self, client):
        """Get review statistics for a repository."""
        response = client.get(
            "/api/v1/reviews/repos/test-repo/stats",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_reviews" in data
