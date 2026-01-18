# DevMind AI Phase 8: CodeMigrator Agent Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an intelligent code migration agent that analyzes legacy codebases and automates migration between frameworks, languages, or versions.

**Architecture:** Multi-phase migration system with Scanner (analysis), Strategy (planning), Transformer (code generation), and Validator (verification). Uses Claude for complex code transformations.

**Tech Stack:** FastAPI, tree-sitter for AST, Claude API, ast-grep for pattern matching

**Prerequisites:** Phase 1 (Foundation) completed

---

## Task 1: Migration Scanner and Analyzer

**Files:**
- Create: `src/agents/code_migrator/scanner.py`
- Create: `src/agents/code_migrator/patterns.py`
- Test: `tests/agents/code_migrator/test_scanner.py`

### Implementation Overview

```python
# src/agents/code_migrator/scanner.py
"""Scans codebase for migration targets."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MigrationType(Enum):
    """Types of migrations supported."""
    FRAMEWORK = "framework"  # React Class -> Hooks, Vue 2 -> 3
    LANGUAGE = "language"  # JS -> TS, Python 2 -> 3
    LIBRARY = "library"  # Moment.js -> date-fns
    API_VERSION = "api_version"  # REST -> GraphQL, SDK upgrades


@dataclass
class MigrationTarget:
    """A file/code block that needs migration."""
    file_path: str
    line_start: int
    line_end: int
    pattern_type: str
    current_code: str
    complexity: str  # simple, moderate, complex
    dependencies: list[str] = field(default_factory=list)


@dataclass
class MigrationAnalysis:
    """Analysis of a codebase for migration."""
    migration_type: MigrationType
    source_version: str
    target_version: str
    targets: list[MigrationTarget] = field(default_factory=list)
    total_files: int = 0
    estimated_hours: float = 0.0
    breaking_changes: list[str] = field(default_factory=list)


class MigrationScanner:
    """Scans codebase to identify migration targets."""

    # Pattern definitions for common migrations
    PATTERNS = {
        "react_class_to_hooks": {
            "pattern": r"class\s+\w+\s+extends\s+(React\.)?Component",
            "type": MigrationType.FRAMEWORK,
        },
        "vue2_to_vue3": {
            "pattern": r"new Vue\({",
            "type": MigrationType.FRAMEWORK,
        },
        "moment_to_datefns": {
            "pattern": r"import.*from\s+['\"]moment['\"]",
            "type": MigrationType.LIBRARY,
        },
        "js_to_ts": {
            "pattern": r"\.js$",  # File extension
            "type": MigrationType.LANGUAGE,
        },
    }

    def scan(
        self,
        files: dict[str, str],
        migration_type: str,
        source_version: str,
        target_version: str,
    ) -> MigrationAnalysis:
        """Scan files for migration targets."""
        targets = []

        for file_path, content in files.items():
            file_targets = self._scan_file(file_path, content, migration_type)
            targets.extend(file_targets)

        # Estimate complexity
        estimated_hours = self._estimate_effort(targets)

        return MigrationAnalysis(
            migration_type=MigrationType(migration_type),
            source_version=source_version,
            target_version=target_version,
            targets=targets,
            total_files=len(set(t.file_path for t in targets)),
            estimated_hours=estimated_hours,
        )

    def _scan_file(self, path: str, content: str, migration_type: str) -> list[MigrationTarget]:
        """Scan a single file for patterns."""
        targets = []
        pattern_info = self.PATTERNS.get(migration_type, {})

        if not pattern_info:
            return targets

        import re
        pattern = pattern_info.get("pattern", "")

        for match in re.finditer(pattern, content, re.MULTILINE):
            line_num = content[:match.start()].count("\n") + 1
            targets.append(MigrationTarget(
                file_path=path,
                line_start=line_num,
                line_end=line_num + 10,  # Estimate
                pattern_type=migration_type,
                current_code=match.group(0),
                complexity="moderate",
            ))

        return targets

    def _estimate_effort(self, targets: list[MigrationTarget]) -> float:
        """Estimate migration effort in hours."""
        hours = 0.0
        for target in targets:
            if target.complexity == "simple":
                hours += 0.25
            elif target.complexity == "moderate":
                hours += 1.0
            else:
                hours += 3.0
        return hours
```

