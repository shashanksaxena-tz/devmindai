# DevMind AI - Phase 1: Foundation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the foundational infrastructure for DevMind AI including project setup, database models, core API, authentication, and the first working agent (VulnScanner).

**Architecture:** FastAPI backend with Celery workers, PostgreSQL for persistence, Redis for caching/queues, Qdrant for vector storage. Multi-agent system using Agno framework with Claude and Gemini as LLM providers.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy 2.0, Celery, Redis, PostgreSQL, Qdrant, Agno, Anthropic SDK, Google GenerativeAI SDK, Pydantic v2, Alembic, pytest

---

## Task 1: Project Configuration

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `README.md`

**Step 1: Create pyproject.toml**

```toml
[project]
name = "devmind-ai"
version = "0.1.0"
description = "AI-powered developer platform with 10 intelligent agents"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    # Web Framework
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "python-multipart>=0.0.6",

    # Database
    "sqlalchemy[asyncio]>=2.0.25",
    "asyncpg>=0.29.0",
    "alembic>=1.13.1",

    # Redis & Celery
    "redis>=5.0.1",
    "celery[redis]>=5.3.6",

    # Vector Database
    "qdrant-client>=1.7.0",

    # LLM Providers
    "anthropic>=0.18.0",
    "google-generativeai>=0.3.2",
    "openai>=1.12.0",

    # Agent Framework
    "agno>=2.10.0",

    # Authentication
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "httpx>=0.26.0",

    # Utilities
    "pydantic>=2.6.0",
    "pydantic-settings>=2.1.0",
    "python-dotenv>=1.0.1",
    "structlog>=24.1.0",
    "tenacity>=8.2.3",

    # Code Analysis
    "tree-sitter>=0.20.4",
    "gitpython>=3.1.41",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.4",
    "pytest-cov>=4.1.0",
    "httpx>=0.26.0",
    "ruff>=0.2.0",
    "mypy>=1.8.0",
    "pre-commit>=3.6.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "-v --cov=src --cov-report=term-missing"

[tool.mypy]
python_version = "3.11"
strict = true
```

**Step 2: Create .env.example**

```bash
# Database
DATABASE_URL=postgresql+asyncpg://devmind:devmind@localhost:5432/devmind

# Redis
REDIS_URL=redis://localhost:6379/0

# Qdrant
QDRANT_URL=http://localhost:6333

# LLM API Keys
ANTHROPIC_API_KEY=sk-ant-xxx
GOOGLE_API_KEY=xxx
OPENAI_API_KEY=sk-xxx

# GitHub App
GITHUB_APP_ID=123456
GITHUB_CLIENT_ID=Iv1.xxx
GITHUB_CLIENT_SECRET=xxx
GITHUB_PRIVATE_KEY_PATH=./config/github-app.pem
GITHUB_WEBHOOK_SECRET=xxx

# Security
SECRET_KEY=your-secret-key-at-least-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
APP_NAME=DevMind AI
APP_ENV=development
DEBUG=true
API_V1_PREFIX=/api/v1
```

**Step 3: Create .gitignore**

```
# Byte-compiled
__pycache__/
*.py[cod]
*$py.class
*.so

# Distribution
dist/
build/
*.egg-info/

# Virtual environments
.venv/
venv/
ENV/

# Environment
.env
.env.local
*.pem

# IDE
.idea/
.vscode/
*.swp
*.swo

# Testing
.coverage
htmlcov/
.pytest_cache/

# Logs
*.log
logs/

# Database
*.db
*.sqlite

# OS
.DS_Store
Thumbs.db
```

**Step 4: Create README.md**

```markdown
# DevMind AI

AI-powered developer platform with 10 intelligent agents for code review, security scanning, test generation, and more.

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker (optional)

### Setup

1. Clone and install dependencies:
```bash
cd DevMind-AI
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

2. Copy environment file:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Start services (Docker):
```bash
docker-compose up -d postgres redis qdrant
```

4. Run migrations:
```bash
alembic upgrade head
```

5. Start the API:
```bash
uvicorn src.api.main:app --reload
```

## Project Structure

```
DevMind-AI/
├── src/
│   ├── api/           # FastAPI routes and middleware
│   ├── agents/        # AI agent implementations
│   ├── core/          # Core business logic
│   ├── db/            # Database models and migrations
│   ├── integrations/  # External service integrations
│   └── utils/         # Shared utilities
├── tests/             # Test suite
├── dashboard/         # Streamlit dashboard
├── config/            # Configuration files
└── docs/              # Documentation
```

## Agents

1. **VulnScanner** - Security vulnerability detection
2. **CodeReviewer** - Automated PR reviews
3. **TestGenerator** - AI-generated test suites
4. **DebtAnalyzer** - Technical debt tracking
5. **DocGenerator** - Automated documentation
6. **IncidentResponder** - Alert correlation & diagnosis
7. **CodeMigrator** - Framework/language migrations
8. **QueryOptimizer** - Database query optimization
9. **ADRRecorder** - Architecture decision recording
10. **PipelineGenerator** - CI/CD pipeline generation

## License

