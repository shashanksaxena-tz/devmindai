# Per-Folder Documentation Generator - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

## ✅ IMPLEMENTATION COMPLETE (2026-02-02)

**All 9 tasks completed.** All 43 tests passing.

### Files Created:
- `src/agents/project_documenter/folder_analyzer.py` - FolderAnalyzer and FolderInfo
- `src/agents/project_documenter/smart_merger.py` - SmartMerger with section preservation
- `src/agents/project_documenter/metadata_manager.py` - MetadataManager for change tracking
- `src/agents/project_documenter/per_folder_generator.py` - PerFolderGenerator with LLM integration
- `src/agents/project_documenter/index_builder.py` - IndexBuilder for navigation indexes
- `tests/agents/project_documenter/test_folder_analyzer.py` - Test suite (7 tests)
- `tests/agents/project_documenter/test_smart_merger.py` - Test suite (9 tests)
- `tests/agents/project_documenter/test_metadata_manager.py` - Test suite (12 tests)
- `tests/agents/project_documenter/test_per_folder_generator.py` - Test suite (9 tests)
- `tests/agents/project_documenter/test_e2e_per_folder.py` - E2E workflow tests (7 tests)

### Files Modified:
- `src/agents/project_documenter/__init__.py` - Added new component exports
- `src/agents/project_documenter/agent.py` - Integrated per-folder generation and added _generate_per_folder_docs method
- `src/cli/commands/document.py` - Added CLI options: --per-folder, --no-per-folder, --incremental, --force

### CLI Usage:
```bash
devmind document ./my-project -w                    # Generate all docs with per-folder
devmind document ./my-project -w --incremental      # Only regenerate changed folders
devmind document ./my-project -w --no-per-folder    # Skip per-folder doc generation
devmind document ./my-project -w --force            # Force regenerate all folders
```

---

**Goal:** Add per-folder documentation generation (AI-CONTEXT.md + README.md) to Project Documenter Agent with smart preservation and change tracking.

**Architecture:** Four new components (FolderAnalyzer, PerFolderGenerator, SmartMerger, MetadataManager) integrated into existing ProjectDocumenterAgent. Uses LLM for content generation, HTML markers for preservation, SHA256 hashing for change detection.

**Tech Stack:** Python 3.11+, asyncio, pathlib, dataclasses, hashlib, existing LLM router

---

## Task 1: Create FolderInfo Dataclass and FolderAnalyzer Foundation

**Files:**
- Create: `DevMind-AI/src/agents/project_documenter/folder_analyzer.py`
- Create: `DevMind-AI/tests/agents/project_documenter/test_folder_analyzer.py`

**Step 1: Write the failing test**

Create test file:
```python
"""Tests for FolderAnalyzer."""

from pathlib import Path
import pytest
from src.agents.project_documenter.folder_analyzer import FolderAnalyzer, FolderInfo


def test_folder_analyzer_identifies_code_folders(tmp_path):
    """Test that FolderAnalyzer finds folders with source code."""
    # Create test structure
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "agents").mkdir()
    (tmp_path / "src" / "agents" / "agent.py").write_text("class Agent: pass")
    (tmp_path / "src" / "agents" / "__init__.py").write_text("")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "test.pyc").write_text("compiled")

    analyzer = FolderAnalyzer()
    folders = analyzer.analyze_folders(tmp_path)

    # Should find src/agents but not __pycache__
    folder_paths = [f.relative_path for f in folders]
    assert Path("src/agents") in folder_paths
    assert Path("__pycache__") not in folder_paths
    assert len(folders) > 0


def test_folder_info_scoring():
    """Test folder scoring prioritization."""
    # Will implement after FolderInfo dataclass exists
    pass
```

**Step 2: Run test to verify it fails**

Run: `cd DevMind-AI && poetry run pytest tests/agents/project_documenter/test_folder_analyzer.py::test_folder_analyzer_identifies_code_folders -v`

Expected: FAIL with "No module named 'folder_analyzer'"

**Step 3: Create FolderInfo dataclass**

Create `DevMind-AI/src/agents/project_documenter/folder_analyzer.py`:
```python
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

            # Skip excluded directories
            if self._should_exclude(root_path):
                dirs.clear()  # Don't recurse into excluded dirs
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
        if "__init__.py" in source_files or "index.js" in source_files:
            score += 10

        # +5: Contains 3+ source files
        if len(source_files) >= 3:
            score += 5

        # +3: Has subdirectories
        if subdirs:
            score += 3

        # +2: Name indicates significance
        significant_names = ["core", "agents", "api", "services", "lib", "src"]
        if folder_path.name in significant_names:
            score += 2

        # +1: Contains tests
        if "test" in folder_path.name.lower():
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
        else:
            return "unknown"
```

**Step 4: Run test to verify it passes**

Run: `cd DevMind-AI && poetry run pytest tests/agents/project_documenter/test_folder_analyzer.py::test_folder_analyzer_identifies_code_folders -v`

Expected: PASS

**Step 5: Commit**

```bash
cd DevMind-AI
git add src/agents/project_documenter/folder_analyzer.py tests/agents/project_documenter/test_folder_analyzer.py
git commit -m "feat(docs): add FolderAnalyzer to identify folders for documentation

- Add FolderInfo dataclass with scoring
- Add FolderAnalyzer with exclusion patterns
- Implement folder scoring (package marker, file count, etc.)
- Add test for folder identification"
```

---

## Task 2: Create SmartMerger with Marker Parsing

**Files:**
- Create: `DevMind-AI/src/agents/project_documenter/smart_merger.py`
- Create: `DevMind-AI/tests/agents/project_documenter/test_smart_merger.py`

**Step 1: Write the failing test**

