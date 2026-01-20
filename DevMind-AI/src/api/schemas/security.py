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
