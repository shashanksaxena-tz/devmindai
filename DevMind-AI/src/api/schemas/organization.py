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
