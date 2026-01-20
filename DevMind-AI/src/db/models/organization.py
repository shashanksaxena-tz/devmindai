"""Organization model."""

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, JSON, String
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
    settings: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Relationships
    repositories: Mapped[list["Repository"]] = relationship(
        "Repository", back_populates="organization", cascade="all, delete-orphan"
    )
    members: Mapped[list["OrgMember"]] = relationship(
        "OrgMember", back_populates="organization", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name={self.name}, slug={self.slug})>"
