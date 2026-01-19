"""Security API routes for vulnerability scanning."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.api.schemas.security import (
    ScanRequest,
    ScanResponse,
    VulnerabilityResponse,
    VulnerabilitySummary,
    VulnerabilityUpdate,
)
from src.db.models.repository import Repository
from src.db.models.security import Vulnerability, VulnerabilityScan
from src.db.session import async_session
from src.agents.vuln_scanner import VulnScannerAgent
from src.agents.base import AgentContext

logger = logging.getLogger(__name__)

router = APIRouter()


async def run_scan_background(scan_id: uuid.UUID, repo_id: str, full_scan: bool = False):
    """Run vulnerability scan in background."""
    async with async_session() as session:
        try:
            # Get scan record
            scan = await session.get(VulnerabilityScan, scan_id)
            if not scan:
                logger.error(f"Scan {scan_id} not found")
                return

            # Update status to running
            scan.status = "running"
            await session.commit()

            # Get repository to find path/url
            repo = await session.get(Repository, uuid.UUID(repo_id))
            if not repo:
                scan.status = "failed"
                scan.summary = {"error": "Repository not found"}
                scan.completed_at = datetime.now(timezone.utc)
                await session.commit()
                return

            # In a real scenario, we would clone the repo here.
            # For now, we assume repo is available at a path, or we use a temporary directory if we had cloning logic.
            # Since we don't have cloning logic fully implemented in this phase, we'll try to use a local path if available
            # or fail gracefully/mock for now if no path is configured.

            # Note: In Phase 1 Foundation, Repository model has 'config' JSONB field.
            # We can check if 'local_path' is in config or assume standard checkout location.
            repo_path = repo.config.get("local_path")

            if not repo_path:
                 # Fallback for testing/demo purposes if no local path is set
                 # We might want to just skip actual scanning if no path is available
                 # But to allow testing, we might need a dummy path or similar.
                 pass

            # Initialize Agent
            agent = VulnScannerAgent()

            # Create Agent Context
            context = AgentContext(
                organization_id=str(repo.org_id),
                repository_id=str(repo.id),
                metadata={"repo_path": repo_path}
            )

            # Execute Scan
            try:
                result = await agent.execute(context, full_scan=full_scan)

                # Check for agent errors
                if result.get("error"):
                     scan.status = "failed"
                     scan.summary = {"error": result["error"]}
                     scan.completed_at = datetime.now(timezone.utc)
                     await session.commit()
                     return

                # Save Results
                scan.status = "completed"
                scan.completed_at = datetime.now(timezone.utc)
                scan.summary = {
                    "total_dependencies": result.get("total_dependencies", 0),
                    "vulnerabilities": result.get("vulnerabilities", {}),
                    "exploitable": result.get("exploitable", 0)
                }

                # Save individual vulnerabilities
                for detail in result.get("details", []):
                    vuln = Vulnerability(
                        scan_id=scan.id,
                        repo_id=repo.id,
                        cve_id=detail.get("vulnerability_id"),
                        package_name=detail.get("package"),
                        package_version=detail.get("version"),
                        severity=detail.get("severity", "unknown"),
                        cvss_score=detail.get("cvss_score"),
                        title=detail.get("title"),
                        fix_version=detail.get("fix_version"),
                        is_exploitable=detail.get("is_exploitable"),
                        status="open"
                    )
                    session.add(vuln)

                await session.commit()

            except Exception as e:
                logger.exception("Error running vulnerability scan")
                scan.status = "failed"
                scan.summary = {"error": str(e)}
                scan.completed_at = datetime.now(timezone.utc)
                await session.commit()
            finally:
                await agent.close()

        except Exception as e:
            logger.exception("Critical error in background scan task")


@router.post("/{repo_id}/scan", response_model=ScanResponse, status_code=202)
async def create_scan(
    repo_id: str,
    request: ScanRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Trigger a vulnerability scan for a repository.

    The scan runs asynchronously. Poll the returned scan_id
    to check status and get results.

    Args:
        repo_id: Repository UUID
        request: Scan configuration
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        Scan metadata with ID for tracking
    """
    # Verify repository exists
    try:
        repo_uuid = uuid.UUID(repo_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid repository ID")

    repo = await db.get(Repository, repo_uuid)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    # Create scan record
    scan = VulnerabilityScan(
        repo_id=repo_uuid,
        commit_sha=request.commit_sha or "HEAD",
        status="pending",
        triggered_by="manual",
    )
    db.add(scan)
    await db.commit()
    await db.refresh(scan)

    # Trigger background task
    background_tasks.add_task(
        run_scan_background,
        scan.id,
        repo_id,
        request.full_scan
    )

    return scan


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
    db: AsyncSession = Depends(get_db),
):
    """List vulnerabilities for a repository.

    Args:
        repo_id: Repository UUID
        severity: Filter by severity level
        status: Filter by status (default: open)
        exploitable_only: Only return exploitable vulnerabilities
        limit: Maximum results to return
        offset: Pagination offset
        db: Database session

    Returns:
        List of vulnerabilities matching filters
    """
    try:
        repo_uuid = uuid.UUID(repo_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid repository ID")

    query = select(Vulnerability).where(Vulnerability.repo_id == repo_uuid)

    if severity:
        query = query.where(Vulnerability.severity == severity)

    if status:
        query = query.where(Vulnerability.status == status)

    if exploitable_only:
        query = query.where(Vulnerability.is_exploitable == True)

    query = query.limit(limit).offset(offset).order_by(Vulnerability.first_seen_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{repo_id}/summary", response_model=VulnerabilitySummary)
async def get_vulnerability_summary(repo_id: str, db: AsyncSession = Depends(get_db)):
    """Get vulnerability summary for a repository.

    Args:
        repo_id: Repository UUID
        db: Database session

    Returns:
        Summary counts by severity
    """
    try:
        repo_uuid = uuid.UUID(repo_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid repository ID")

    # This is a basic implementation. For production, efficient aggregation queries should be used.
    query = select(Vulnerability).where(
        Vulnerability.repo_id == repo_uuid,
        Vulnerability.status == "open"
    )
    result = await db.execute(query)
    vulns = result.scalars().all()

    summary = VulnerabilitySummary()
    summary.total = len(vulns)

    for vuln in vulns:
        if vuln.is_exploitable:
            summary.exploitable += 1

        if vuln.severity == "critical":
            summary.critical += 1
        elif vuln.severity == "high":
            summary.high += 1
        elif vuln.severity == "medium":
            summary.medium += 1
        elif vuln.severity == "low":
            summary.low += 1

    return summary


@router.patch("/vulns/{vuln_id}", response_model=VulnerabilityResponse)
async def update_vulnerability_status(
    vuln_id: str,
    update_data: VulnerabilityUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update vulnerability status.

    Use this to mark vulnerabilities as ignored or false positive.
    Requires a reason when ignoring.

    Args:
        vuln_id: Vulnerability UUID
        update_data: Status update data
        db: Database session

    Returns:
        Updated vulnerability
    """
    if update_data.status in ["ignored", "false_positive"] and not update_data.ignored_reason:
        raise HTTPException(
            status_code=400,
            detail="Reason required when ignoring vulnerability",
        )

    try:
        vuln_uuid = uuid.UUID(vuln_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid vulnerability ID")

    vuln = await db.get(Vulnerability, vuln_uuid)
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")

    vuln.status = update_data.status
    if update_data.ignored_reason:
        vuln.ignored_reason = update_data.ignored_reason

    await db.commit()
    await db.refresh(vuln)
    return vuln