---

## Task 2: Migration Strategy Planner

**Files:**
- Create: `src/agents/code_migrator/strategy.py`
- Test: `tests/agents/code_migrator/test_strategy.py`

### Implementation Overview

```python
# src/agents/code_migrator/strategy.py
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
        response = await self.llm_client.generate(
            prompt=prompt,
            system="You are a migration expert.",
            response_format={"type": "json_object"},
        )
        return response.get("breaking_changes", [])

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
```

---

## Task 3: Code Transformer

**Files:**
- Create: `src/agents/code_migrator/transformer.py`
- Test: `tests/agents/code_migrator/test_transformer.py`

### Implementation Overview

```python
# src/agents/code_migrator/transformer.py
"""Transforms code for migration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .scanner import MigrationTarget


@dataclass
class TransformResult:
    """Result of code transformation."""
    file_path: str
    original_code: str
    transformed_code: str
    success: bool
    error: Optional[str] = None
    diff: str = ""


class CodeTransformer:
    """Transforms code using LLM."""

    def __init__(self, llm_client: Any):
        self.llm_client = llm_client

    async def transform(
        self,
        target: MigrationTarget,
        full_file_content: str,
        migration_type: str,
        target_version: str,
    ) -> TransformResult:
        """Transform a migration target."""
        prompt = f"""Transform this code from {migration_type} to {target_version}:

Original code:
```
{target.current_code}
```

Full file context:
```
{full_file_content[:2000]}
```

Requirements:
1. Preserve all functionality
2. Follow {target_version} best practices
3. Maintain code style consistency

Return only the transformed code, no explanations.
"""

        try:
            transformed = await self.llm_client.generate(
                prompt=prompt,
                system=f"You are an expert at {migration_type} migrations.",
            )

            # Apply transformation to full file
            new_content = full_file_content.replace(
                target.current_code,
                transformed,
            )

            return TransformResult(
                file_path=target.file_path,
                original_code=target.current_code,
                transformed_code=transformed,
                success=True,
                diff=self._generate_diff(target.current_code, transformed),
            )

        except Exception as e:
            return TransformResult(
                file_path=target.file_path,
                original_code=target.current_code,
                transformed_code="",
                success=False,
                error=str(e),
            )

    def _generate_diff(self, original: str, transformed: str) -> str:
        """Generate unified diff."""
        import difflib
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            transformed.splitlines(keepends=True),
            fromfile="original",
            tofile="transformed",
        )
        return "".join(diff)
```

---

## Task 4: CodeMigrator Agent and API

**Files:**
- Create: `src/agents/code_migrator/agent.py`
- Create: `src/api/routes/migrations.py`
- Test: `tests/agents/code_migrator/test_agent.py`

### Implementation Overview

```python
# src/agents/code_migrator/agent.py
"""CodeMigrator agent."""
from __future__ import annotations

from typing import Any

from src.core.agents import BaseAgent, AgentContext, TaskComplexity

from .scanner import MigrationScanner
from .strategy import MigrationPlanner
from .transformer import CodeTransformer


class CodeMigratorAgent(BaseAgent):
    """Agent that automates code migrations."""

    name = "code_migrator"
    description = "Analyzes and automates framework/language migrations"
    complexity = TaskComplexity.COMPLEX

    def __init__(self, llm_client: Any):
        super().__init__(llm_client)
        self.scanner = MigrationScanner()
        self.planner = MigrationPlanner(llm_client)
        self.transformer = CodeTransformer(llm_client)

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
```

---

## Summary

Phase 8 (CodeMigrator Agent) consists of 4 tasks:

1. **Migration Scanner** - Identify migration targets using pattern matching
2. **Strategy Planner** - Create phased migration plan with breaking change analysis
3. **Code Transformer** - LLM-powered code transformation
4. **CodeMigrator Agent & API** - Orchestration and REST endpoints

**Estimated Implementation Time:** ~1.5 weeks

**Dependencies:** Phase 1 (Foundation)
