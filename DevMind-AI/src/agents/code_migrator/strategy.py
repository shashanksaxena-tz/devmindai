"""Plans migration strategy."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .scanner import MigrationAnalysis, MigrationTarget


@dataclass
class MigrationPhase:
    """A phase of the migration."""
    name: str
    description: str
    targets: list[MigrationTarget]
    dependencies: list[str]
    order: int
    can_rollback: bool = True


@dataclass
class MigrationStrategy:
    """Complete migration strategy."""
    phases: list[MigrationPhase]
    total_phases: int
    breaking_changes: list[dict]
    rollback_plan: str
    testing_requirements: list[str]


class MigrationPlanner:
    """Plans phased migration strategy."""

    def __init__(self, llm_client: Any):
        self.llm_client = llm_client

    async def plan(self, analysis: MigrationAnalysis) -> MigrationStrategy:
        """Create a phased migration plan."""
        # Group targets by dependency order
        phases = self._create_phases(analysis.targets)

        # Identify breaking changes
        breaking_changes = await self._identify_breaking_changes(analysis)

        # Generate rollback plan
        rollback_plan = await self._generate_rollback_plan(phases)

        return MigrationStrategy(
            phases=phases,
            total_phases=len(phases),
            breaking_changes=breaking_changes,
            rollback_plan=rollback_plan,
            testing_requirements=self._get_testing_requirements(analysis),
        )

    def _create_phases(self, targets: list[MigrationTarget]) -> list[MigrationPhase]:
        """Group targets into phases."""
        # Simple grouping by file for now
        by_file: dict[str, list[MigrationTarget]] = {}
        for target in targets:
            by_file.setdefault(target.file_path, []).append(target)

        phases = []
        for i, (file_path, file_targets) in enumerate(by_file.items()):
            phases.append(MigrationPhase(
                name=f"Phase {i + 1}: {file_path.split('/')[-1]}",
                description=f"Migrate {len(file_targets)} targets in {file_path}",
                targets=file_targets,
                dependencies=[],
                order=i,
            ))

        return phases

    async def _identify_breaking_changes(self, analysis: MigrationAnalysis) -> list[dict]:
        """Identify breaking changes in the migration."""
        prompt = f"""Identify breaking changes for migration:
From: {analysis.source_version}
To: {analysis.target_version}
Type: {analysis.migration_type.value}

Return JSON: {{"breaking_changes": [{{"change": "...", "impact": "...", "mitigation": "..."}}]}}
"""
        try:
            response = await self.llm_client.generate(
                prompt=prompt,
                system="You are a migration expert.",
                response_format={"type": "json_object"},
            )
            # Assuming response is already a dict if LLM client handles JSON parsing
            # If not, might need json.loads, but BaseLLMClient often returns dict for structured/json format?
            # Looking at memory: "BaseLLMClient.generate_structured to ensure strictly typed JSON outputs."
            # Here we use `generate` with `response_format`. I should assume it returns string or dict.
            # If string, I need to parse.
            # Let's check `src/core/llm/base.py` if possible. But for now, let's assume it returns a dict-like object if we asked for JSON, or we might need to parse.
            # Wait, usually `generate` returns a string. `generate_structured` returns an object.
            # The code snippet in plan uses `response.get("breaking_changes", [])` suggesting `response` is a dict.
            # I'll check `BaseLLMClient` usage in other agents.

            if isinstance(response, str):
                import json
                try:
                    response = json.loads(response)
                except json.JSONDecodeError:
                     return []

            return response.get("breaking_changes", [])
        except Exception:
            return []

    async def _generate_rollback_plan(self, phases: list[MigrationPhase]) -> str:
        """Generate rollback instructions."""
        return "Revert commits in reverse phase order. Run test suite after each revert."

    def _get_testing_requirements(self, analysis: MigrationAnalysis) -> list[str]:
        """Determine testing requirements."""
        return [
            "Run full test suite after each phase",
            "Manual smoke testing of critical paths",
            "Performance comparison before/after",
        ]