```python
"""Tests for SmartMerger."""

import pytest
from src.agents.project_documenter.smart_merger import SmartMerger, Section


def test_smart_merger_preserves_custom_sections():
    """Test that custom sections are preserved during merge."""
    existing = """
# Module

<!-- AUTO-GENERATED: Purpose - DO NOT EDIT -->
## Purpose
Old purpose text
<!-- END AUTO-GENERATED -->

<!-- CUSTOM SECTION: My notes -->
## My Custom Notes
User-added content here
<!-- END CUSTOM SECTION -->
"""

    new_content = """
# Module

<!-- AUTO-GENERATED: Purpose - DO NOT EDIT -->
## Purpose
New updated purpose text
<!-- END AUTO-GENERATED -->

<!-- CUSTOM SECTION: My notes -->
## My Custom Notes
<!-- END CUSTOM SECTION -->
"""

    merger = SmartMerger()
    result = merger.merge(existing, new_content)

    assert "New updated purpose text" in result
    assert "User-added content here" in result
    assert "Old purpose text" not in result


def test_smart_merger_handles_new_sections():
    """Test that new auto-generated sections are added."""
    existing = """
# Module

<!-- AUTO-GENERATED: Purpose - DO NOT EDIT -->
## Purpose
Old purpose
<!-- END AUTO-GENERATED -->
"""

    new_content = """
# Module

<!-- AUTO-GENERATED: Purpose - DO NOT EDIT -->
## Purpose
Updated purpose
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: New Section - DO NOT EDIT -->
## New Section
This is new
<!-- END AUTO-GENERATED -->
"""

    merger = SmartMerger()
    result = merger.merge(existing, new_content)

    assert "Updated purpose" in result
    assert "This is new" in result


def test_smart_merger_no_markers_generates_fresh():
    """Test that files without markers are generated fresh."""
    existing = """
# Manual File
No markers here
"""

    new_content = """
<!-- AUTO-GENERATED: Purpose - DO NOT EDIT -->
## Purpose
Fresh content with markers
<!-- END AUTO-GENERATED -->
"""

    merger = SmartMerger()
    result = merger.merge(existing, new_content)

    assert "Fresh content with markers" in result
```

**Step 2: Run test to verify it fails**

Run: `cd DevMind-AI && poetry run pytest tests/agents/project_documenter/test_smart_merger.py -v`

Expected: FAIL with "No module named 'smart_merger'"

**Step 3: Implement SmartMerger**

Create `DevMind-AI/src/agents/project_documenter/smart_merger.py`:
```python
"""Smart content merger that preserves custom sections."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict


class SectionType(Enum):
    """Type of content section."""

    AUTO_GENERATED = "AUTO-GENERATED"
    CUSTOM = "CUSTOM"
    UNTAGGED = "UNTAGGED"


@dataclass
class Section:
    """A section of content with markers."""

    section_type: SectionType
    name: str  # Section identifier (e.g., "Purpose", "My notes")
    content: str  # Content between markers
    raw: str  # Full section including markers


class SmartMerger:
    """Merges new generated content while preserving custom sections."""

    # Regex patterns for markers
    AUTO_START_PATTERN = re.compile(
        r"<!--\s*AUTO-GENERATED:\s*(.+?)\s*-\s*DO NOT EDIT\s*-->"
    )
    AUTO_END_PATTERN = re.compile(r"<!--\s*END AUTO-GENERATED\s*-->")

    CUSTOM_START_PATTERN = re.compile(r"<!--\s*CUSTOM SECTION:\s*(.+?)\s*-->")
    CUSTOM_END_PATTERN = re.compile(r"<!--\s*END CUSTOM SECTION\s*-->")

    def merge(self, existing: str, new_content: str) -> str:
        """Merge new content with existing, preserving custom sections.

        Args:
            existing: Existing file content
            new_content: Newly generated content

        Returns:
            Merged content with custom sections preserved
        """
        # Parse both contents
        existing_sections = self._parse_sections(existing)
        new_sections = self._parse_sections(new_content)

        # If existing has no markers, return new content (fresh generation)
        if not any(
            s.section_type in [SectionType.AUTO_GENERATED, SectionType.CUSTOM]
            for s in existing_sections
        ):
            return new_content

        # Build merged content
        result_sections: List[str] = []
        existing_custom = {
            s.name: s for s in existing_sections if s.section_type == SectionType.CUSTOM
        }

        for section in new_sections:
            if section.section_type == SectionType.AUTO_GENERATED:
                # Use new auto-generated content
                result_sections.append(section.raw)
            elif section.section_type == SectionType.CUSTOM:
                # Use existing custom content if present, otherwise new (empty) custom
                if section.name in existing_custom:
                    result_sections.append(existing_custom[section.name].raw)
                else:
                    result_sections.append(section.raw)
            else:
                # Untagged content (headers, etc.)
                result_sections.append(section.content)

        return "\n".join(result_sections)

    def _parse_sections(self, content: str) -> List[Section]:
        """Parse content into sections based on markers."""
        sections: List[Section] = []
        lines = content.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check for AUTO-GENERATED start
            auto_match = self.AUTO_START_PATTERN.search(line)
            if auto_match:
                section_name = auto_match.group(1)
                section_lines = [line]
                i += 1

                # Collect lines until END AUTO-GENERATED
                while i < len(lines):
                    section_lines.append(lines[i])
                    if self.AUTO_END_PATTERN.search(lines[i]):
                        i += 1
                        break
                    i += 1

                raw = "\n".join(section_lines)
                # Extract content between markers (exclude marker lines)
                content_lines = section_lines[1:-1]
                content = "\n".join(content_lines)

                sections.append(
                    Section(
                        section_type=SectionType.AUTO_GENERATED,
                        name=section_name,
                        content=content,
                        raw=raw,
                    )
                )
                continue

            # Check for CUSTOM SECTION start
            custom_match = self.CUSTOM_START_PATTERN.search(line)
            if custom_match:
                section_name = custom_match.group(1)
                section_lines = [line]
                i += 1

                # Collect lines until END CUSTOM SECTION
                while i < len(lines):
                    section_lines.append(lines[i])
                    if self.CUSTOM_END_PATTERN.search(lines[i]):
                        i += 1
                        break
                    i += 1

                raw = "\n".join(section_lines)
                content_lines = section_lines[1:-1]
                content = "\n".join(content_lines)

                sections.append(
                    Section(
                        section_type=SectionType.CUSTOM,
                        name=section_name,
                        content=content,
                        raw=raw,
                    )
                )
                continue

            # Untagged line
            sections.append(
                Section(
                    section_type=SectionType.UNTAGGED,
                    name="",
                    content=line,
                    raw=line,
                )
            )
            i += 1

        return sections
```

**Step 4: Run test to verify it passes**

Run: `cd DevMind-AI && poetry run pytest tests/agents/project_documenter/test_smart_merger.py -v`

Expected: PASS

**Step 5: Commit**

```bash
cd DevMind-AI
git add src/agents/project_documenter/smart_merger.py tests/agents/project_documenter/test_smart_merger.py
git commit -m "feat(docs): add SmartMerger for preserving custom content

- Parse AUTO-GENERATED and CUSTOM SECTION markers
- Merge new content while preserving user edits
- Handle files without markers (fresh generation)
- Add comprehensive tests for merge scenarios"
```

---

## Task 3: Create MetadataManager for Change Tracking

