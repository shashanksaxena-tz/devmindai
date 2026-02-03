"""Folder analyzer for per-folder documentation generation."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class FolderInfo:
    """Information about a folder that should be documented."""

    path: Path  # Absolute path
    relative_path: Path  # Relative to project root
    score: int  # Priority score
    file_count: int  # Number of source files
    has_subfolders: bool  # Has documented subfolders
    primary_language: str  # Detected language


class FolderAnalyzer:
    """Analyzes project structure to identify folders needing documentation."""

    # Patterns to exclude from documentation
    EXCLUDED_PATTERNS = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "venv",
        ".venv",
        "env",
        "node_modules",
        ".git",
        ".svn",
        ".hg",
        "dist",
        "build",
        "target",
        "out",
        ".pytest_cache",
        ".mypy_cache",
        ".tox",
        "coverage",
        ".coverage",
        ".nyc_output",
        ".devmind",
        ".next",
        ".nuxt",
        "__tests__",
        ".eggs",
        "*.egg-info",
        ".cache",
        ".gradle",
        ".idea",
        ".vscode",
        "vendor",
        "bower_components",
    ]

    # Source code extensions
    SOURCE_EXTENSIONS = {
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".java",
        ".kt",
        ".go",
        ".rs",
        ".rb",
        ".php",
        ".cpp",
        ".c",
        ".h",
        ".cs",
        ".swift",
        ".scala",
        ".clj",
        ".ex",
        ".exs",
    }

    def analyze_folders(self, project_path: Path) -> List[FolderInfo]:
        """Analyze project to find folders that should be documented.

        Args:
            project_path: Root path of the project

        Returns:
            Sorted list of FolderInfo objects (highest score first)
        """
        folders: List[FolderInfo] = []

        # Walk directory tree
        for root, dirs, files in os.walk(project_path):
            root_path = Path(root)

            # Skip excluded directories - modify dirs in place
            dirs[:] = [d for d in dirs if not self._should_exclude_dir(d)]

            # Skip if the root itself is excluded
            if self._should_exclude(root_path):
                continue

            # Check if folder has source code
            source_files = [
                f for f in files if Path(f).suffix in self.SOURCE_EXTENSIONS
            ]

            if source_files:
                # Create FolderInfo
                folder_info = self._create_folder_info(
                    root_path, project_path, source_files, dirs
                )
                folders.append(folder_info)

        # Sort by score (highest first)
        folders.sort(key=lambda f: f.score, reverse=True)

        return folders

    def _should_exclude_dir(self, dir_name: str) -> bool:
        """Check if directory name should be excluded."""
        for pattern in self.EXCLUDED_PATTERNS:
            if pattern.startswith("*"):
                # Extension pattern
                if dir_name.endswith(pattern[1:]):
                    return True
            else:
                # Exact match
                if dir_name == pattern:
                    return True
        return False

    def _should_exclude(self, folder_path: Path) -> bool:
        """Check if folder should be excluded from documentation."""
        folder_name = folder_path.name

        for pattern in self.EXCLUDED_PATTERNS:
            if pattern.startswith("*"):
                # Extension pattern
                if folder_name.endswith(pattern[1:]):
                    return True
            else:
                # Exact match
                if folder_name == pattern:
                    return True

        return False

    def _create_folder_info(
        self,
        folder_path: Path,
        project_root: Path,
        source_files: List[str],
        subdirs: List[str],
    ) -> FolderInfo:
        """Create FolderInfo with calculated score."""
        relative_path = folder_path.relative_to(project_root)

        # Calculate score
        score = 0

        # +10: Contains package marker
        if "__init__.py" in source_files or "index.js" in source_files or "index.ts" in source_files:
            score += 10

        # +5: Contains 3+ source files
        if len(source_files) >= 3:
            score += 5

        # +3: Has subdirectories
        if subdirs:
            score += 3

        # +2: Name indicates significance
        significant_names = ["core", "agents", "api", "services", "lib", "src", "utils", "models", "routes", "handlers", "controllers"]
        if folder_path.name in significant_names:
            score += 2

        # +1: Contains tests
        if "test" in folder_path.name.lower() or "spec" in folder_path.name.lower():
            score += 1

        # Detect primary language
        extensions = {Path(f).suffix for f in source_files}
        primary_language = self._detect_primary_language(extensions)

        return FolderInfo(
            path=folder_path,
            relative_path=relative_path,
            score=score,
            file_count=len(source_files),
            has_subfolders=bool(subdirs),
            primary_language=primary_language,
        )

    def _detect_primary_language(self, extensions: set[str]) -> str:
        """Detect primary language from extensions."""
        if ".py" in extensions:
            return "python"
        elif ".ts" in extensions or ".tsx" in extensions:
            return "typescript"
        elif ".js" in extensions or ".jsx" in extensions:
            return "javascript"
        elif ".go" in extensions:
            return "go"
        elif ".rs" in extensions:
            return "rust"
        elif ".java" in extensions:
            return "java"
        elif ".kt" in extensions:
            return "kotlin"
        elif ".rb" in extensions:
            return "ruby"
        elif ".php" in extensions:
            return "php"
        elif ".cs" in extensions:
            return "csharp"
        elif ".swift" in extensions:
            return "swift"
        elif ".cpp" in extensions or ".c" in extensions:
            return "cpp"
        else:
            return "unknown"