MIT
```

**Step 5: Commit**

```bash
git add pyproject.toml .env.example .gitignore README.md
git commit -m "chore: initialize DevMind AI project configuration"
```

---

## Task 2: Core Configuration Module

**Files:**
- Create: `src/__init__.py`
- Create: `src/core/__init__.py`
- Create: `src/core/config.py`
- Test: `tests/__init__.py`
- Test: `tests/core/__init__.py`
- Test: `tests/core/test_config.py`

**Step 1: Create package init files**

Create `src/__init__.py`:
```python
"""DevMind AI - Intelligent Developer Platform."""
```

Create `src/core/__init__.py`:
```python
"""Core module for DevMind AI."""

from src.core.config import settings

__all__ = ["settings"]
```

**Step 2: Write the failing test for config**

Create `tests/__init__.py`:
```python
"""Tests for DevMind AI."""
```

Create `tests/core/__init__.py`:
```python
"""Tests for core module."""
```

Create `tests/core/test_config.py`:
```python
"""Tests for configuration module."""

import os
from unittest.mock import patch

import pytest


class TestSettings:
    """Test suite for Settings configuration."""

    def test_settings_loads_from_environment(self):
        """Settings should load values from environment variables."""
        from src.core.config import Settings

        with patch.dict(os.environ, {
            "DATABASE_URL": "postgresql+asyncpg://test:test@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "SECRET_KEY": "test-secret-key-at-least-32-chars",
            "ANTHROPIC_API_KEY": "sk-ant-test",
            "GOOGLE_API_KEY": "test-google-key",
        }):
            settings = Settings()
            assert settings.DATABASE_URL == "postgresql+asyncpg://test:test@localhost/test"
            assert settings.REDIS_URL == "redis://localhost:6379/0"
            assert settings.SECRET_KEY == "test-secret-key-at-least-32-chars"

    def test_settings_has_required_fields(self):
        """Settings should have all required configuration fields."""
        from src.core.config import Settings

        with patch.dict(os.environ, {
            "DATABASE_URL": "postgresql+asyncpg://test:test@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "SECRET_KEY": "test-secret-key-at-least-32-chars",
            "ANTHROPIC_API_KEY": "sk-ant-test",
            "GOOGLE_API_KEY": "test-google-key",
        }):
            settings = Settings()

            # Check all required fields exist
            assert hasattr(settings, "APP_NAME")
            assert hasattr(settings, "APP_ENV")
            assert hasattr(settings, "DEBUG")
            assert hasattr(settings, "API_V1_PREFIX")
            assert hasattr(settings, "DATABASE_URL")
            assert hasattr(settings, "REDIS_URL")
            assert hasattr(settings, "QDRANT_URL")
            assert hasattr(settings, "ANTHROPIC_API_KEY")
            assert hasattr(settings, "GOOGLE_API_KEY")

    def test_settings_default_values(self):
        """Settings should have sensible defaults."""
        from src.core.config import Settings

        with patch.dict(os.environ, {
            "DATABASE_URL": "postgresql+asyncpg://test:test@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "SECRET_KEY": "test-secret-key-at-least-32-chars",
            "ANTHROPIC_API_KEY": "sk-ant-test",
            "GOOGLE_API_KEY": "test-google-key",
        }):
            settings = Settings()

            assert settings.APP_NAME == "DevMind AI"
            assert settings.API_V1_PREFIX == "/api/v1"
            assert settings.QDRANT_URL == "http://localhost:6333"
```

**Step 3: Run test to verify it fails**

```bash
cd DevMind-AI
pip install -e ".[dev]"
pytest tests/core/test_config.py -v
```
Expected: FAIL with "ModuleNotFoundError: No module named 'src.core.config'"

**Step 4: Write the implementation**

Create `src/core/config.py`:
```python
"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "DevMind AI"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"

    # LLM API Keys
    ANTHROPIC_API_KEY: str
    GOOGLE_API_KEY: str
    OPENAI_API_KEY: str | None = None

    # GitHub App
    GITHUB_APP_ID: int | None = None
    GITHUB_CLIENT_ID: str | None = None
    GITHUB_CLIENT_SECRET: str | None = None
    GITHUB_PRIVATE_KEY_PATH: str | None = None
    GITHUB_WEBHOOK_SECRET: str | None = None

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.APP_ENV == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.APP_ENV == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
```

**Step 5: Run test to verify it passes**

```bash
pytest tests/core/test_config.py -v
```
Expected: PASS (3 tests)

**Step 6: Commit**

```bash
git add src/ tests/
git commit -m "feat: add core configuration module with Pydantic settings"
```

---

## Task 3: Database Models - Base and Organizations

**Files:**
- Create: `src/db/__init__.py`
- Create: `src/db/base.py`
- Create: `src/db/session.py`
- Create: `src/db/models/__init__.py`
- Create: `src/db/models/organization.py`
- Test: `tests/db/__init__.py`
- Test: `tests/db/test_models.py`

**Step 1: Create db package init**

Create `src/db/__init__.py`:
```python
"""Database module for DevMind AI."""

from src.db.base import Base
from src.db.session import async_session, engine, get_db