**Files:**
- Create: `DevMind-AI/src/agents/project_documenter/metadata_manager.py`
- Create: `DevMind-AI/tests/agents/project_documenter/test_metadata_manager.py`

**Step 1: Write the failing test**

```python
"""Tests for MetadataManager."""

from pathlib import Path
import pytest
import json
from src.agents.project_documenter.metadata_manager import MetadataManager, FolderMetadata


def test_metadata_manager_tracks_folder_hashes(tmp_path):
    """Test that MetadataManager stores and retrieves folder hashes."""
    project_path = tmp_path / "project"
    project_path.mkdir()
    (project_path / "src").mkdir()
    (project_path / "src" / "main.py").write_text("print('hello')")

    manager = MetadataManager()
    manager.initialize(project_path)

    # Update folder metadata
    folder_path = project_path / "src"
    manager.update_folder(folder_path, file_count=1)

    # Verify metadata is stored
    metadata = manager.get_folder_metadata(folder_path)
    assert metadata is not None
    assert metadata.file_count == 1
    assert metadata.content_hash != ""


def test_metadata_manager_detects_changes(tmp_path):
    """Test that MetadataManager detects when folder content changes."""
    project_path = tmp_path / "project"
    project_path.mkdir()
    (project_path / "src").mkdir()
    (project_path / "src" / "main.py").write_text("print('hello')")

    manager = MetadataManager()
    manager.initialize(project_path)

    folder_path = project_path / "src"
    manager.update_folder(folder_path, file_count=1)

    # Modify file
    (project_path / "src" / "main.py").write_text("print('world')")

    # Should detect change
    assert manager.has_folder_changed(folder_path) is True
```

**Step 2: Run test to verify it fails**

Run: `cd DevMind-AI && poetry run pytest tests/agents/project_documenter/test_metadata_manager.py -v`

Expected: FAIL with "No module named 'metadata_manager'"

**Step 3: Implement MetadataManager**

Create `DevMind-AI/src/agents/project_documenter/metadata_manager.py`:
```python
"""Metadata manager for tracking documentation generation state."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


@dataclass
class FolderMetadata:
    """Metadata for a documented folder."""

    last_generated: str  # ISO timestamp
    content_hash: str  # SHA256 hash of source files
    file_count: int
    files: Dict[str, str]  # filename -> hash


class MetadataManager:
    """Manages metadata for documentation generation tracking."""

    METADATA_DIR = ".devmind"
    METADATA_FILE = "doc-metadata.json"

    def __init__(self):
        """Initialize metadata manager."""
        self.project_root: Optional[Path] = None
        self.metadata: Dict[str, any] = {}

    def initialize(self, project_path: Path) -> None:
        """Initialize metadata for a project.

        Args:
            project_path: Root path of the project
        """
        self.project_root = project_path
        self.metadata_file = project_path / self.METADATA_DIR / self.METADATA_FILE

        # Create .devmind directory if it doesn't exist
        self.metadata_file.parent.mkdir(exist_ok=True)

        # Load existing metadata if present
        if self.metadata_file.exists():
            with open(self.metadata_file, "r") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {
                "version": "1.0",
                "last_full_run": None,
                "project_root": str(project_path),
                "folders": {},
            }

    def update_folder(self, folder_path: Path, file_count: int) -> None:
        """Update metadata for a folder after documentation generation.

        Args:
            folder_path: Path to the documented folder
            file_count: Number of source files in folder
        """
        if not self.project_root:
            raise RuntimeError("MetadataManager not initialized")

        relative_path = str(folder_path.relative_to(self.project_root))

        # Compute content hash
        content_hash, file_hashes = self._compute_folder_hash(folder_path)

        # Update metadata
        self.metadata["folders"][relative_path] = {
            "last_generated": datetime.utcnow().isoformat() + "Z",
            "content_hash": content_hash,
            "file_count": file_count,
            "files": file_hashes,
        }

        # Save to disk
        self._save()

    def get_folder_metadata(self, folder_path: Path) -> Optional[FolderMetadata]:
        """Get metadata for a folder.

        Args:
            folder_path: Path to the folder

        Returns:
            FolderMetadata if exists, None otherwise
        """
        if not self.project_root:
            return None

        relative_path = str(folder_path.relative_to(self.project_root))
        folder_data = self.metadata["folders"].get(relative_path)

        if folder_data:
            return FolderMetadata(**folder_data)

        return None

    def has_folder_changed(self, folder_path: Path) -> bool:
        """Check if folder content has changed since last generation.

        Args:
            folder_path: Path to the folder

        Returns:
            True if folder has changed or is new, False otherwise
        """
        if not self.project_root:
            return True

        # Get stored metadata
        metadata = self.get_folder_metadata(folder_path)
        if not metadata:
            return True  # New folder

        # Compute current hash
        current_hash, _ = self._compute_folder_hash(folder_path)

        return current_hash != metadata.content_hash

    def _compute_folder_hash(self, folder_path: Path) -> tuple[str, Dict[str, str]]:
        """Compute SHA256 hash of all source files in folder.

        Args:
            folder_path: Path to the folder

        Returns:
            Tuple of (combined_hash, file_hashes)
        """
        source_extensions = {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs"}

        file_hashes: Dict[str, str] = {}
        hash_list = []

        # Get all source files
        source_files = sorted(
            [f for f in folder_path.iterdir() if f.suffix in source_extensions]
        )

        for file_path in source_files:
            try:
                content = file_path.read_bytes()
                file_hash = hashlib.sha256(content).hexdigest()
                file_hashes[file_path.name] = file_hash
                hash_list.append(file_hash)
            except Exception:
                continue

        # Combine all file hashes
        combined = "".join(hash_list)
        combined_hash = hashlib.sha256(combined.encode()).hexdigest()

        return combined_hash, file_hashes

    def _save(self) -> None:
        """Save metadata to disk."""
        if not self.metadata_file:
            return

        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f, indent=2)

    def mark_full_run(self) -> None:
        """Mark that a full documentation run has completed."""
        self.metadata["last_full_run"] = datetime.utcnow().isoformat() + "Z"
        self._save()
```

**Step 4: Run test to verify it passes**

Run: `cd DevMind-AI && poetry run pytest tests/agents/project_documenter/test_metadata_manager.py -v`

Expected: PASS

**Step 5: Commit**

```bash
cd DevMind-AI
git add src/agents/project_documenter/metadata_manager.py tests/agents/project_documenter/test_metadata_manager.py
git commit -m "feat(docs): add MetadataManager for change tracking

- Track folder content hashes with SHA256
- Detect changes in source files
- Store metadata in .devmind/doc-metadata.json
- Enable incremental documentation regeneration"
```

