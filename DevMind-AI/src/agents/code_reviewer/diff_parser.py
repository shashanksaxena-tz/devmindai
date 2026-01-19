# src/agents/code_reviewer/diff_parser.py
"""Parse unified diff format from Git/GitHub."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ChangeType(Enum):
    """Type of file change in diff."""
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


@dataclass
class HunkChange:
    """Represents a single change hunk in a diff."""
    old_start: int
    old_lines: int
    new_start: int
    new_lines: int
    content: str
    added_lines: list[tuple[int, str]] = field(default_factory=list)
    removed_lines: list[tuple[int, str]] = field(default_factory=list)


@dataclass
class FileDiff:
    """Represents changes to a single file."""
    path: str
    change_type: ChangeType
    old_path: Optional[str] = None
    hunks: list[HunkChange] = field(default_factory=list)
    additions: int = 0
    deletions: int = 0
    is_binary: bool = False
    language: Optional[str] = None

    @property
    def total_changes(self) -> int:
        return self.additions + self.deletions


@dataclass
class DiffResult:
    """Complete diff parsing result."""
    files: list[FileDiff] = field(default_factory=list)

    @property
    def total_additions(self) -> int:
        return sum(f.additions for f in self.files)

    @property
    def total_deletions(self) -> int:
        return sum(f.deletions for f in self.files)

    @property
    def files_changed(self) -> int:
        return len(self.files)


class DiffParser:
    """Parser for unified diff format."""

    # Regex patterns
    FILE_HEADER_PATTERN = re.compile(r'^diff --git a/(.+) b/(.+)$')
    NEW_FILE_PATTERN = re.compile(r'^new file mode')
    DELETED_FILE_PATTERN = re.compile(r'^deleted file mode')
    RENAME_FROM_PATTERN = re.compile(r'^rename from (.+)$')
    RENAME_TO_PATTERN = re.compile(r'^rename to (.+)$')
    BINARY_PATTERN = re.compile(r'^Binary files')
    HUNK_HEADER_PATTERN = re.compile(
        r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@'
    )
    INDEX_PATTERN = re.compile(r'^index ([a-f0-9]+)\.\.([a-f0-9]+)')

    # Language detection by extension
    LANGUAGE_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.jsx': 'javascript',
        '.java': 'java',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.cs': 'csharp',
        '.cpp': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.hpp': 'cpp',
        '.sql': 'sql',
        '.md': 'markdown',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
    }

    def parse(self, diff_text: str) -> DiffResult:
        """Parse unified diff text into structured result."""
        result = DiffResult()
        lines = diff_text.split('\n')
        current_file: Optional[FileDiff] = None
        current_hunk: Optional[HunkChange] = None
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check for new file header
            file_match = self.FILE_HEADER_PATTERN.match(line)
            if file_match:
                # Save previous file if exists
                if current_file:
                    if current_hunk:
                        current_file.hunks.append(current_hunk)
                    result.files.append(current_file)

                # Start new file
                old_path, new_path = file_match.groups()
                current_file = FileDiff(
                    path=new_path,
                    change_type=ChangeType.MODIFIED,
                )
                current_hunk = None

                # Look ahead for file metadata
                i = self._parse_file_metadata(
                    lines, i + 1, current_file, old_path
                )
                continue

            # Check for hunk header
            hunk_match = self.HUNK_HEADER_PATTERN.match(line)
            if hunk_match and current_file:
                if current_hunk:
                    current_file.hunks.append(current_hunk)

                old_start = int(hunk_match.group(1))
                old_lines = int(hunk_match.group(2) or 1)
                new_start = int(hunk_match.group(3))
                new_lines = int(hunk_match.group(4) or 1)

                current_hunk = HunkChange(
                    old_start=old_start,
                    old_lines=old_lines,
                    new_start=new_start,
                    new_lines=new_lines,
                    content=line,
                )
                i += 1
                continue

            # Parse hunk content
            if current_hunk and current_file:
                if line.startswith('+') and not line.startswith('+++'):
                    current_file.additions += 1
                    line_num = current_hunk.new_start + len(
                        current_hunk.added_lines
                    )
                    current_hunk.added_lines.append((line_num, line[1:]))
                elif line.startswith('-') and not line.startswith('---'):
                    current_file.deletions += 1
                    line_num = current_hunk.old_start + len(
                        current_hunk.removed_lines
                    )
                    current_hunk.removed_lines.append((line_num, line[1:]))

            i += 1

        # Don't forget the last file
        if current_file:
            if current_hunk:
                current_file.hunks.append(current_hunk)
            result.files.append(current_file)

        # Detect languages
        for file_diff in result.files:
            file_diff.language = self._detect_language(file_diff.path)

        return result

    def _parse_file_metadata(
        self,
        lines: list[str],
        start_idx: int,
        file_diff: FileDiff,
        old_path: str,
    ) -> int:
        """Parse file metadata (new/deleted/renamed/binary)."""
        i = start_idx
        while i < len(lines):
            line = lines[i]

            if self.NEW_FILE_PATTERN.match(line):
                file_diff.change_type = ChangeType.ADDED
            elif self.DELETED_FILE_PATTERN.match(line):
                file_diff.change_type = ChangeType.DELETED
            elif self.BINARY_PATTERN.match(line):
                file_diff.is_binary = True
            elif rename_from := self.RENAME_FROM_PATTERN.match(line):
                file_diff.change_type = ChangeType.RENAMED
                file_diff.old_path = rename_from.group(1)
            elif rename_to := self.RENAME_TO_PATTERN.match(line):
                file_diff.path = rename_to.group(1)
            elif line.startswith('diff --git') or line.startswith('@@'):
                # Next file or hunk, stop parsing metadata
                return i
            elif line.startswith('---') or line.startswith('+++'):
                pass  # Skip these lines
            elif self.INDEX_PATTERN.match(line):
                pass  # Skip index line

            i += 1

        return i

    def _detect_language(self, file_path: str) -> Optional[str]:
        """Detect programming language from file extension."""
        for ext, lang in self.LANGUAGE_MAP.items():
            if file_path.endswith(ext):
                return lang
        return None


def parse_unified_diff(diff_text: str) -> DiffResult:
    """Convenience function to parse unified diff."""
    return DiffParser().parse(diff_text)
