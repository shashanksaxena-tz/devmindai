"""Celery application configuration and task definitions for DevMind AI."""

import asyncio
from typing import Any

from celery import Celery

from src.core.config import settings

# Create Celery app
celery_app = Celery(
    "devmind",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "src.core.celery_app",  # Include this module for task discovery
    ],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Task execution settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,

    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour

    # Task routing - different queues for different priorities
    task_routes={
        "src.core.celery_app.run_code_review": {"queue": "high_priority"},
        "src.core.celery_app.run_security_scan": {"queue": "high_priority"},
        "src.core.celery_app.run_incident_response": {"queue": "high_priority"},
        "src.core.celery_app.run_test_generation": {"queue": "default"},
        "src.core.celery_app.run_debt_analysis": {"queue": "default"},
        "src.core.celery_app.run_doc_generation": {"queue": "low_priority"},
        "src.core.celery_app.run_pipeline_generation": {"queue": "low_priority"},
        "src.core.celery_app.run_query_optimization": {"queue": "default"},
        "src.core.celery_app.run_code_migration": {"queue": "low_priority"},
        "src.core.celery_app.run_adr_capture": {"queue": "low_priority"},
    },

    # Queue configuration
    task_default_queue="default",
    task_queues={
        "high_priority": {"exchange": "high_priority", "routing_key": "high"},
        "default": {"exchange": "default", "routing_key": "default"},
        "low_priority": {"exchange": "low_priority", "routing_key": "low"},
    },
)