__all__ = ["Base", "async_session", "engine", "get_db"]
```

**Step 2: Write failing test for database models**

Create `tests/db/__init__.py`:
```python
"""Tests for database module."""
```

Create `tests/db/test_models.py`:
```python
"""Tests for database models."""

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.db.base import Base


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
```

**Step 3: Run test to verify it fails**

```bash
pip install aiosqlite  # For testing with SQLite
pytest tests/db/test_models.py -v
```
Expected: FAIL with "ModuleNotFoundError"

**Step 4: Write the implementation**

Create `src/db/base.py`:
```python
"""SQLAlchemy base model with common fields."""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
```

Create `src/db/session.py`:
```python
"""Database session management."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database sessions."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

Create `src/db/models/__init__.py`:
```python
"""Database models for DevMind AI."""

from src.db.models.organization import Organization
from src.db.models.repository import Repository
from src.db.models.user import User

__all__ = [
    "Organization",
    "Repository",
    "User",
]
```

Create `src/db/models/organization.py`:
```python
"""Organization model."""

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.db.models.repository import Repository
    from src.db.models.user import OrgMember


class Organization(Base):
    """Organization/team that owns repositories."""

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    github_org_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, nullable=True)
    plan: Mapped[str] = mapped_column(String(50), default="free", nullable=False)
    settings: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    repositories: Mapped[list["Repository"]] = relationship(
        "Repository", back_populates="organization", cascade="all, delete-orphan"
    )
    members: Mapped[list["OrgMember"]] = relationship(
        "OrgMember", back_populates="organization", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name={self.name}, slug={self.slug})>"
```

Create `src/db/models/user.py`:
```python
"""User and organization membership models."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.db.models.organization import Organization


class User(Base):
    """User account."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    github_user_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, nullable=True)
    github_username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    settings: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    memberships: Mapped[list["OrgMember"]] = relationship(
        "OrgMember", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"


class OrgMember(Base):
    """Organization membership linking users to organizations."""

    __tablename__ = "org_members"

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(50), default="member", nullable=False)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="memberships")

    def __repr__(self) -> str:
        return f"<OrgMember(org_id={self.org_id}, user_id={self.user_id}, role={self.role})>"
```

Create `src/db/models/repository.py`:
```python
"""Repository model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.db.models.organization import Organization


class Repository(Base):
    """GitHub repository connected to DevMind."""

    __tablename__ = "repositories"

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    github_repo_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(500), nullable=False)
    default_branch: Mapped[str] = mapped_column(String(100), default="main", nullable=False)
    language: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    config: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    last_scan_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    health_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="repositories")

    def __repr__(self) -> str:
        return f"<Repository(id={self.id}, full_name={self.full_name})>"
```

**Step 5: Run test to verify it passes**

```bash
pytest tests/db/test_models.py -v
```
Expected: PASS (5 tests)

**Step 6: Commit**

```bash
git add src/db/ tests/db/
git commit -m "feat: add database models for organizations, users, and repositories"
```

---

## Task 4: Security Models (Vulnerabilities, Scans)

**Files:**
- Create: `src/db/models/security.py`
- Modify: `src/db/models/__init__.py`
- Test: `tests/db/test_security_models.py`

**Step 1: Write failing test**

Create `tests/db/test_security_models.py`:
```python
"""Tests for security-related database models."""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.db.base import Base


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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/db/test_security_models.py -v
```
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write the implementation**

Create `src/db/models/security.py`:
```python
"""Security-related database models."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.db.models.repository import Repository
    from src.db.models.user import User


class VulnerabilityScan(Base):
    """Record of a vulnerability scan run."""

    __tablename__ = "vulnerability_scans"

    repo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    commit_sha: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # pending, running, completed, failed
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    summary: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    triggered_by: Mapped[str | None] = mapped_column(String(50), nullable=True)  # schedule, push, manual, pr

    # Relationships
    vulnerabilities: Mapped[list["Vulnerability"]] = relationship(
        "Vulnerability", back_populates="scan", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<VulnerabilityScan(id={self.id}, repo_id={self.repo_id}, status={self.status})>"


class Vulnerability(Base):
    """Individual vulnerability found in a repository."""

    __tablename__ = "vulnerabilities"

    scan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vulnerability_scans.id", ondelete="CASCADE"), nullable=False
    )
    repo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    cve_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    package_name: Mapped[str] = mapped_column(String(255), nullable=False)
    package_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)  # critical, high, medium, low
    cvss_score: Mapped[Decimal | None] = mapped_column(Numeric(3, 1), nullable=True)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    fix_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_exploitable: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    exploit_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="open", nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    fixed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ignored_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    ignored_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    scan: Mapped["VulnerabilityScan"] = relationship("VulnerabilityScan", back_populates="vulnerabilities")

    def __repr__(self) -> str:
        return f"<Vulnerability(id={self.id}, cve={self.cve_id}, severity={self.severity})>"
```

**Step 4: Update models __init__.py**

Modify `src/db/models/__init__.py`:
```python
"""Database models for DevMind AI."""

from src.db.models.organization import Organization
from src.db.models.repository import Repository
from src.db.models.security import Vulnerability, VulnerabilityScan
from src.db.models.user import OrgMember, User

__all__ = [
    "Organization",
    "OrgMember",
    "Repository",
    "User",
    "Vulnerability",
    "VulnerabilityScan",
]
```

**Step 5: Run test to verify it passes**

```bash
pytest tests/db/test_security_models.py -v
```
Expected: PASS (2 tests)

**Step 6: Commit**

```bash
git add src/db/models/ tests/db/
git commit -m "feat: add security models for vulnerability scans and vulnerabilities"
```

---

## Task 5: Alembic Migrations Setup

**Files:**
- Create: `alembic.ini`
- Create: `src/db/migrations/env.py`
- Create: `src/db/migrations/script.py.mako`
- Create: `src/db/migrations/versions/.gitkeep`

**Step 1: Create alembic.ini**

```ini
[alembic]
script_location = src/db/migrations
prepend_sys_path = .
version_path_separator = os

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

**Step 2: Create migrations directory structure**

```bash
mkdir -p src/db/migrations/versions
touch src/db/migrations/versions/.gitkeep
```

**Step 3: Create env.py**

Create `src/db/migrations/env.py`:
```python
"""Alembic migration environment configuration."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from src.core.config import settings
from src.db.base import Base

