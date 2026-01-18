"""Tests for security API routes."""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def client():
    """Create test client."""
    from src.api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


class TestSecurityEndpoints:
    """Test suite for security API endpoints."""

    @pytest.mark.asyncio
    async def test_trigger_scan_returns_scan_id(self, client: AsyncClient):
        """POST /api/v1/security/{repo_id}/scan should return scan ID."""
        repo_id = str(uuid.uuid4())

        with patch("src.api.routes.security.trigger_vulnerability_scan") as mock_trigger:
            mock_trigger.return_value = {
                "id": str(uuid.uuid4()),
                "repo_id": repo_id,
                "commit_sha": "HEAD",
                "status": "pending",
                "started_at": "2024-01-01T00:00:00Z",
                "triggered_by": "manual",
            }

            response = await client.post(
                f"/api/v1/security/{repo_id}/scan",
                json={"full_scan": False},
            )

            assert response.status_code == 202
            data = response.json()
            assert "id" in data
            assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_list_vulnerabilities(self, client: AsyncClient):
        """GET /api/v1/security/{repo_id}/vulns should return vulnerabilities."""
        repo_id = str(uuid.uuid4())

        with patch("src.api.routes.security.get_vulnerabilities") as mock_get:
            mock_get.return_value = [
                {
                    "id": str(uuid.uuid4()),
                    "scan_id": str(uuid.uuid4()),
                    "repo_id": repo_id,
                    "cve_id": "CVE-2024-1234",
                    "package_name": "lodash",
                    "severity": "high",
                    "status": "open",
                    "first_seen_at": "2024-01-01T00:00:00Z",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                }
            ]

            response = await client.get(f"/api/v1/security/{repo_id}/vulns")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]["cve_id"] == "CVE-2024-1234"

    @pytest.mark.asyncio
    async def test_filter_vulnerabilities_by_severity(self, client: AsyncClient):
        """Should filter vulnerabilities by severity."""
        repo_id = str(uuid.uuid4())

        with patch("src.api.routes.security.get_vulnerabilities") as mock_get:
            mock_get.return_value = []

            response = await client.get(
                f"/api/v1/security/{repo_id}/vulns",
                params={"severity": "critical"},
            )

            assert response.status_code == 200
            mock_get.assert_called_once()
            # Verify severity filter was passed
            call_kwargs = mock_get.call_args.kwargs
            assert call_kwargs.get("severity") == "critical"