def run_async(coro):
    """Run an async function in the current event loop or create a new one."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


# =============================================================================
# Agent Tasks
# =============================================================================

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def run_code_review(
    self,
    repo_id: str,
    pr_number: int,
    diff_content: str,
    file_contents: dict[str, str],
    organization_id: str | None = None,
    user_id: str | None = None,
) -> dict[str, Any]:
    """Run code review on a pull request.

    Args:
        repo_id: Repository identifier
        pr_number: Pull request number
        diff_content: The diff to review
        file_contents: Dict mapping file paths to their contents
        organization_id: Optional organization ID
        user_id: Optional user ID

    Returns:
        Review results with comments and summary
    """
    from src.agents.code_reviewer.agent import CodeReviewerAgent
    from src.agents.base import AgentContext

    try:
        agent = CodeReviewerAgent()
        context = AgentContext(
            repository_id=repo_id,
            pr_number=pr_number,
            organization_id=organization_id,
            user_id=user_id,
        )

        result = run_async(agent.run(
            context,
            diff=diff_content,
            files=file_contents,
        ))

        return {
            "task_id": self.request.id,
            "status": "completed",
            "result": result,
        }
    except Exception as e:
        self.retry(exc=e)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def run_security_scan(
    self,
    repo_id: str,
    manifest_files: dict[str, str],
    organization_id: str | None = None,
    user_id: str | None = None,
) -> dict[str, Any]:
    """Run vulnerability scan on repository dependencies.

    Args:
        repo_id: Repository identifier
        manifest_files: Dict mapping manifest file paths to contents
            e.g., {"package.json": "...", "requirements.txt": "..."}
        organization_id: Optional organization ID
        user_id: Optional user ID

    Returns:
        Vulnerability scan results
    """
    from src.agents.vuln_scanner.agent import VulnScannerAgent
    from src.agents.base import AgentContext

    try:
        agent = VulnScannerAgent()
        context = AgentContext(
            repository_id=repo_id,
            organization_id=organization_id,
            user_id=user_id,
        )

        result = run_async(agent.run(
            context,
            manifests=manifest_files,
        ))

        return {
            "task_id": self.request.id,
            "status": "completed",
            "result": result,
        }
    except Exception as e:
        self.retry(exc=e)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def run_test_generation(
    self,
    repo_id: str,
    source_files: dict[str, str],
    existing_tests: dict[str, str] | None = None,
    framework: str = "pytest",
    organization_id: str | None = None,
    user_id: str | None = None,
) -> dict[str, Any]:
    """Generate tests for source code.

    Args:
        repo_id: Repository identifier
        source_files: Dict mapping source file paths to contents
        existing_tests: Optional dict of existing test files
        framework: Test framework to use (pytest, jest, etc.)
        organization_id: Optional organization ID
        user_id: Optional user ID

    Returns:
        Generated test files and coverage analysis
    """
    from src.agents.test_generator.agent import TestGeneratorAgent
    from src.agents.base import AgentContext

    try:
        agent = TestGeneratorAgent()
        context = AgentContext(
            repository_id=repo_id,
            organization_id=organization_id,
            user_id=user_id,
        )

        result = run_async(agent.run(
            context,
            files=source_files,
            existing_tests=existing_tests or {},
            framework=framework,
        ))

        return {
            "task_id": self.request.id,
            "status": "completed",
            "result": result,
        }
    except Exception as e:
        self.retry(exc=e)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def run_debt_analysis(
    self,
    repo_id: str,
    source_files: dict[str, str],
    organization_id: str | None = None,
    user_id: str | None = None,
) -> dict[str, Any]:
    """Analyze technical debt in codebase.

    Args:
        repo_id: Repository identifier
        source_files: Dict mapping source file paths to contents
        organization_id: Optional organization ID
        user_id: Optional user ID

    Returns:
        Technical debt analysis with scores and recommendations
    """
    from src.agents.debt_analyzer.agent import DebtAnalyzerAgent
    from src.agents.base import AgentContext

    try:
        agent = DebtAnalyzerAgent()
        context = AgentContext(
            repository_id=repo_id,
            organization_id=organization_id,
            user_id=user_id,
        )

        result = run_async(agent.run(
            context,
            files=source_files,
        ))

        return {
            "task_id": self.request.id,
            "status": "completed",
            "result": result,
        }
    except Exception as e:
        self.retry(exc=e)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def run_doc_generation(
    self,
    repo_id: str,
    source_files: dict[str, str],
    doc_format: str = "markdown",
    organization_id: str | None = None,
    user_id: str | None = None,
) -> dict[str, Any]:
    """Generate documentation for code.

    Args:
        repo_id: Repository identifier
        source_files: Dict mapping source file paths to contents
        doc_format: Output format (markdown, openapi, etc.)
        organization_id: Optional organization ID
        user_id: Optional user ID

    Returns:
        Generated documentation
    """
    from src.agents.doc_generator.agent import DocGeneratorAgent
    from src.agents.base import AgentContext

    try:
        agent = DocGeneratorAgent()
        context = AgentContext(
            repository_id=repo_id,
            organization_id=organization_id,
            user_id=user_id,
        )

        result = run_async(agent.run(
            context,
            files=source_files,
            format=doc_format,
        ))

        return {
            "task_id": self.request.id,
            "status": "completed",
            "result": result,
        }
    except Exception as e:
        self.retry(exc=e)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def run_incident_response(
    self,
    organization_id: str,
    alert_data: dict[str, Any],
    logs: list[str] | None = None,
    metrics: dict[str, Any] | None = None,
    user_id: str | None = None,
) -> dict[str, Any]:
    """Process and respond to an incident alert.

    Args:
        organization_id: Organization identifier
        alert_data: Alert information from monitoring system
        logs: Optional list of relevant log lines
        metrics: Optional dict of relevant metrics
        user_id: Optional user ID

    Returns:
        Incident analysis and recommended actions
    """
    from src.agents.incident_responder.agent import IncidentResponderAgent
    from src.agents.base import AgentContext

    try:
        agent = IncidentResponderAgent()
        context = AgentContext(
            organization_id=organization_id,
            user_id=user_id,
        )

        result = run_async(agent.run(
            context,
            alert=alert_data,
            logs=logs or [],
            metrics=metrics or {},
        ))

        return {
            "task_id": self.request.id,
            "status": "completed",
            "result": result,
        }
    except Exception as e:
        self.retry(exc=e)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=120)
def run_code_migration(
    self,
    repo_id: str,
    source_files: dict[str, str],
    migration_type: str,
    target_version: str | None = None,
    organization_id: str | None = None,
    user_id: str | None = None,
) -> dict[str, Any]:
    """Migrate code between frameworks or language versions.

    Args:
        repo_id: Repository identifier
        source_files: Dict mapping source file paths to contents
        migration_type: Type of migration (e.g., "react-class-to-hooks")
        target_version: Target version for migration
        organization_id: Optional organization ID
        user_id: Optional user ID

    Returns:
        Migrated code and migration report
    """
    from src.agents.code_migrator.agent import CodeMigratorAgent
    from src.agents.base import AgentContext

    try:
        agent = CodeMigratorAgent()
        context = AgentContext(
            repository_id=repo_id,
            organization_id=organization_id,
            user_id=user_id,
        )

        result = run_async(agent.run(
            context,
            files=source_files,
            migration_type=migration_type,
            target_version=target_version,
        ))

        return {
            "task_id": self.request.id,
            "status": "completed",
            "result": result,
        }
    except Exception as e:
        self.retry(exc=e)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def run_query_optimization(
    self,
    repo_id: str,
    queries: list[str],
    database_type: str = "postgresql",
    schema: dict[str, Any] | None = None,
    organization_id: str | None = None,
    user_id: str | None = None,
) -> dict[str, Any]:
    """Optimize database queries.

    Args:
        repo_id: Repository identifier
        queries: List of SQL queries to optimize
        database_type: Type of database (postgresql, mysql, etc.)
        schema: Optional database schema information
        organization_id: Optional organization ID
        user_id: Optional user ID

    Returns:
        Optimized queries and performance analysis
    """
    from src.agents.query_optimizer.agent import QueryOptimizerAgent
    from src.agents.base import AgentContext

    try:
        agent = QueryOptimizerAgent()
        context = AgentContext(
            repository_id=repo_id,
            organization_id=organization_id,
            user_id=user_id,
        )

        result = run_async(agent.run(
            context,
            queries=queries,
            database_type=database_type,
            schema=schema or {},
        ))

        return {
            "task_id": self.request.id,
            "status": "completed",
            "result": result,
        }
    except Exception as e:
        self.retry(exc=e)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def run_pipeline_generation(
    self,
    repo_id: str,
    project_files: dict[str, str],
    platform: str = "github_actions",
    organization_id: str | None = None,
    user_id: str | None = None,
) -> dict[str, Any]:
    """Generate CI/CD pipeline configuration.

    Args:
        repo_id: Repository identifier
        project_files: Dict mapping file paths to contents
            (package.json, requirements.txt, Dockerfile, etc.)
        platform: Target CI/CD platform
        organization_id: Optional organization ID
        user_id: Optional user ID

    Returns:
        Generated pipeline configuration
    """
    from src.agents.pipeline_generator.agent import PipelineGeneratorAgent
    from src.agents.base import AgentContext

    try:
        agent = PipelineGeneratorAgent()
        context = AgentContext(
            repository_id=repo_id,
            organization_id=organization_id,
            user_id=user_id,
        )

        result = run_async(agent.run(
            context,
            files=project_files,
            platform=platform,
        ))

        return {
            "task_id": self.request.id,
            "status": "completed",
            "result": result,
        }
    except Exception as e:
        self.retry(exc=e)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def run_adr_capture(
    self,
    repo_id: str,
    messages: list[dict[str, str]],
    source: str = "manual",
    next_adr_number: int = 1,
    organization_id: str | None = None,
    user_id: str | None = None,
) -> dict[str, Any]:
    """Capture architecture decisions from conversations.

    Args:
        repo_id: Repository identifier
        messages: List of conversation messages with 'author' and 'content'
        source: Source of the conversation (slack, github_pr, manual)
        next_adr_number: Number for the next ADR
        organization_id: Optional organization ID
        user_id: Optional user ID

    Returns:
        Generated ADR document
    """
    from src.agents.adr_recorder.agent import ADRRecorderAgent
    from src.agents.base import AgentContext

    try:
        agent = ADRRecorderAgent()
        context = AgentContext(
            repository_id=repo_id,
            organization_id=organization_id,
            user_id=user_id,
        )

        result = run_async(agent.run(
            context,
            action="capture",
            messages=messages,
            source=source,
            next_adr_number=next_adr_number,
        ))

        return {
            "task_id": self.request.id,
            "status": "completed",
            "result": result,
        }
    except Exception as e:
        self.retry(exc=e)


# =============================================================================
# Utility Tasks
# =============================================================================

@celery_app.task
def get_task_status(task_id: str) -> dict[str, Any]:
    """Get the status of a task.

    Args:
        task_id: The task ID to check

    Returns:
        Task status and result if available
    """
    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
        "error": str(result.result) if result.failed() else None,
    }


@celery_app.task
def health_check() -> dict[str, Any]:
    """Health check task for monitoring."""
    return {
        "status": "healthy",
        "worker": "celery",
    }