---

## Task 4: Create PerFolderGenerator with LLM Integration

**Files:**
- Create: `DevMind-AI/src/agents/project_documenter/per_folder_generator.py`
- Create: `DevMind-AI/tests/agents/project_documenter/test_per_folder_generator.py`

**Step 1: Write the failing test**

```python
"""Tests for PerFolderGenerator."""

from pathlib import Path
import pytest
from unittest.mock import Mock, AsyncMock
from src.agents.project_documenter.per_folder_generator import PerFolderGenerator
from src.agents.project_documenter.folder_analyzer import FolderInfo
from src.agents.project_documenter.analyzer import CodebaseProfile


@pytest.mark.asyncio
async def test_per_folder_generator_creates_ai_context():
    """Test that PerFolderGenerator generates AI-CONTEXT.md."""
    # Mock LLM client
    llm_client = Mock()
    llm_client.generate_text = AsyncMock(return_value="Generated AI context content")

    generator = PerFolderGenerator(llm_client)

    folder_info = FolderInfo(
        path=Path("/project/src/agents"),
        relative_path=Path("src/agents"),
        score=15,
        file_count=5,
        has_subfolders=True,
        primary_language="python",
    )

    profile = Mock(spec=CodebaseProfile)

    result = await generator.generate_ai_context(folder_info, profile)

    assert result.path == "src/agents/AI-CONTEXT.md"
    assert "AUTO-GENERATED" in result.content
    assert "CUSTOM SECTION" in result.content


@pytest.mark.asyncio
async def test_per_folder_generator_creates_readme():
    """Test that PerFolderGenerator generates README.md."""
    llm_client = Mock()
    llm_client.generate_text = AsyncMock(return_value="Generated README content")

    generator = PerFolderGenerator(llm_client)

    folder_info = FolderInfo(
        path=Path("/project/src/api"),
        relative_path=Path("src/api"),
        score=12,
        file_count=3,
        has_subfolders=False,
        primary_language="python",
    )

    profile = Mock(spec=CodebaseProfile)

    result = await generator.generate_readme(folder_info, profile)

    assert result.path == "src/api/README.md"
    assert "Overview" in result.content
```

**Step 2: Run test to verify it fails**

Run: `cd DevMind-AI && poetry run pytest tests/agents/project_documenter/test_per_folder_generator.py -v`

Expected: FAIL with "No module named 'per_folder_generator'"

**Step 3: Implement PerFolderGenerator**

Create `DevMind-AI/src/agents/project_documenter/per_folder_generator.py`:
```python
"""Per-folder documentation generator."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from src.agents.project_documenter.folder_analyzer import FolderInfo
from src.agents.project_documenter.generators.base import GeneratedDoc

if TYPE_CHECKING:
    from src.core.llm import BaseLLMClient
    from src.agents.project_documenter.analyzer import CodebaseProfile


class PerFolderGenerator:
    """Generates per-folder documentation (AI-CONTEXT.md and README.md)."""

    def __init__(self, llm_client: BaseLLMClient):
        """Initialize generator.

        Args:
            llm_client: LLM client for content generation
        """
        self.llm_client = llm_client

    async def generate_ai_context(
        self, folder_info: FolderInfo, profile: CodebaseProfile
    ) -> GeneratedDoc:
        """Generate AI-CONTEXT.md for a folder.

        Args:
            folder_info: Information about the folder
            profile: Codebase profile for context

        Returns:
            GeneratedDoc with AI-CONTEXT.md content
        """
        # Read folder contents
        folder_contents = self._analyze_folder_contents(folder_info.path)

        # Build prompt
        prompt = self._build_ai_context_prompt(folder_info, profile, folder_contents)

        # Generate content with LLM
        generated_content = await self.llm_client.generate_text(
            prompt, max_tokens=2000
        )

        # Wrap in template with markers
        full_content = self._wrap_ai_context_template(
            folder_info.relative_path.name, generated_content
        )

        return GeneratedDoc(
            path=str(folder_info.relative_path / "AI-CONTEXT.md"),
            content=full_content,
            format_name="per_folder",
            description=f"AI context for {folder_info.relative_path}",
        )

    async def generate_readme(
        self, folder_info: FolderInfo, profile: CodebaseProfile
    ) -> GeneratedDoc:
        """Generate README.md for a folder.

        Args:
            folder_info: Information about the folder
            profile: Codebase profile for context

        Returns:
            GeneratedDoc with README.md content
        """
        # Read folder contents
        folder_contents = self._analyze_folder_contents(folder_info.path)

        # Build prompt
        prompt = self._build_readme_prompt(folder_info, profile, folder_contents)

        # Generate content with LLM
        generated_content = await self.llm_client.generate_text(
            prompt, max_tokens=1500
        )

        # Wrap in template with markers
        full_content = self._wrap_readme_template(
            folder_info.relative_path.name, generated_content
        )

        return GeneratedDoc(
            path=str(folder_info.relative_path / "README.md"),
            content=full_content,
            format_name="per_folder",
            description=f"README for {folder_info.relative_path}",
        )

    def _analyze_folder_contents(self, folder_path: Path) -> dict:
        """Analyze folder to extract key information."""
        source_extensions = {".py", ".js", ".ts", ".tsx", ".jsx"}

        files = []
        for file_path in sorted(folder_path.iterdir()):
            if file_path.suffix in source_extensions:
                try:
                    # Read first 50 lines for context
                    lines = file_path.read_text().split("\n")[:50]
                    files.append(
                        {"name": file_path.name, "preview": "\n".join(lines)}
                    )
                except Exception:
                    files.append({"name": file_path.name, "preview": ""})

        return {"files": files, "file_count": len(files)}

    def _build_ai_context_prompt(
        self, folder_info: FolderInfo, profile: CodebaseProfile, contents: dict
    ) -> str:
        """Build prompt for AI-CONTEXT.md generation."""
        return f"""Generate AI assistant context documentation for a code module.

Project: {profile.name}
Primary Language: {profile.primary_language}
Module Path: {folder_info.relative_path}
Files: {contents['file_count']}

Module Files:
{self._format_file_list(contents['files'])}

Generate structured documentation with these sections:

1. Purpose (2-3 sentences)
2. Key Files (list each file with brief purpose)
3. Coding Conventions (naming, patterns, error handling specific to this module)
4. Common Patterns (with actual code examples from the files)
5. Testing Approach (where tests are, how to run)
6. Integration Points (what it imports, what uses it)

Be specific and use actual examples from the code. Focus on conventions an AI assistant should follow when editing this module.
"""

    def _build_readme_prompt(
        self, folder_info: FolderInfo, profile: CodebaseProfile, contents: dict
    ) -> str:
        """Build prompt for README.md generation."""
        return f"""Generate a developer-friendly README for a code module.

Project: {profile.name}
Module Path: {folder_info.relative_path}
Files: {contents['file_count']}

Module Files:
{self._format_file_list(contents['files'])}

Generate concise documentation with these sections:

1. Overview (what this module does, 2-3 paragraphs)
2. Key Components (bullet list of main components/classes)
3. Usage Examples (1-2 practical code examples)
4. Related Documentation (links to related modules)

Keep it practical and actionable for developers.
"""

    def _format_file_list(self, files: list[dict]) -> str:
        """Format file list for prompt."""
        lines = []
        for file in files[:10]:  # Limit to first 10 files
            lines.append(f"- {file['name']}")
            if file["preview"]:
                # Show first few lines
                preview_lines = file["preview"].split("\n")[:5]
                for line in preview_lines:
                    lines.append(f"  {line}")
        return "\n".join(lines)

    def _wrap_ai_context_template(self, folder_name: str, content: str) -> str:
        """Wrap generated content in AI-CONTEXT.md template."""
        return f"""# {folder_name} - AI Context

<!-- AUTO-GENERATED: Purpose - DO NOT EDIT -->
{self._extract_section(content, "Purpose") or "## Purpose\n\nModule purpose goes here."}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Key Files - DO NOT EDIT -->
{self._extract_section(content, "Key Files") or "## Key Files\n\n- file.py - Description"}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Coding Conventions - DO NOT EDIT -->
{self._extract_section(content, "Coding Conventions") or "## Coding Conventions\n\nConventions go here."}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Common Patterns - DO NOT EDIT -->
{self._extract_section(content, "Common Patterns") or "## Common Patterns\n\nPatterns go here."}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Testing Approach - DO NOT EDIT -->
{self._extract_section(content, "Testing Approach") or "## Testing Approach\n\nTesting info goes here."}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Integration Points - DO NOT EDIT -->
{self._extract_section(content, "Integration Points") or "## Integration Points\n\nIntegration info goes here."}
<!-- END AUTO-GENERATED -->

<!-- CUSTOM SECTION: You can add notes below -->
## Additional Notes

<!-- END CUSTOM SECTION -->
"""

    def _wrap_readme_template(self, folder_name: str, content: str) -> str:
        """Wrap generated content in README.md template."""
        return f"""# {folder_name}

<!-- AUTO-GENERATED: Overview - DO NOT EDIT -->
{self._extract_section(content, "Overview") or "## Overview\n\nModule overview goes here."}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Key Components - DO NOT EDIT -->
{self._extract_section(content, "Key Components") or "## Key Components\n\n- Component 1"}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Usage Examples - DO NOT EDIT -->
{self._extract_section(content, "Usage Examples") or "## Usage Examples\n\nExamples go here."}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Related Documentation - DO NOT EDIT -->
{self._extract_section(content, "Related Documentation") or "## Related Documentation\n\n- [Parent Module](../README.md)"}
<!-- END AUTO-GENERATED -->

<!-- CUSTOM SECTION: You can add notes below -->
## Additional Information

<!-- END CUSTOM SECTION -->
"""

    def _extract_section(self, content: str, section_name: str) -> str:
        """Extract a section from generated content."""
        # Simple section extraction - look for ## {section_name}
        lines = content.split("\n")
        section_lines = []
        in_section = False

        for line in lines:
            if line.strip().startswith(f"## {section_name}"):
                in_section = True
                section_lines.append(line)
            elif in_section and line.strip().startswith("##"):
                break
            elif in_section:
                section_lines.append(line)

        return "\n".join(section_lines) if section_lines else ""
```

