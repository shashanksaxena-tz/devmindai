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

        # Find the enum member corresponding to the string
        try:
             # Check if migration_type is a valid MigrationType value
            mig_type_enum = next((t for t in MigrationType if t.value == migration_type), None)

            # If not found by value, default or handle error.
            # However, the logic below uses `PATTERNS` keys which are strings, not enum values.
            # But MigrationAnalysis requires MigrationType.

            # Wait, the `PATTERNS` keys are specific migration scenarios (e.g. "react_class_to_hooks"),
            # but `migration_type` argument seems to be "framework", "language" etc OR the scenario?

            # Re-reading the plan:
            # "migration_type" passed to scan seems to be the broader category (FRAMEWORK, etc)
            # OR the specific migration KEY (e.g. "react_class_to_hooks")?

            # Looking at `_scan_file`, it does `self.PATTERNS.get(migration_type, {})`.
            # So `migration_type` passed to `scan` MUST be the key in `PATTERNS` (e.g., "react_class_to_hooks").

            # But MigrationAnalysis expects `migration_type: MigrationType`.
            # So we need to derive the MigrationType from the pattern info.

            pattern_info = self.PATTERNS.get(migration_type)
            if pattern_info:
                mig_type_enum = pattern_info["type"]
            else:
                 # Fallback if unknown, or maybe raise error
                 # For now, let's assume it matches one of the values if not in patterns
                 mig_type_enum = next((t for t in MigrationType if t.value == migration_type), MigrationType.FRAMEWORK)

        except Exception:
            mig_type_enum = MigrationType.FRAMEWORK


        for file_path, content in files.items():
            file_targets = self._scan_file(file_path, content, migration_type)
            targets.extend(file_targets)

        # Estimate complexity
        estimated_hours = self._estimate_effort(targets)

        return MigrationAnalysis(
            migration_type=mig_type_enum,
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

        # If pattern is regex for content
        if not pattern.endswith("$") and not pattern.startswith("^"):
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

        # If pattern is checking file extension (like .js$)
        elif pattern.startswith("\\.") and pattern.endswith("$"):
             if re.search(pattern, path):
                 # Whole file is target
                 targets.append(MigrationTarget(
                    file_path=path,
                    line_start=1,
                    line_end=content.count("\n") + 1,
                    pattern_type=migration_type,
                    current_code="[WHOLE FILE]",
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
