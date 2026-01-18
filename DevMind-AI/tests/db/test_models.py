"""Tests for database models."""

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.db.base import Base
# Import models to register them with Base.metadata
from src.db.models.organization import Organization
from src.db.models.repository import Repository
from src.db.models.user import User


@pytest.fixture
async def db_session():
    """Create an in-memory SQLite database session for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    await engine.dispose()


class TestOrganizationModel:
    """Test suite for Organization model."""

    @pytest.mark.asyncio
    async def test_create_organization(self, db_session: AsyncSession):
        """Should create an organization with all required fields."""
        from src.db.models.organization import Organization

        org = Organization(
            name="Test Organization",
            slug="test-org",
        )

        db_session.add(org)
        await db_session.commit()
        await db_session.refresh(org)

        assert org.id is not None
        assert isinstance(org.id, uuid.UUID)
        assert org.name == "Test Organization"
        assert org.slug == "test-org"
        assert org.plan == "free"
        assert org.settings == {}
        assert org.created_at is not None

    @pytest.mark.asyncio
    async def test_organization_with_github_org_id(self, db_session: AsyncSession):
        """Should store GitHub organization ID."""
        from src.db.models.organization import Organization

        org = Organization(
            name="GitHub Org",
            slug="github-org",
            github_org_id=12345678,
        )

        db_session.add(org)
        await db_session.commit()
        await db_session.refresh(org)

        assert org.github_org_id == 12345678

    @pytest.mark.asyncio
    async def test_organization_settings_json(self, db_session: AsyncSession):
        """Should store settings as JSON."""
        from src.db.models.organization import Organization

        org = Organization(
            name="Configured Org",
            slug="configured-org",
            settings={"notifications": {"slack": True, "email": False}},
        )

        db_session.add(org)
        await db_session.commit()
        await db_session.refresh(org)

        assert org.settings["notifications"]["slack"] is True


class TestUserModel:
    """Test suite for User model."""

    @pytest.mark.asyncio
    async def test_create_user(self, db_session: AsyncSession):
        """Should create a user with all required fields."""
        from src.db.models.user import User

        user = User(
            email="test@example.com",
            name="Test User",
            github_user_id=12345,
            github_username="testuser",
        )

        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.github_username == "testuser"


class TestRepositoryModel:
    """Test suite for Repository model."""

    @pytest.mark.asyncio
    async def test_create_repository(self, db_session: AsyncSession):
        """Should create a repository linked to an organization."""
        from src.db.models.organization import Organization
        from src.db.models.repository import Repository

        # Create org first
        org = Organization(name="Test Org", slug="test-org")
        db_session.add(org)
        await db_session.commit()

        # Create repo
        repo = Repository(
            org_id=org.id,
            github_repo_id=987654321,
            name="test-repo",
            full_name="test-org/test-repo",
            default_branch="main",
            language="Python",
        )

        db_session.add(repo)
        await db_session.commit()
        await db_session.refresh(repo)

        assert repo.id is not None
        assert repo.org_id == org.id
        assert repo.full_name == "test-org/test-repo"
        assert repo.is_active is True
        assert repo.health_score is None