**Step 4: Run test to verify it passes**

Run: `cd DevMind-AI && poetry run pytest tests/agents/project_documenter/test_per_folder_generator.py -v`

Expected: PASS

**Step 5: Commit**

```bash
cd DevMind-AI
git add src/agents/project_documenter/per_folder_generator.py tests/agents/project_documenter/test_per_folder_generator.py
git commit -m "feat(docs): add PerFolderGenerator for AI-CONTEXT and README

- Generate AI-CONTEXT.md with conventions and patterns
- Generate README.md with overview and examples
- Use LLM for intelligent content generation
- Extract sections and wrap in marker templates"
```

---

## Task 5: Integrate Components into ProjectDocumenterAgent

**Files:**
- Modify: `DevMind-AI/src/agents/project_documenter/agent.py`

**Step 1: Add imports and initialize new components**

In `agent.py`, add imports:
```python
from .folder_analyzer import FolderAnalyzer
from .per_folder_generator import PerFolderGenerator
from .smart_merger import SmartMerger
from .metadata_manager import MetadataManager
```

In `__init__` method, initialize components:
```python
def __init__(self, router: LLMRouter | None = None):
    super().__init__(router)
    self.analyzer = CodebaseAnalyzer()

    # NEW: Per-folder components
    self.folder_analyzer = FolderAnalyzer()
    self.per_folder_generator = PerFolderGenerator(self.llm_client)
    self.smart_merger = SmartMerger()
    self.metadata_manager = MetadataManager()

    # Existing generators...
    self._generators = {...}
```

**Step 2: Add per-folder generation to execute method**

In `execute` method, after existing top-level doc generation, add:
```python
async def execute(self, context: AgentContext, **kwargs) -> dict:
    # ... existing code for profile analysis ...

    # ... existing code for top-level doc generation ...

    # NEW: Generate per-folder docs
    folder_docs = []
    if kwargs.get("per_folder_docs", True):
        # Initialize metadata manager
        self.metadata_manager.initialize(project_path)

        # Analyze folders
        folders = self.folder_analyzer.analyze_folders(project_path)

        # Filter for incremental mode
        if kwargs.get("incremental", False):
            folders = [
                f for f in folders if self.metadata_manager.has_folder_changed(f.path)
            ]

        # Generate docs for each folder
        for folder_info in folders:
            try:
                # Generate AI-CONTEXT.md
                ai_context = await self.per_folder_generator.generate_ai_context(
                    folder_info, profile
                )

                # Smart merge if exists
                ai_context_path = folder_info.path / "AI-CONTEXT.md"
                if ai_context_path.exists():
                    existing_content = ai_context_path.read_text()
                    ai_context.content = self.smart_merger.merge(
                        existing_content, ai_context.content
                    )

                folder_docs.append(ai_context)

                # Generate README.md
                readme = await self.per_folder_generator.generate_readme(
                    folder_info, profile
                )

                # Smart merge if exists
                readme_path = folder_info.path / "README.md"
                if readme_path.exists():
                    existing_content = readme_path.read_text()
                    readme.content = self.smart_merger.merge(
                        existing_content, readme.content
                    )

                folder_docs.append(readme)

                # Update metadata
                if kwargs.get("write_files", False):
                    self.metadata_manager.update_folder(
                        folder_info.path, folder_info.file_count
                    )

            except Exception as e:
                # Log error but continue
                folder_docs.append(
                    GeneratedDoc(
                        path=f"error_{folder_info.relative_path}.txt",
                        content=f"Error generating docs: {str(e)}",
                        format_name="per_folder",
                        description=f"Error for {folder_info.relative_path}",
                    )
                )

        generated_docs.extend(folder_docs)

        # Mark full run complete
        if not kwargs.get("incremental", False):
            self.metadata_manager.mark_full_run()

    # ... existing code for writing files ...

    return {
        "success": True,
        "profile": profile_dict,
        "generated_docs": doc_list,
        "folder_docs_count": len(folder_docs),  # NEW
        "written_files": written_files,
    }
```