# Import all models to register them with Base.metadata
from src.db.models import (  # noqa: F401
    Organization,
    OrgMember,
    Repository,
    User,
    Vulnerability,
    VulnerabilityScan,
)

# Alembic Config object
config = context.config

# Set up logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Model metadata for autogenerate
target_metadata = Base.metadata


def get_url() -> str:
    """Get database URL from settings."""
    return settings.DATABASE_URL


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**Step 4: Create script.py.mako**

Create `src/db/migrations/script.py.mako`:
```mako
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
```

**Step 5: Commit**

```bash
git add alembic.ini src/db/migrations/
git commit -m "chore: add Alembic migrations configuration"
```

---

## Task 6: FastAPI Application Setup

**Files:**
- Create: `src/api/__init__.py`
- Create: `src/api/main.py`
- Create: `src/api/deps.py`
- Test: `tests/api/__init__.py`
- Test: `tests/api/test_main.py`

**Step 1: Write failing test**

Create `tests/api/__init__.py`:
```python
"""Tests for API module."""
```

Create `tests/api/test_main.py`:
```python
"""Tests for main FastAPI application."""

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


class TestHealthEndpoints:
    """Test suite for health check endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Health endpoint should return OK status."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    @pytest.mark.asyncio
    async def test_ready_check(self, client: AsyncClient):
        """Ready endpoint should return readiness status."""
        response = await client.get("/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"


class TestAPIInfo:
    """Test suite for API information endpoints."""

    @pytest.mark.asyncio
    async def test_root_redirects_to_docs(self, client: AsyncClient):
        """Root should redirect to API documentation."""
        response = await client.get("/", follow_redirects=False)

        assert response.status_code == 307
        assert response.headers["location"] == "/docs"

    @pytest.mark.asyncio
    async def test_openapi_schema_available(self, client: AsyncClient):
        """OpenAPI schema should be available."""
        response = await client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()
        assert data["info"]["title"] == "DevMind AI"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/api/test_main.py -v
```
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write the implementation**

Create `src/api/__init__.py`:
```python
"""API module for DevMind AI."""
```

Create `src/api/deps.py`:
```python
"""FastAPI dependencies."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import async_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# Type alias for dependency injection
DbSession = Annotated[AsyncSession, Depends(get_db)]
```

Create `src/api/main.py`:
```python
"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from src.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print(f"Starting {settings.APP_NAME}...")
    yield
    # Shutdown
    print(f"Shutting down {settings.APP_NAME}...")


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered developer platform with 10 intelligent agents",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    """Redirect root to API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "app": settings.APP_NAME,
    }


@app.get("/ready", tags=["Health"])
async def ready_check() -> dict[str, Any]:
    """Readiness check endpoint."""
    # TODO: Add database and Redis connectivity checks
    return {
        "status": "ready",
        "database": "connected",
        "redis": "connected",
    }
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/api/test_main.py -v
```
Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add src/api/ tests/api/
git commit -m "feat: add FastAPI application with health endpoints"
```

---

## Task 7: Pydantic Schemas

**Files:**
- Create: `src/api/schemas/__init__.py`
- Create: `src/api/schemas/organization.py`
- Create: `src/api/schemas/repository.py`
- Create: `src/api/schemas/security.py`
- Test: `tests/api/test_schemas.py`

**Step 1: Write failing test**

Create `tests/api/test_schemas.py`:
```python
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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/api/test_schemas.py -v
```
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write the implementation**

Create `src/api/schemas/__init__.py`:
```python
"""Pydantic schemas for API request/response validation."""

from src.api.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
)
from src.api.schemas.repository import (
    RepositoryConfig,
    RepositoryConnect,
    RepositoryResponse,
)
from src.api.schemas.security import (
    ScanRequest,
    ScanResponse,
    VulnerabilityResponse,
    VulnerabilitySummary,
    VulnerabilityUpdate,
)

__all__ = [
    "OrganizationCreate",
    "OrganizationResponse",
    "OrganizationUpdate",
    "RepositoryConfig",
    "RepositoryConnect",
    "RepositoryResponse",
    "ScanRequest",
    "ScanResponse",
    "VulnerabilityResponse",
    "VulnerabilitySummary",
    "VulnerabilityUpdate",
]
```

Create `src/api/schemas/organization.py`:
```python
"""Organization schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrganizationBase(BaseModel):
    """Base organization schema."""

    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")


class OrganizationCreate(OrganizationBase):
    """Schema for creating an organization."""

    github_org_id: int | None = None


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization."""

    name: str | None = Field(None, min_length=1, max_length=255)
    settings: dict | None = None


