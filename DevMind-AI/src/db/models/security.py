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
    JSON,
    Numeric,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.db.models.repository import Repository
    from src.db.models.user import User


class VulnerabilityScan(Base):
    """Record of a vulnerability scan run."""

    __tablename__ = "vulnerability_scans"

    repo_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    commit_sha: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # pending, running, completed, failed
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
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
        Uuid(as_uuid=True), ForeignKey("vulnerability_scans.id", ondelete="CASCADE"), nullable=False
    )
    repo_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
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
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    ignored_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    scan: Mapped["VulnerabilityScan"] = relationship("VulnerabilityScan", back_populates="vulnerabilities")

    def __repr__(self) -> str:
        return f"<Vulnerability(id={self.id}, cve={self.cve_id}, severity={self.severity})>"