**Step 3: Test integration**

Run: `cd DevMind-AI && poetry run pytest tests/agents/project_documenter/test_agent.py -v`

Expected: Existing tests should still pass

**Step 4: Commit**

```bash
cd DevMind-AI
git add src/agents/project_documenter/agent.py
git commit -m "feat(docs): integrate per-folder generation into agent

- Initialize folder analyzer, generator, merger, metadata manager
- Generate AI-CONTEXT.md and README.md for each code folder
- Support incremental mode with change detection
- Smart merge to preserve custom content"
```

---

## Task 6: Add CLI Options for Per-Folder Documentation

**Files:**
- Modify: `DevMind-AI/src/cli/commands/document.py`

**Step 1: Add CLI arguments**

In `document_command` function, add new options:
```python
def document_command(
    path: Path = typer.Argument(...),
    formats: Optional[List[str]] = typer.Option(None, "--format", "-f"),
    write: bool = typer.Option(False, "--write", "-w"),
    # ... existing options ...

    # NEW: Per-folder options
    per_folder: bool = typer.Option(
        True,
        "--per-folder/--no-per-folder",
        help="Generate per-folder documentation (AI-CONTEXT.md + README.md)",
    ),
    incremental: bool = typer.Option(
        False,
        "--incremental",
        help="Only regenerate changed folders (based on content hash)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Force regenerate all folders (ignore metadata)",
    ),
):
    """
    Generate AI-agent documentation for a project.

    NEW: Per-folder documentation generates AI-CONTEXT.md and README.md
    in each code folder for better AI assistant context.

    Examples:
        # Full generation with per-folder docs
        devmind document ./project -w

        # Skip per-folder docs
        devmind document ./project -w --no-per-folder

        # Incremental: only regenerate changed folders
        devmind document ./project -w --incremental

        # Force regenerate everything
        devmind document ./project -w --force
    """
    asyncio.run(
        run_document(
            path=path,
            formats=selected_formats,
            output_dir=output_dir,
            write_files=write,
            output_to_project=to_project,
            analyze_only=analyze,
            format_output=format_output,
            per_folder_docs=per_folder,  # NEW
            incremental=incremental and not force,  # NEW
        )
    )
```

**Step 2: Update run_document to pass options**

In `run_document` async function:
```python
async def run_document(
    path: Path,
    formats: List[str],
    output_dir: Optional[Path],
    write_files: bool,
    output_to_project: bool,
    analyze_only: bool,
    format_output: str,
    per_folder_docs: bool = True,  # NEW
    incremental: bool = False,  # NEW
):
    # ... existing code ...

    result = await agent.execute(
        context,
        path=str(path),
        formats=formats,
        write_files=write_files,
        output_to_project=output_to_project,
        output_dir=str(output_dir) if output_dir else None,
        per_folder_docs=per_folder_docs,  # NEW
        incremental=incremental,  # NEW
    )

    # ... existing code ...
```

**Step 3: Test CLI**

Run: `cd DevMind-AI && poetry run devmind document --help`

Expected: Should show new options

**Step 4: Commit**

```bash
cd DevMind-AI
git add src/cli/commands/document.py
git commit -m "feat(cli): add per-folder documentation CLI options

- Add --per-folder/--no-per-folder flag
- Add --incremental flag for changed folders only
- Add --force flag to regenerate all
- Update help text with examples"
```

---

## Task 7: End-to-End Test on Sample Project

**Files:**
- Create: `DevMind-AI/tests/agents/project_documenter/test_e2e_per_folder.py`

**Step 1: Create end-to-end test**

```python
"""End-to-end test for per-folder documentation generation."""

from pathlib import Path
import pytest
from src.agents.project_documenter import ProjectDocumenterAgent
from src.agents.base import AgentContext


@pytest.mark.asyncio
async def test_e2e_per_folder_generation(tmp_path):
    """Test full per-folder documentation generation workflow."""
    # Create test project structure
    project = tmp_path / "test_project"
    project.mkdir()

    (project / "src").mkdir()
    (project / "src" / "core").mkdir()
    (project / "src" / "core" / "__init__.py").write_text("")
    (project / "src" / "core" / "utils.py").write_text(
        """
def helper_function():
    '''A helper function.'''
    return True
"""
    )

    (project / "src" / "api").mkdir()
    (project / "src" / "api" / "main.py").write_text(
        """
def api_handler():
    '''API handler.'''
    pass
"""
    )

    # Run agent
    agent = ProjectDocumenterAgent()
    context = AgentContext()

    result = await agent.execute(
        context,
        path=str(project),
        formats=["claude"],
        write_files=True,
        per_folder_docs=True,
        output_to_project=True,
    )

    assert result["success"] is True
    assert result["folder_docs_count"] > 0

    # Verify files were created
    assert (project / "src" / "core" / "AI-CONTEXT.md").exists()
    assert (project / "src" / "core" / "README.md").exists()
    assert (project / "src" / "api" / "AI-CONTEXT.md").exists()
    assert (project / "src" / "api" / "README.md").exists()

    # Verify content has markers
    ai_context_content = (project / "src" / "core" / "AI-CONTEXT.md").read_text()
    assert "AUTO-GENERATED" in ai_context_content
    assert "CUSTOM SECTION" in ai_context_content


@pytest.mark.asyncio
async def test_e2e_incremental_regeneration(tmp_path):
    """Test incremental regeneration only updates changed folders."""
    project = tmp_path / "test_project"
    project.mkdir()

    (project / "src").mkdir()
    (project / "src" / "module.py").write_text("def func(): pass")

    agent = ProjectDocumenterAgent()
    context = AgentContext()

    # First run
    result1 = await agent.execute(
        context,
        path=str(project),
        formats=["claude"],
        write_files=True,
        per_folder_docs=True,
        output_to_project=True,
    )

    folder_count_1 = result1["folder_docs_count"]

    # Second run without changes (incremental)
    result2 = await agent.execute(
        context,
        path=str(project),
        formats=["claude"],
        write_files=True,
        per_folder_docs=True,
        output_to_project=True,
        incremental=True,
    )

    # Should regenerate 0 folders (nothing changed)
    assert result2["folder_docs_count"] == 0

    # Modify file
    (project / "src" / "module.py").write_text("def func(): return True")

    # Third run with changes (incremental)
    result3 = await agent.execute(
        context,
        path=str(project),
        formats=["claude"],
        write_files=True,
        per_folder_docs=True,
        output_to_project=True,
        incremental=True,
    )

    # Should regenerate changed folder
    assert result3["folder_docs_count"] > 0
```

