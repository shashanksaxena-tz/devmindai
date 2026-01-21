# src/api/routes/reviews.py
"""Code review API endpoints."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, func

from src.core.auth import get_current_user
from src.core.config import get_settings
from src.agents.code_reviewer.orchestrator import ReviewOrchestrator
from src.agents.code_reviewer.synthesizer import ReviewSynthesizer
from src.agents.code_reviewer.context_gatherer import ContextGatherer
from src.agents.code_reviewer.diff_parser import DiffParser
from src.db.models import PRReview, Repository
from src.db.session import async_session
from src.integrations.github import get_github_client
from src.core.llm import get_claude_client, get_gemini_client

router = APIRouter(tags=["reviews"])


# Request/Response Models
class TriggerReviewRequest(BaseModel):
    """Request to trigger a PR review."""
    pr_number: int = Field(..., description="Pull request number")
    reviewers: Optional[list[str]] = Field(
        default=None,
        description="Specific reviewers to run (all if not specified)",
    )


class TriggerReviewResponse(BaseModel):
    """Response for triggered review."""
    job_id: str
    status: str = "queued"
    pr_number: int
    message: str


class ReviewFileRequest(BaseModel):
    """Request for manual file review."""
    file_path: str
    content: str
    diff: Optional[str] = None
    language: Optional[str] = None


class ReviewConfigRequest(BaseModel):
    """Request to configure review settings."""
    enabled_reviewers: Optional[list[str]] = None
    auto_review: Optional[bool] = None
    severity_threshold: Optional[str] = None


class ReviewComment(BaseModel):
    """A single review comment."""
    file_path: str
    line_number: int
    severity: str
    category: str
    title: str
    message: str
    suggestion: Optional[str] = None


class ReviewSummary(BaseModel):
    """Summary of a review."""
    id: str
    pr_number: int
    status: str
    blocker_count: int
    warning_count: int
    suggestion_count: int
    created_at: datetime
    comments: list[ReviewComment] = []


class ReviewListResponse(BaseModel):
    """List of reviews."""
    reviews: list[ReviewSummary]
    total: int
    page: int
    page_size: int


class ReviewStatsResponse(BaseModel):
    """Review statistics."""
    total_reviews: int
    average_blockers: float
    average_warnings: float
    most_common_issues: list[dict[str, Any]]
    review_trend: list[dict[str, Any]]


# In-memory job storage (replace with Redis/DB in production)
_review_jobs: dict[str, dict[str, Any]] = {}


# Endpoints
@router.post(
    "/repos/{repo_id}/review",
    response_model=TriggerReviewResponse,
    status_code=202,
)
async def trigger_pr_review(
    repo_id: str,
    request: TriggerReviewRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
):
    """Trigger a code review for a pull request.

    This queues the review job and returns immediately.
    Use the job_id to check status.
    """
    job_id = str(uuid.uuid4())

    _review_jobs[job_id] = {
        "status": "queued",
        "repo_id": repo_id,
        "pr_number": request.pr_number,
        "created_at": datetime.now(timezone.utc),
        "user_id": user.get("id"),
    }

    # Queue the actual review work
    background_tasks.add_task(
        _execute_pr_review,
        job_id=job_id,
        repo_id=repo_id,
        pr_number=request.pr_number,
        reviewers=request.reviewers,
    )

    return TriggerReviewResponse(
        job_id=job_id,
        status="queued",
        pr_number=request.pr_number,
        message=f"Review queued for PR #{request.pr_number}",
    )


async def _execute_pr_review(
    job_id: str,
    repo_id: str,
    pr_number: int,
    reviewers: Optional[list[str]] = None,
):
    """Execute the PR review in the background."""
    try:
        _review_jobs[job_id]["status"] = "running"

        async with async_session() as session:
             # Fetch repository
             stmt = select(Repository).where(str(Repository.id) == repo_id)
             try:
                 repo_uuid = uuid.UUID(repo_id)
                 stmt = select(Repository).where(Repository.id == repo_uuid)
             except ValueError:
                 stmt = select(Repository).where(Repository.full_name == repo_id)

             result = await session.execute(stmt)
             repo = result.scalar_one_or_none()

             if not repo:
                 raise ValueError(f"Repository {repo_id} not found")

             owner, repo_name = repo.full_name.split("/")

             # Initialize clients
             github_client = get_github_client()
             context_gatherer = ContextGatherer(github_client)

             orchestrator = ReviewOrchestrator(
                claude_client=get_claude_client(),
                gemini_client=get_gemini_client(),
                enabled_reviewers=reviewers,
             )

             # Gather Context
             pr_context = context_gatherer.gather_pr_context(owner, repo_name, pr_number)
             pr_files = github_client.get_pr_files(owner, repo_name, pr_number)

             # Iterate files and review
             file_reviews = []
             for file_info in pr_files:
                 filename = file_info["filename"]
                 status = file_info["status"]

                 if status == "removed":
                     continue

                 diff = file_info.get("patch", "")

                 file_context = context_gatherer.gather_file_context(
                     owner, repo_name, filename, pr_context.base_branch, pr_context.head_sha
                 )

                 full_content = file_context.content_after or ""

                 results = await orchestrator.review_file(
                     file_path=filename,
                     diff=diff,
                     full_content=full_content,
                     context={"pr": pr_context}
                 )
                 file_reviews.extend(results)

             # Synthesize
             synthesizer = ReviewSynthesizer(llm_client=get_gemini_client())
             summary = await synthesizer.synthesize(file_reviews)

             # Save to DB
             review = PRReview(
                 repo_id=repo.id,
                 pr_number=pr_number,
                 status="completed",
                 completed_at=datetime.now(timezone.utc),
                 results={
                     "summary": summary.summary,
                     "comments": [c.__dict__ for c in summary.comments],
                     "stats": {
                         "blockers": summary.blocker_count,
                         "warnings": summary.warning_count,
                         "suggestions": summary.suggestion_count
                     }
                 }
             )
             session.add(review)
             await session.commit()

        _review_jobs[job_id]["status"] = "completed"
        _review_jobs[job_id]["completed_at"] = datetime.now(timezone.utc)

    except Exception as e:
        import traceback
        traceback.print_exc()
        _review_jobs[job_id]["status"] = "failed"
        _review_jobs[job_id]["error"] = str(e)


@router.get("/jobs/{job_id}/status")
async def get_review_job_status(
    job_id: str,
    user: dict = Depends(get_current_user),
):
    """Get the status of a review job."""
    job = _review_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job_id,
        "status": job["status"],
        "pr_number": job.get("pr_number"),
        "created_at": job.get("created_at"),
        "completed_at": job.get("completed_at"),
        "error": job.get("error"),
    }


@router.get(
    "/repos/{repo_id}/reviews",
    response_model=ReviewListResponse,
)
async def list_pr_reviews(
    repo_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: dict = Depends(get_current_user),
):
    """List all reviews for a repository."""
    async with async_session() as session:
        # Check repo exists
        try:
            repo_uuid = uuid.UUID(repo_id)
            stmt = select(Repository).where(Repository.id == repo_uuid)
        except ValueError:
            stmt = select(Repository).where(Repository.full_name == repo_id)

        repo_result = await session.execute(stmt)
        repo = repo_result.scalar_one_or_none()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")

        # Get total count
        count_stmt = select(func.count()).select_from(PRReview).where(PRReview.repo_id == repo.id)
        total_result = await session.execute(count_stmt)
        total = total_result.scalar() or 0

        # Get page
        stmt = (
            select(PRReview)
            .where(PRReview.repo_id == repo.id)
            .order_by(PRReview.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await session.execute(stmt)
        reviews = result.scalars().all()

        review_summaries = []
        for r in reviews:
            results_data = r.results or {}
            stats = results_data.get("stats", {})
            review_summaries.append(ReviewSummary(
                id=str(r.id),
                pr_number=r.pr_number,
                status=r.status,
                blocker_count=stats.get("blockers", 0),
                warning_count=stats.get("warnings", 0),
                suggestion_count=stats.get("suggestions", 0),
                created_at=r.created_at,
                comments=[] # Don't load all comments for list view
            ))

        return ReviewListResponse(
            reviews=review_summaries,
            total=total,
            page=page,
            page_size=page_size,
        )


@router.get("/reviews/{review_id}")
async def get_review_details(
    review_id: str,
    user: dict = Depends(get_current_user),
):
    """Get details of a specific review."""
    async with async_session() as session:
        try:
            review_uuid = uuid.UUID(review_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid review ID format")

        stmt = select(PRReview).where(PRReview.id == review_uuid)
        result = await session.execute(stmt)
        review = result.scalar_one_or_none()

        if not review:
             raise HTTPException(status_code=404, detail="Review not found")

        results_data = review.results or {}
        stats = results_data.get("stats", {})
        comments_data = results_data.get("comments", [])

        # Parse comments back to objects
        comments = []
        for c in comments_data:
            comments.append(ReviewComment(
                file_path=c.get("file_path", ""),
                line_number=c.get("line_number", 0),
                severity=c.get("severity", {}).get("value", "suggestion") if isinstance(c.get("severity"), dict) else c.get("severity", "suggestion"),
                category=c.get("category", ""),
                title=c.get("title", ""),
                message=c.get("message", ""),
                suggestion=c.get("suggestion")
            ))

        return ReviewSummary(
            id=str(review.id),
            pr_number=review.pr_number,
            status=review.status,
            blocker_count=stats.get("blockers", 0),
            warning_count=stats.get("warnings", 0),
            suggestion_count=stats.get("suggestions", 0),
            created_at=review.created_at,
            comments=comments
        )


@router.post("/review-file", status_code=200)
async def review_file(
    request: ReviewFileRequest,
    user: dict = Depends(get_current_user),
):
    """Manually review a single file.

    Useful for IDE integration or testing.
    """
    settings = get_settings()

    # Create orchestrator
    orchestrator = ReviewOrchestrator(
        claude_client=get_claude_client(),
        gemini_client=get_gemini_client(),
    )

    # Generate diff if not provided
    diff = request.diff or f"+{request.content}"

    # Run review
    results = await orchestrator.review_file(
        file_path=request.file_path,
        diff=diff,
        full_content=request.content,
    )

    # Synthesize results
    synthesizer = ReviewSynthesizer(llm_client=get_gemini_client())
    summary = await synthesizer.synthesize(results)

    return {
        "file_path": request.file_path,
        "blocker_count": summary.blocker_count,
        "warning_count": summary.warning_count,
        "suggestion_count": summary.suggestion_count,
        "comments": [
            {
                "line_number": c.line_number,
                "severity": c.severity.value,
                "category": c.category,
                "title": c.title,
                "message": c.message,
                "suggestion": c.suggestion,
            }
            for c in summary.comments
        ],
    }


@router.patch("/repos/{repo_id}/config")
async def configure_reviewers(
    repo_id: str,
    request: ReviewConfigRequest,
    user: dict = Depends(get_current_user),
):
    """Configure review settings for a repository."""
    # TODO: Save to database
    return {
        "repo_id": repo_id,
        "config": request.model_dump(exclude_none=True),
        "updated_at": datetime.now(timezone.utc),
    }


@router.get(
    "/repos/{repo_id}/stats",
    response_model=ReviewStatsResponse,
)
async def get_review_stats(
    repo_id: str,
    days: int = Query(30, ge=1, le=365),
    user: dict = Depends(get_current_user),
):
    """Get review statistics for a repository."""
    # TODO: Aggregate from database
    return ReviewStatsResponse(
        total_reviews=0,
        average_blockers=0.0,
        average_warnings=0.0,
        most_common_issues=[],
        review_trend=[],
    )