class OrganizationResponse(OrganizationBase):
    """Schema for organization response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    github_org_id: int | None = None
    plan: str
    settings: dict
    created_at: datetime
    updated_at: datetime
```

Create `src/api/schemas/repository.py`:
```python
"""Repository schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RepositoryConnect(BaseModel):
    """Schema for connecting a repository."""

    github_repo_id: int
    name: str = Field(..., min_length=1, max_length=255)
    full_name: str = Field(..., min_length=1, max_length=500)
    default_branch: str = "main"
    language: str | None = None


class RepositoryConfig(BaseModel):
    """Schema for repository configuration."""

    auto_review: bool = True
    auto_scan: bool = True
    scan_schedule: str = "0 2 * * *"  # Daily at 2 AM
    review_rules: dict = Field(default_factory=dict)
    ignored_paths: list[str] = Field(default_factory=list)


class RepositoryResponse(BaseModel):
    """Schema for repository response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    org_id: uuid.UUID
    github_repo_id: int
    name: str
    full_name: str
    default_branch: str
    language: str | None
    is_active: bool
    config: dict = Field(default_factory=dict)
    last_scan_at: datetime | None = None
    health_score: int | None = None
    created_at: datetime
    updated_at: datetime
```

Create `src/api/schemas/security.py`:
```python
"""Security-related schemas."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class VulnerabilitySummary(BaseModel):
    """Summary of vulnerabilities by severity."""

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    total: int = 0
    exploitable: int = 0


class ScanRequest(BaseModel):
    """Schema for triggering a vulnerability scan."""

    commit_sha: str | None = None
    full_scan: bool = False


class ScanResponse(BaseModel):
    """Schema for scan response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    repo_id: uuid.UUID
    commit_sha: str
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    summary: VulnerabilitySummary | None = None
    triggered_by: str | None = None


class VulnerabilityResponse(BaseModel):
    """Schema for vulnerability response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    scan_id: uuid.UUID
    repo_id: uuid.UUID
    cve_id: str | None = None
    package_name: str
    package_version: str | None = None
    severity: Literal["critical", "high", "medium", "low"]
    cvss_score: float | None = None
    title: str | None = None
    description: str | None = None
    fix_version: str | None = None
    is_exploitable: bool | None = None
    exploit_path: str | None = None
    status: str
    first_seen_at: datetime
    fixed_at: datetime | None = None
    ignored_reason: str | None = None
    created_at: datetime
    updated_at: datetime


class VulnerabilityUpdate(BaseModel):
    """Schema for updating vulnerability status."""

    status: Literal["open", "fixed", "ignored", "false_positive"]
    ignored_reason: str | None = Field(None, max_length=500)
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/api/test_schemas.py -v
```
Expected: PASS (5 tests)

**Step 5: Commit**

```bash
git add src/api/schemas/ tests/api/
git commit -m "feat: add Pydantic schemas for API validation"
```

---

## Task 8: Docker Compose for Local Development

**Files:**
- Create: `docker-compose.yml`
- Create: `Dockerfile`
- Create: `scripts/start.sh`

**Step 1: Create docker-compose.yml**

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: devmind-postgres
    environment:
      POSTGRES_USER: devmind
      POSTGRES_PASSWORD: devmind
      POSTGRES_DB: devmind
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U devmind"]
      interval: 5s
      timeout: 5s
      retries: 5

  # Redis
  redis:
    image: redis:7-alpine
    container_name: devmind-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  # Qdrant Vector Database
  qdrant:
    image: qdrant/qdrant:latest
    container_name: devmind-qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      QDRANT__SERVICE__GRPC_PORT: 6334

  # API Server (development)
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: devmind-api
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - DATABASE_URL=postgresql+asyncpg://devmind:devmind@postgres:5432/devmind
      - REDIS_URL=redis://redis:6379/0
      - QDRANT_URL=http://qdrant:6333
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - SECRET_KEY=${SECRET_KEY:-development-secret-key-change-in-production}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      qdrant:
        condition: service_started
    command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

  # Celery Worker
  worker:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: devmind-worker
    volumes:
      - .:/app
    environment:
      - DATABASE_URL=postgresql+asyncpg://devmind:devmind@postgres:5432/devmind
      - REDIS_URL=redis://redis:6379/0
      - QDRANT_URL=http://qdrant:6333
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - SECRET_KEY=${SECRET_KEY:-development-secret-key-change-in-production}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: celery -A src.core.celery_app worker --loglevel=info
    profiles:
      - full

volumes:
  postgres_data:
  redis_data:
  qdrant_data:
```

**Step 2: Create Dockerfile**

```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install -e ".[dev]"

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Step 3: Create start script**

Create `scripts/start.sh`:
```bash
#!/bin/bash
set -e

echo "🚀 Starting DevMind AI development environment..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your API keys before continuing."
    exit 1
fi

# Start infrastructure services
echo "🐳 Starting Docker services..."
docker-compose up -d postgres redis qdrant

# Wait for services to be ready
echo "⏳ Waiting for services to be healthy..."
sleep 5