**Step 2: Run test**

Run: `cd DevMind-AI && poetry run pytest tests/agents/project_documenter/test_e2e_per_folder.py -v`

Expected: PASS

**Step 3: Commit**

```bash
cd DevMind-AI
git add tests/agents/project_documenter/test_e2e_per_folder.py
git commit -m "test(docs): add end-to-end tests for per-folder generation

- Test full workflow from analysis to file writing
- Test incremental regeneration with change detection
- Verify AI-CONTEXT.md and README.md creation
- Verify marker preservation"
```

---

## Task 8: Create DevMind Skill for Per-Folder Documentation

**Files:**
- Create: `DevMind-AI/.devmind/skills/per-folder-docs.md`

**Step 1: Write the skill document**

```markdown
---
name: per-folder-docs
description: Generate per-folder AI-CONTEXT.md and README.md documentation for better AI assistant context
tags: [documentation, ai-context, skills]
---

# Per-Folder Documentation Skill

## Purpose

Generate detailed per-folder documentation (AI-CONTEXT.md + README.md) for any codebase to give AI assistants (Claude, Copilot, Gemini) better context when working in specific modules.

## When to Use

- Setting up a new project for AI assistant work
- After major refactoring (regenerate affected folders)
- When onboarding AI assistants to specific modules
- Adding new features in isolated folders

## How It Works

**Components**:
1. **FolderAnalyzer** - Identifies code folders to document
2. **PerFolderGenerator** - Uses LLM to generate AI-CONTEXT.md and README.md
3. **SmartMerger** - Preserves custom edits during regeneration
4. **MetadataManager** - Tracks changes for incremental updates

**Generated Files**:
- `AI-CONTEXT.md` - AI-specific conventions, patterns, testing
- `README.md` - Human-friendly overview, components, examples

## Usage

### Full Generation

```bash
# Generate docs for all code folders
poetry run devmind document /path/to/project -w

# Generate and write directly to project
poetry run devmind document /path/to/project -w --to-project
```

### Incremental Updates

```bash
# Only regenerate changed folders
poetry run devmind document /path/to/project -w --incremental

# Force regenerate everything
poetry run devmind document /path/to/project -w --force
```

### Selective Generation

```bash
# Skip per-folder docs (only top-level)
poetry run devmind document /path/to/project -w --no-per-folder

# Specific formats
poetry run devmind document /path/to/project -w -f claude -f copilot
```

## For AI Assistants

When working in a codebase with per-folder docs:

1. **Check for AI-CONTEXT.md** in current folder before editing
2. **Follow conventions** specified in AI-CONTEXT.md
3. **Use patterns** from Common Patterns section
4. **Preserve custom sections** when regenerating (marked with `<!-- CUSTOM SECTION -->`)

### Example: Using Context

```python
# Before editing src/agents/code_reviewer/analyzer.py
# Read: src/agents/code_reviewer/AI-CONTEXT.md

# Learn:
# - Naming conventions (e.g., "Use snake_case for functions")
# - Error handling patterns
# - Testing approach
# - Integration points

# Then make changes following learned conventions
```

## Customizing Generated Docs

### Adding Custom Content

Edit any generated file and add content in CUSTOM SECTION blocks:

```markdown
<!-- CUSTOM SECTION: Team notes -->
## Team Guidelines

Our team prefers:
- Use type hints
- Write docstrings for public functions
- Keep functions under 50 lines

<!-- END CUSTOM SECTION -->
```

Custom content is **preserved** across regenerations.

### Regenerating with Preservation

```bash
# Smart merge keeps your custom sections
poetry run devmind document /path/to/project -w --incremental
```

## File Structure

After generation:

```
project/
├── CLAUDE.md                    (enhanced with module index)
├── README.md                    (enhanced with folder tree)
├── .devmind/
│   └── doc-metadata.json        (change tracking)
├── src/
│   ├── AI-CONTEXT.md           (NEW)
│   ├── README.md               (NEW)
│   ├── agents/
│   │   ├── AI-CONTEXT.md      (NEW)
│   │   ├── README.md          (NEW)
│   │   └── code_reviewer/
│   │       ├── AI-CONTEXT.md  (NEW)
│   │       └── README.md      (NEW)
│   └── api/
│       ├── AI-CONTEXT.md      (NEW)
│       └── README.md          (NEW)
```

## Implementation Details

**Location**: `src/agents/project_documenter/`

**Key Classes**:
- `FolderAnalyzer` - `folder_analyzer.py`
- `PerFolderGenerator` - `per_folder_generator.py`
- `SmartMerger` - `smart_merger.py`
- `MetadataManager` - `metadata_manager.py`

**Tests**: `tests/agents/project_documenter/test_*.py`

## Troubleshooting

**Issue**: Folders excluded that shouldn't be

**Solution**: Check `FolderAnalyzer.EXCLUDED_PATTERNS` - may need to adjust

**Issue**: Custom content lost during regeneration

**Solution**: Ensure content is in `<!-- CUSTOM SECTION -->` blocks

**Issue**: Incremental mode not detecting changes

**Solution**: Check `.devmind/doc-metadata.json` - may need to delete and regenerate

## Related

- Design Doc: `docs/plans/2026-02-02-per-folder-documentation-design.md`
- Implementation Plan: `docs/plans/2026-02-02-per-folder-docs-implementation.md`
- Project Documenter Agent: `src/agents/project_documenter/agent.py`
```

**Step 2: Test the skill**

