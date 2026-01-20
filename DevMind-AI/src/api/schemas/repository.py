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
