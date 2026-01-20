"""Tests for Pydantic schemas."""

import uuid
from datetime import datetime, timezone

import pytest


class TestOrganizationSchemas:
    """Test suite for Organization schemas."""

    def test_organization_create_schema(self):
        """Should validate organization creation data."""
        from src.api.schemas.organization import OrganizationCreate

        data = OrganizationCreate(
            name="Test Organization",
            slug="test-org",
        )

        assert data.name == "Test Organization"
        assert data.slug == "test-org"

    def test_organization_response_schema(self):
        """Should serialize organization response."""
        from src.api.schemas.organization import OrganizationResponse

        org_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        data = OrganizationResponse(
            id=org_id,
            name="Test Org",
            slug="test-org",
            plan="free",
            settings={},
            created_at=now,
            updated_at=now,
        )

        assert data.id == org_id
        assert data.plan == "free"


class TestRepositorySchemas:
    """Test suite for Repository schemas."""

    def test_repository_response_schema(self):
        """Should serialize repository response."""
        from src.api.schemas.repository import RepositoryResponse

        repo_id = uuid.uuid4()
        org_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        data = RepositoryResponse(
            id=repo_id,
            org_id=org_id,
            github_repo_id=12345,
            name="test-repo",
            full_name="org/test-repo",
            default_branch="main",
            language="Python",
            is_active=True,
            health_score=85,
            created_at=now,
            updated_at=now,
        )

        assert data.full_name == "org/test-repo"
        assert data.health_score == 85


class TestSecuritySchemas:
    """Test suite for Security schemas."""

    def test_vulnerability_response_schema(self):
        """Should serialize vulnerability response."""
        from src.api.schemas.security import VulnerabilityResponse

        vuln_id = uuid.uuid4()
        repo_id = uuid.uuid4()
        scan_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        data = VulnerabilityResponse(
            id=vuln_id,
            scan_id=scan_id,
            repo_id=repo_id,
            cve_id="CVE-2024-1234",
            package_name="lodash",
            package_version="4.17.20",
            severity="high",
            cvss_score=7.5,
            title="Prototype Pollution",
            is_exploitable=True,
            status="open",
            first_seen_at=now,
            created_at=now,
            updated_at=now,
        )

        assert data.cve_id == "CVE-2024-1234"
        assert data.is_exploitable is True

    def test_scan_request_schema(self):
        """Should validate scan request data."""
        from src.api.schemas.security import ScanRequest

        data = ScanRequest(full_scan=True)

        assert data.full_scan is True
        assert data.commit_sha is None