Run: `cd DevMind-AI && poetry run devmind document . --help`

Expected: Help text shows new options

**Step 3: Commit**

```bash
cd DevMind-AI
git add .devmind/skills/per-folder-docs.md
git commit -m "docs: add per-folder-docs skill documentation

- Document usage for AI assistants
- Include examples and troubleshooting
- Explain file structure and customization
- Add to DevMind skills collection"
```

---

## Task 9: Update Project Documentation

**Files:**
- Modify: `DevMind-AI/README.md`
- Modify: `DevMind-AI/CLAUDE.md`
- Create: `DevMind-AI/src/agents/project_documenter/README.md`

**Step 1: Update main README**

Add to "Available Agents" section:
```markdown
### Project Documenter Agent

Generates AI-optimized documentation for any codebase:

**Features**:
- **Per-Folder Docs**: AI-CONTEXT.md and README.md in every code folder
- **Smart Preservation**: Custom edits preserved during regeneration
- **Incremental Updates**: Only regenerate changed folders
- **Multi-Format**: Claude, Copilot, Cursor, Gemini, Windsurf, Aider, Cline

**Usage**:
```bash
# Full generation with per-folder docs
poetry run devmind document /path/to/project -w

# Incremental regeneration
poetry run devmind document /path/to/project -w --incremental
```

See [Per-Folder Docs Skill](.devmind/skills/per-folder-docs.md) for details.
```

**Step 2: Update CLAUDE.md**

Add to "Available Agents" section:
```markdown
## Project Documenter Agent

**Command**: `poetry run devmind document`

**New Feature**: Per-folder documentation generation

Generates:
- `AI-CONTEXT.md` in each code folder (conventions, patterns, testing)
- `README.md` in each code folder (overview, examples)
- Smart merge preserves custom edits
- Incremental mode for fast updates

**When editing**:
1. Read `AI-CONTEXT.md` in current folder
2. Follow conventions and patterns
3. Preserve `<!-- CUSTOM SECTION -->` blocks

**Key Files**:
- `src/agents/project_documenter/agent.py` - Main agent
- `src/agents/project_documenter/folder_analyzer.py` - Folder detection
- `src/agents/project_documenter/per_folder_generator.py` - Content generation
- `src/agents/project_documenter/smart_merger.py` - Preservation logic
```

**Step 3: Create agent-specific README**

Create `DevMind-AI/src/agents/project_documenter/README.md`:
```markdown
# Project Documenter Agent

Generates AI-optimized documentation for existing codebases.

## Overview

This agent analyzes any project and generates documentation in multiple formats for AI coding assistants (Claude, Copilot, Cursor, Gemini, etc.) and human developers.

**New**: Per-folder documentation generation with AI-CONTEXT.md and README.md in every code folder.

## Components

- **CodebaseAnalyzer** - Analyzes project structure and conventions
- **FolderAnalyzer** - Identifies folders needing documentation
- **PerFolderGenerator** - Generates AI-CONTEXT.md and README.md with LLM
- **SmartMerger** - Preserves custom content during regeneration
- **MetadataManager** - Tracks changes for incremental updates
- **IndexBuilder** - Creates navigation index in top-level docs
- **Format Generators** - Claude, Copilot, Cursor, Gemini, etc.

## Usage

### Basic Generation

\`\`\`bash
# Analyze and generate all formats
poetry run devmind document /path/to/project -w

# Generate specific formats
poetry run devmind document /path/to/project -w -f claude -f copilot

# Write directly to project
poetry run devmind document /path/to/project -w --to-project
\`\`\`

### Per-Folder Documentation

\`\`\`bash
# Generate with per-folder docs (default)
poetry run devmind document /path/to/project -w

# Skip per-folder docs
poetry run devmind document /path/to/project -w --no-per-folder

# Incremental: only regenerate changed folders
poetry run devmind document /path/to/project -w --incremental

# Force regenerate all
poetry run devmind document /path/to/project -w --force
\`\`\`

## File Structure

\`\`\`
DevMind-AI/src/agents/project_documenter/
├── agent.py                    # Main ProjectDocumenterAgent
├── analyzer.py                 # Codebase analysis
├── folder_analyzer.py          # Folder identification
├── per_folder_generator.py     # Per-folder content generation
├── smart_merger.py             # Content preservation
├── metadata_manager.py         # Change tracking
├── output_manager.py           # Output organization
└── generators/
    ├── base.py                 # GeneratedDoc dataclass
    ├── claude.py               # Claude Code format
    ├── copilot.py              # GitHub Copilot format
    ├── cursor.py               # Cursor AI format
    ├── gemini.py               # Google Gemini format
    └── ...                     # Other formats
\`\`\`

## Testing

\`\`\`bash
# Run all tests
poetry run pytest tests/agents/project_documenter/ -v

# Run specific test
poetry run pytest tests/agents/project_documenter/test_folder_analyzer.py -v

# End-to-end test
poetry run pytest tests/agents/project_documenter/test_e2e_per_folder.py -v
\`\`\`

## Related Documentation

- [Design Doc](../../../docs/plans/2026-02-02-per-folder-documentation-design.md)
- [Implementation Plan](../../../docs/plans/2026-02-02-per-folder-docs-implementation.md)
- [Per-Folder Docs Skill](../../../.devmind/skills/per-folder-docs.md)
```

**Step 4: Commit**

```bash
cd DevMind-AI
git add README.md CLAUDE.md src/agents/project_documenter/README.md
git commit -m "docs: update project documentation for per-folder feature

- Add per-folder docs to main README
- Update CLAUDE.md with usage for AI assistants
- Create detailed README for project_documenter agent
- Include examples and file structure"
```

---

## Success Criteria

✅ **All tests pass**:
```bash
cd DevMind-AI && poetry run pytest tests/agents/project_documenter/ -v
```

✅ **CLI works**:
```bash
cd DevMind-AI && poetry run devmind document . -w --per-folder
```

✅ **Files generated**:
- `AI-CONTEXT.md` in code folders
- `README.md` in code folders
- `.devmind/doc-metadata.json` created

✅ **Smart merge works**:
- Custom sections preserved
- Auto-generated sections updated

✅ **Incremental mode works**:
- Only changed folders regenerated
- Unchanged folders skipped

---

## Plan Complete

**Plan saved to**: `docs/plans/2026-02-02-per-folder-docs-implementation.md`

**Total Tasks**: 9 (Foundation → Integration → Testing → Documentation)

**Estimated Time**: 3-4 hours for experienced developer

**Next Steps**: Use @superpowers:executing-plans or @superpowers:subagent-driven-development to implement