# Run migrations
echo "📊 Running database migrations..."
alembic upgrade head

# Start the API server
echo "🌐 Starting API server..."
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Make it executable:
```bash
chmod +x scripts/start.sh
```

**Step 4: Commit**

```bash
git add docker-compose.yml Dockerfile scripts/
git commit -m "chore: add Docker Compose configuration for local development"
```

---

## Task 9: LLM Client Abstraction

**Files:**
- Create: `src/core/llm/__init__.py`
- Create: `src/core/llm/base.py`
- Create: `src/core/llm/claude.py`
- Create: `src/core/llm/gemini.py`
- Create: `src/core/llm/router.py`
- Test: `tests/core/test_llm.py`

**Step 1: Write failing test**

Create `tests/core/test_llm.py`:
```python
"""Tests for LLM client abstraction."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestLLMRouter:
    """Test suite for LLM router."""

    def test_router_selects_claude_for_complex_tasks(self):
        """Router should select Claude for complex reasoning tasks."""
        from src.core.llm.router import LLMRouter, TaskComplexity

        router = LLMRouter()

        client = router.get_client(TaskComplexity.COMPLEX)
        assert client.__class__.__name__ == "ClaudeClient"

    def test_router_selects_gemini_for_simple_tasks(self):
        """Router should select Gemini for simple/fast tasks."""
        from src.core.llm.router import LLMRouter, TaskComplexity

        router = LLMRouter()

        client = router.get_client(TaskComplexity.SIMPLE)
        assert client.__class__.__name__ == "GeminiClient"


class TestClaudeClient:
    """Test suite for Claude client."""

    @pytest.mark.asyncio
    async def test_claude_client_generates_response(self):
        """Claude client should generate responses."""
        from src.core.llm.claude import ClaudeClient

        with patch("src.core.llm.claude.anthropic.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client

            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="Test response")]
            mock_client.messages.create = AsyncMock(return_value=mock_response)

            client = ClaudeClient()
            response = await client.generate("Test prompt")

            assert response == "Test response"
            mock_client.messages.create.assert_called_once()


class TestGeminiClient:
    """Test suite for Gemini client."""

    @pytest.mark.asyncio
    async def test_gemini_client_generates_response(self):
        """Gemini client should generate responses."""
        from src.core.llm.gemini import GeminiClient

        with patch("src.core.llm.gemini.genai") as mock_genai:
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model

            mock_response = MagicMock()
            mock_response.text = "Test response"
            mock_model.generate_content_async = AsyncMock(return_value=mock_response)

            client = GeminiClient()
            response = await client.generate("Test prompt")

            assert response == "Test response"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/core/test_llm.py -v
```
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write the implementation**

Create `src/core/llm/__init__.py`:
```python
"""LLM client abstraction layer."""

from src.core.llm.base import BaseLLMClient
from src.core.llm.claude import ClaudeClient
from src.core.llm.gemini import GeminiClient
from src.core.llm.router import LLMRouter, TaskComplexity

__all__ = [
    "BaseLLMClient",
    "ClaudeClient",
    "GeminiClient",
    "LLMRouter",
    "TaskComplexity",
]
```

Create `src/core/llm/base.py`:
```python
"""Base LLM client interface."""

from abc import ABC, abstractmethod
from typing import Any


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """Generate a response from the LLM.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            **kwargs: Additional provider-specific arguments

        Returns:
            Generated text response
        """
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: dict[str, Any],
        *,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a structured response matching a schema.

        Args:
            prompt: The user prompt
            schema: JSON schema for the response
            system_prompt: Optional system prompt
            **kwargs: Additional provider-specific arguments

        Returns:
            Structured response matching the schema
        """
        pass
```

Create `src/core/llm/claude.py`:
```python
"""Claude (Anthropic) LLM client."""

import json
from typing import Any

import anthropic

from src.core.config import settings
from src.core.llm.base import BaseLLMClient


class ClaudeClient(BaseLLMClient):
    """Client for Anthropic Claude API."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        """Initialize Claude client.

        Args:
            model: Claude model to use
        """
        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = model

    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """Generate a response using Claude."""
        messages = [{"role": "user", "content": prompt}]

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "You are a helpful AI assistant.",
            messages=messages,
            **kwargs,
        )

        return response.content[0].text

    async def generate_structured(
        self,
        prompt: str,
        schema: dict[str, Any],
        *,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a structured response using Claude."""
        schema_str = json.dumps(schema, indent=2)
        structured_prompt = f"""{prompt}

Respond with valid JSON matching this schema:
{schema_str}

JSON response:"""

        system = system_prompt or "You are a helpful AI assistant that responds only with valid JSON."

        response = await self.generate(
            structured_prompt,
            system_prompt=system,
            **kwargs,
        )

        # Parse JSON from response
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(response[start:end])
            raise
```

