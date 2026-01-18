"""Security API routes for vulnerability scanning."""

import uuid
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query

from src.api.schemas.security import (
    ScanRequest,
    ScanResponse,
    VulnerabilityResponse,
    VulnerabilitySummary,
    VulnerabilityUpdate,
)

router = APIRouter()


# Placeholder functions - will be replaced with actual database operations
async def trigger_vulnerability_scan(
    repo_id: str,
    request: ScanRequest,
    background_tasks: BackgroundTasks,
) -> dict:
    """Trigger a vulnerability scan (placeholder)."""
    scan_id = str(uuid.uuid4())
    return {
        "id": scan_id,
        "repo_id": repo_id,
        "commit_sha": request.commit_sha or "HEAD",
        "status": "pending",
        "started_at": "2024-01-01T00:00:00Z", # Mock date
        "triggered_by": "manual",
    }


async def get_vulnerabilities(
    repo_id: str,
    severity: str | None = None,
    status: str | None = None,
    exploitable_only: bool = False,
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    """Get vulnerabilities for a repository (placeholder)."""
    return []


async def update_vulnerability(
    vuln_id: str,
    update: VulnerabilityUpdate,
) -> dict:
    """Update a vulnerability (placeholder)."""
    return {
        "id": vuln_id,
        "status": update.status,
    }


@router.post("/{repo_id}/scan", response_model=ScanResponse, status_code=202)
async def create_scan(
    repo_id: str,
    request: ScanRequest,
    background_tasks: BackgroundTasks,
):
    """Trigger a vulnerability scan for a repository.

    The scan runs asynchronously. Poll the returned scan_id
    to check status and get results.

    Args:
        repo_id: Repository UUID
        request: Scan configuration
        background_tasks: FastAPI background tasks

    Returns:
        Scan metadata with ID for tracking
    """
    result = await trigger_vulnerability_scan(repo_id, request, background_tasks)
    return ScanResponse(**result)


@router.get("/{repo_id}/vulns", response_model=list[VulnerabilityResponse])
async def list_vulnerabilities(
    repo_id: str,
    severity: Literal["critical", "high", "medium", "low"] | None = None,
    status: Literal["open", "fixed", "ignored", "false_positive"] | None = Query(
        default="open"
    ),
    exploitable_only: bool = False,
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0, ge=0),
):
    """List vulnerabilities for a repository.

    Args:
        repo_id: Repository UUID
        severity: Filter by severity level
        status: Filter by status (default: open)
        exploitable_only: Only return exploitable vulnerabilities
        limit: Maximum results to return
        offset: Pagination offset

    Returns:
        List of vulnerabilities matching filters
    """
    vulns = await get_vulnerabilities(
        repo_id=repo_id,
        severity=severity,
        status=status,
        exploitable_only=exploitable_only,
        limit=limit,
        offset=offset,
    )
    return vulns


@router.get("/{repo_id}/summary", response_model=VulnerabilitySummary)
async def get_vulnerability_summary(repo_id: str):
    """Get vulnerability summary for a repository.

    Args:
        repo_id: Repository UUID

    Returns:
        Summary counts by severity
    """
    # Placeholder - will query database
    return VulnerabilitySummary(
        critical=0,
        high=0,
        medium=0,
        low=0,
        total=0,
        exploitable=0,
    )


@router.patch("/vulns/{vuln_id}", response_model=VulnerabilityResponse)
async def update_vulnerability_status(
    vuln_id: str,
    update: VulnerabilityUpdate,
):
    """Update vulnerability status.

    Use this to mark vulnerabilities as ignored or false positive.
    Requires a reason when ignoring.

    Args:
        vuln_id: Vulnerability UUID
        update: Status update data

    Returns:
        Updated vulnerability
    """
    if update.status in ["ignored", "false_positive"] and not update.ignored_reason:
        raise HTTPException(
            status_code=400,
            detail="Reason required when ignoring vulnerability",
        )

    result = await update_vulnerability(vuln_id, update)
    return result
