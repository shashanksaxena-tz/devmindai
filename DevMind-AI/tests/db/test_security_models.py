"""Tests for security-related database models."""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.db.base import Base
# Import models to register them with Base.metadata
from src.db.models.organization import Organization
from src.db.models.repository import Repository
from src.db.models.security import Vulnerability, VulnerabilityScan


@pytest.fixture
async def db_session():
    """Create an in-memory SQLite database session for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    await engine.dispose()


class TestVulnerabilityScanModel:
    """Test suite for VulnerabilityScan model."""

    @pytest.mark.asyncio
    async def test_create_vulnerability_scan(self, db_session: AsyncSession):
        """Should create a vulnerability scan."""
        from src.db.models.organization import Organization
        from src.db.models.repository import Repository
        from src.db.models.security import VulnerabilityScan

        # Setup
        org = Organization(name="Test Org", slug="test-org")
        db_session.add(org)
        await db_session.commit()

        repo = Repository(
            org_id=org.id,
            github_repo_id=123,
            name="test-repo",
            full_name="test-org/test-repo",
        )
        db_session.add(repo)
        await db_session.commit()

        # Create scan
        scan = VulnerabilityScan(
            repo_id=repo.id,
            commit_sha="abc123def456",
            status="pending",
            triggered_by="manual",
        )

        db_session.add(scan)
        await db_session.commit()
        await db_session.refresh(scan)

        assert scan.id is not None
        assert scan.repo_id == repo.id
        assert scan.status == "pending"
        assert scan.summary is None


class TestVulnerabilityModel:
    """Test suite for Vulnerability model."""

    @pytest.mark.asyncio
    async def test_create_vulnerability(self, db_session: AsyncSession):
        """Should create a vulnerability with all fields."""
        from src.db.models.organization import Organization
        from src.db.models.repository import Repository
        from src.db.models.security import Vulnerability, VulnerabilityScan

        # Setup
        org = Organization(name="Test Org", slug="test-org")
        db_session.add(org)
        await db_session.commit()

        repo = Repository(
            org_id=org.id,
            github_repo_id=123,
            name="test-repo",
            full_name="test-org/test-repo",
        )
        db_session.add(repo)
        await db_session.commit()

        scan = VulnerabilityScan(
            repo_id=repo.id,
            commit_sha="abc123",
            status="completed",
        )
        db_session.add(scan)
        await db_session.commit()

        # Create vulnerability
        vuln = Vulnerability(
            scan_id=scan.id,
            repo_id=repo.id,
            cve_id="CVE-2024-1234",
            package_name="lodash",
            package_version="4.17.20",
            severity="high",
            cvss_score=Decimal("7.5"),
            title="Prototype Pollution in lodash",
            description="A prototype pollution vulnerability exists in lodash.",
            fix_version="4.17.21",
            is_exploitable=True,
            exploit_path="src/utils/helpers.js:42",
            status="open",
        )

        db_session.add(vuln)
        await db_session.commit()
        await db_session.refresh(vuln)

        assert vuln.id is not None
        assert vuln.cve_id == "CVE-2024-1234"
        assert vuln.severity == "high"
        assert vuln.is_exploitable is True
        assert vuln.status == "open"