Create `src/core/llm/gemini.py`:
```python
"""Google Gemini LLM client."""

import json
from typing import Any

import google.generativeai as genai

from src.core.config import settings
from src.core.llm.base import BaseLLMClient


class GeminiClient(BaseLLMClient):
    """Client for Google Gemini API."""

    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize Gemini client.

        Args:
            model: Gemini model to use
        """
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(model)

    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """Generate a response using Gemini."""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )

        response = await self.model.generate_content_async(
            full_prompt,
            generation_config=generation_config,
        )

        return response.text

    async def generate_structured(
        self,
        prompt: str,
        schema: dict[str, Any],
        *,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a structured response using Gemini."""
        schema_str = json.dumps(schema, indent=2)
        structured_prompt = f"""{prompt}

Respond with valid JSON matching this schema:
{schema_str}

JSON response:"""

        system = system_prompt or "You are a helpful AI assistant that responds only with valid JSON."

        response = await self.generate(
            structured_prompt,
            system_prompt=system,
            **kwargs,
        )

        # Parse JSON from response
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(response[start:end])
            raise
```

Create `src/core/llm/router.py`:
```python
"""LLM router for selecting appropriate model based on task complexity."""

from enum import Enum
from functools import lru_cache

from src.core.llm.base import BaseLLMClient
from src.core.llm.claude import ClaudeClient
from src.core.llm.gemini import GeminiClient


class TaskComplexity(str, Enum):
    """Task complexity levels for routing decisions."""

    SIMPLE = "simple"  # Fast, straightforward tasks
    MODERATE = "moderate"  # Medium complexity
    COMPLEX = "complex"  # Complex reasoning, code review, migrations


class LLMRouter:
    """Routes requests to appropriate LLM based on task requirements."""

    def __init__(self):
        """Initialize router with client instances."""
        self._claude: ClaudeClient | None = None
        self._gemini: GeminiClient | None = None

    @property
    def claude(self) -> ClaudeClient:
        """Lazy-loaded Claude client."""
        if self._claude is None:
            self._claude = ClaudeClient()
        return self._claude

    @property
    def gemini(self) -> GeminiClient:
        """Lazy-loaded Gemini client."""
        if self._gemini is None:
            self._gemini = GeminiClient()
        return self._gemini

    def get_client(self, complexity: TaskComplexity) -> BaseLLMClient:
        """Get appropriate LLM client for task complexity.

        Args:
            complexity: Task complexity level

        Returns:
            LLM client appropriate for the task
        """
        if complexity == TaskComplexity.COMPLEX:
            return self.claude
        elif complexity == TaskComplexity.MODERATE:
            # Use Claude for moderate tasks too (better quality)
            return self.claude
        else:
            # Use Gemini for simple/fast tasks
            return self.gemini

    def get_client_for_agent(self, agent_type: str) -> BaseLLMClient:
        """Get appropriate LLM client for a specific agent type.

        Args:
            agent_type: Type of agent (e.g., 'vuln_scanner', 'code_reviewer')

        Returns:
            LLM client appropriate for the agent
        """
        # Map agent types to complexity
        agent_complexity = {
            # Complex tasks - use Claude
            "code_reviewer": TaskComplexity.COMPLEX,
            "code_migrator": TaskComplexity.COMPLEX,
            "incident_responder": TaskComplexity.COMPLEX,
            "query_optimizer": TaskComplexity.COMPLEX,
            "adr_recorder": TaskComplexity.COMPLEX,
            # Simple/fast tasks - use Gemini
            "vuln_scanner": TaskComplexity.SIMPLE,
            "test_generator": TaskComplexity.MODERATE,
            "debt_analyzer": TaskComplexity.SIMPLE,
            "doc_generator": TaskComplexity.SIMPLE,
            "pipeline_generator": TaskComplexity.MODERATE,
        }

        complexity = agent_complexity.get(agent_type, TaskComplexity.MODERATE)
        return self.get_client(complexity)


@lru_cache
def get_llm_router() -> LLMRouter:
    """Get cached LLM router instance."""
    return LLMRouter()
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/core/test_llm.py -v
```
Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add src/core/llm/ tests/core/
git commit -m "feat: add LLM client abstraction with Claude and Gemini support"
```

---

## Task 10: Base Agent Framework

**Files:**
- Create: `src/agents/__init__.py`
- Create: `src/agents/base.py`
- Test: `tests/agents/__init__.py`
- Test: `tests/agents/test_base.py`

**Step 1: Write failing test**

Create `tests/agents/__init__.py`:
```python
"""Tests for agents module."""
```

Create `tests/agents/test_base.py`:
```python
"""Tests for base agent framework."""

from unittest.mock import AsyncMock, patch

import pytest


class TestBaseAgent:
    """Test suite for BaseAgent."""

    def test_agent_has_required_attributes(self):
        """Agent should have name, description, and llm_client."""
        from src.agents.base import BaseAgent
        from src.core.llm import TaskComplexity

        class TestAgent(BaseAgent):
            name = "test_agent"
            description = "A test agent"
            complexity = TaskComplexity.SIMPLE

            async def execute(self, **kwargs):
                return {"result": "success"}

        agent = TestAgent()

        assert agent.name == "test_agent"
        assert agent.description == "A test agent"
        assert agent.llm_client is not None

    @pytest.mark.asyncio
    async def test_agent_execute_returns_result(self):
        """Agent execute should return a result."""
        from src.agents.base import BaseAgent
        from src.core.llm import TaskComplexity

        class TestAgent(BaseAgent):
            name = "test_agent"
            description = "A test agent"
            complexity = TaskComplexity.SIMPLE

            async def execute(self, **kwargs):
                return {"status": "completed", "data": kwargs.get("input")}

        agent = TestAgent()
        result = await agent.execute(input="test_data")

        assert result["status"] == "completed"
        assert result["data"] == "test_data"

    @pytest.mark.asyncio
    async def test_agent_run_with_context(self):
        """Agent run should execute with context."""
        from src.agents.base import AgentContext, BaseAgent
        from src.core.llm import TaskComplexity

        class TestAgent(BaseAgent):
            name = "test_agent"
            description = "A test agent"
            complexity = TaskComplexity.SIMPLE

            async def execute(self, context: AgentContext, **kwargs):
                return {
                    "repo": context.repository_id,
                    "org": context.organization_id,
                }

        agent = TestAgent()
        context = AgentContext(
            organization_id="org-123",
            repository_id="repo-456",
        )

        result = await agent.run(context)

        assert result["repo"] == "repo-456"
        assert result["org"] == "org-123"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/agents/test_base.py -v
