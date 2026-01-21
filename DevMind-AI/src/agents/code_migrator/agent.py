"""CodeMigrator agent."""
from __future__ import annotations

from typing import Any

from src.agents.base import BaseAgent, AgentContext
from src.core.llm import TaskComplexity, LLMRouter

from .scanner import MigrationScanner
from .strategy import MigrationPlanner
from .transformer import CodeTransformer


class CodeMigratorAgent(BaseAgent):
    """Agent that automates code migrations."""

    name = "code_migrator"
    description = "Analyzes and automates framework/language migrations"
    complexity = TaskComplexity.COMPLEX

    def __init__(self, router: LLMRouter | None = None):
        super().__init__(router)
        self.scanner = MigrationScanner()
        self.planner = MigrationPlanner(self.llm_client)
        self.transformer = CodeTransformer(self.llm_client)

    async def execute(
        self,
        context: AgentContext,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Execute a migration."""
        files = kwargs.get("files", {})
        migration_type = kwargs.get("migration_type", "")
        source_version = kwargs.get("source_version", "")
        target_version = kwargs.get("target_version", "")
        dry_run = kwargs.get("dry_run", True)

        # Scan codebase
        analysis = self.scanner.scan(
            files, migration_type, source_version, target_version
        )

        # Plan migration
        strategy = await self.planner.plan(analysis)

        # Transform if not dry run
        results = []
        if not dry_run:
            for phase in strategy.phases:
                for target in phase.targets:
                    result = await self.transformer.transform(
                        target,
                        files.get(target.file_path, ""),
                        migration_type,
                        target_version,
                    )
                    results.append(result)

        return {
            "analysis": {
                "total_files": analysis.total_files,
                "total_targets": len(analysis.targets),
                "estimated_hours": analysis.estimated_hours,
            },
            "strategy": {
                "phases": len(strategy.phases),
                "breaking_changes": len(strategy.breaking_changes),
            },
            "transforms": [
                {"file": r.file_path, "success": r.success}
                for r in results
            ] if results else [],
            "dry_run": dry_run,
        }
