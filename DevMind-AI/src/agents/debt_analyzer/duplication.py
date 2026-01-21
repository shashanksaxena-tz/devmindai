"""Code duplication detection."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DuplicateBlock:
    """A block of duplicated code."""
    content_hash: str
    lines: int
    occurrences: list[dict] = field(default_factory=list)  # [{file, start_line, end_line}]

    @property
    def total_duplicated_lines(self) -> int:
        return self.lines * (len(self.occurrences) - 1)


@dataclass
class DuplicationReport:
    """Report of code duplication."""
    duplicate_blocks: list[DuplicateBlock] = field(default_factory=list)
    total_lines: int = 0
    duplicated_lines: int = 0

    @property
    def duplication_percentage(self) -> float:
        if self.total_lines == 0:
            return 0.0
        return (self.duplicated_lines / self.total_lines) * 100


class DuplicationDetector:
    """Detects code duplication using content hashing."""

    def __init__(self, min_lines: int = 5, min_tokens: int = 50):
        self.min_lines = min_lines
        self.min_tokens = min_tokens

    def detect(self, files: dict[str, str]) -> DuplicationReport:
        """Detect duplication across multiple files."""
        # Extract code blocks
        blocks: dict[str, list[dict]] = {}  # hash -> occurrences

        for file_path, content in files.items():
            lines = content.splitlines()
            for i in range(len(lines) - self.min_lines + 1):
                block = "\n".join(lines[i:i + self.min_lines])
                normalized = self._normalize(block)

                # Check tokens on the original block to avoid aggressive normalization issues
                if len(block.split()) < self.min_tokens:
                    continue

                block_hash = hashlib.md5(normalized.encode()).hexdigest()

                if block_hash not in blocks:
                    blocks[block_hash] = []

                # Optimization: check if we just added an overlapping block for the same file?
                # The current implementation checks every sliding window.
                # If we have lines 1-5, then 2-6, they will overlap.
                # But simple hashing is usually fine for a first pass, though it might report many overlapping blocks.
                # The plan implementation is basic. I'll stick to it.

                blocks[block_hash].append({
                    "file": file_path,
                    "start_line": i + 1,
                    "end_line": i + self.min_lines,
                })

        # Build report
        duplicates = []
        for block_hash, occurrences in blocks.items():
            if len(occurrences) > 1:
                duplicates.append(DuplicateBlock(
                    content_hash=block_hash,
                    lines=self.min_lines,
                    occurrences=occurrences,
                ))

        # Filter out subsets?
        # The current implementation doesn't handle overlapping blocks well (it counts them all independently).
        # But per the plan, I implement it as is.

        total_lines = sum(len(c.splitlines()) for c in files.values())
        duplicated_lines = sum(d.total_duplicated_lines for d in duplicates)

        # Cap duplicated lines at total lines - unique lines?
        # Or just sum. The formula might produce > 100% if overlaps are counted multiple times.
        # But let's stick to the plan.

        return DuplicationReport(
            duplicate_blocks=duplicates,
            total_lines=total_lines,
            duplicated_lines=duplicated_lines,
        )

    def _normalize(self, code: str) -> str:
        """Normalize code for comparison."""
        # Remove whitespace variations
        lines = [line.strip().replace(" ", "") for line in code.splitlines()]
        return "\n".join(line for line in lines if line)