```
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write the implementation**

Create `src/agents/__init__.py`:
```python
"""AI agents for DevMind."""

from src.agents.base import AgentContext, AgentResult, BaseAgent

__all__ = [
    "AgentContext",
    "AgentResult",
    "BaseAgent",
]
```

Create `src/agents/base.py`:
```python
"""Base agent framework for DevMind AI."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from src.core.llm import BaseLLMClient, LLMRouter, TaskComplexity, get_llm_router

T = TypeVar("T")


@dataclass
class AgentContext:
    """Context passed to agents during execution."""

    organization_id: str | None = None
    repository_id: str | None = None
    user_id: str | None = None
    commit_sha: str | None = None
    pr_number: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Add timestamp to context."""
        self.timestamp = datetime.now(timezone.utc)


@dataclass
class AgentResult(Generic[T]):
    """Result returned by agent execution."""

    success: bool
    data: T | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def ok(cls, data: T, **metadata: Any) -> "AgentResult[T]":
        """Create a successful result."""
        return cls(success=True, data=data, metadata=metadata)

    @classmethod
    def fail(cls, error: str, **metadata: Any) -> "AgentResult[T]":
        """Create a failed result."""
        return cls(success=False, error=error, metadata=metadata)


class BaseAgent(ABC):
    """Abstract base class for all DevMind agents."""

    # Override in subclasses
    name: str = "base_agent"
    description: str = "Base agent"
    complexity: TaskComplexity = TaskComplexity.MODERATE

    def __init__(self, router: LLMRouter | None = None):
        """Initialize agent with LLM router.

        Args:
            router: LLM router instance (uses global if not provided)
        """
        self._router = router or get_llm_router()

    @property
    def llm_client(self) -> BaseLLMClient:
        """Get the appropriate LLM client for this agent."""
        return self._router.get_client(self.complexity)

    @abstractmethod
    async def execute(self, context: AgentContext, **kwargs: Any) -> dict[str, Any]:
        """Execute the agent's main logic.

        Args:
            context: Execution context
            **kwargs: Additional arguments

        Returns:
            Result dictionary
        """
        pass

    async def run(self, context: AgentContext, **kwargs: Any) -> dict[str, Any]:
        """Run the agent with error handling and logging.

        Args:
            context: Execution context
            **kwargs: Additional arguments

        Returns:
            Execution result
        """
        try:
            result = await self.execute(context, **kwargs)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent": self.name,
            }

    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate a response using the agent's LLM client.

        Args:
            prompt: The prompt to send
            system_prompt: Optional system prompt
            **kwargs: Additional arguments

        Returns:
            Generated text
        """
        return await self.llm_client.generate(
            prompt,
            system_prompt=system_prompt,
            **kwargs,
        )

    async def generate_structured(
        self,
        prompt: str,
        schema: dict[str, Any],
        *,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a structured response using the agent's LLM client.

        Args:
            prompt: The prompt to send
            schema: JSON schema for the response
            system_prompt: Optional system prompt
            **kwargs: Additional arguments

        Returns:
            Structured response
        """
        return await self.llm_client.generate_structured(
            prompt,
            schema,
            system_prompt=system_prompt,
            **kwargs,
        )
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/agents/test_base.py -v
```
Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add src/agents/ tests/agents/
git commit -m "feat: add base agent framework with LLM integration"
```

---

## Summary

This completes **Phase 1 Foundation** with:

1. ✅ Project configuration (pyproject.toml, .env, Docker)
2. ✅ Core configuration module
3. ✅ Database models (Organizations, Users, Repositories, Security)
4. ✅ Alembic migrations setup
5. ✅ FastAPI application with health endpoints
6. ✅ Pydantic schemas for API validation
7. ✅ Docker Compose for local development
8. ✅ LLM client abstraction (Claude + Gemini)
9. ✅ Base agent framework

**Next Phase:** Phase 2 will implement the first agent (VulnScanner) with full functionality.

---

## Next Steps

After completing Phase 1:

1. Run all tests: `pytest -v`
2. Start services: `docker-compose up -d postgres redis qdrant`
3. Run migrations: `alembic upgrade head`
4. Start API: `uvicorn src.api.main:app --reload`
5. Verify at: http://localhost:8000/docs

Then proceed to Phase 2: VulnScanner Agent Implementation.
