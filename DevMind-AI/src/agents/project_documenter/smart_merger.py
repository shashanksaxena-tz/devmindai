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
                content_lines = section_lines[1:-1] if len(section_lines) > 2 else []
                section_content = "\n".join(content_lines)

                sections.append(
                    Section(
                        section_type=SectionType.AUTO_GENERATED,
                        name=section_name,
                        content=section_content,
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
                content_lines = section_lines[1:-1] if len(section_lines) > 2 else []
                section_content = "\n".join(content_lines)

                sections.append(
                    Section(
                        section_type=SectionType.CUSTOM,
                        name=section_name,
                        content=section_content,
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

    def has_markers(self, content: str) -> bool:
        """Check if content has any markers.

        Args:
            content: File content to check

        Returns:
            True if content has AUTO-GENERATED or CUSTOM markers
        """
        return bool(
            self.AUTO_START_PATTERN.search(content)
            or self.CUSTOM_START_PATTERN.search(content)
        )

    def extract_custom_sections(self, content: str) -> Dict[str, str]:
        """Extract all custom sections from content.

        Args:
            content: File content

        Returns:
            Dictionary mapping section names to their content
        """
        sections = self._parse_sections(content)
        return {
            s.name: s.content
            for s in sections
            if s.section_type == SectionType.CUSTOM
        }
