"""Index builder for top-level documentation navigation."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List

from .folder_analyzer import FolderInfo


class IndexBuilder:
    """Builds navigation indexes for top-level documentation files."""

    # Marker patterns for finding/replacing index sections
    MODULE_INDEX_PATTERN = re.compile(
        r"<!-- AUTO-GENERATED: Documentation Index -->.*?<!-- END AUTO-GENERATED -->",
        re.DOTALL
    )
    FOLDER_STRUCTURE_PATTERN = re.compile(
        r"<!-- AUTO-GENERATED: Folder Structure -->.*?<!-- END AUTO-GENERATED -->",
        re.DOTALL
    )

    def add_module_index(
        self, content: str, folders: List[FolderInfo], link_to: str = "AI-CONTEXT.md"
    ) -> str:
        """Add or update module index section in documentation.

        Args:
            content: Existing documentation content
            folders: List of documented folders
            link_to: Filename to link to (AI-CONTEXT.md or README.md)

        Returns:
            Content with updated module index
        """
        index_section = self._build_module_index(folders, link_to)

        # Check if index already exists
        if self.MODULE_INDEX_PATTERN.search(content):
            # Replace existing
            return self.MODULE_INDEX_PATTERN.sub(index_section, content)
        else:
            # Find a good insertion point
            insertion_point = self._find_insertion_point(content)
            if insertion_point >= 0:
                return content[:insertion_point] + "\n\n" + index_section + "\n" + content[insertion_point:]
            else:
                # Append at end
                return content.rstrip() + "\n\n" + index_section + "\n"

    def add_folder_structure(
        self, content: str, folders: List[FolderInfo], link_to: str = "README.md"
    ) -> str:
        """Add or update folder structure section in documentation.

        Args:
            content: Existing README content
            folders: List of documented folders
            link_to: Filename to link to

        Returns:
            Content with updated folder structure
        """
        structure_section = self._build_folder_structure(folders, link_to)

        # Check if structure already exists
        if self.FOLDER_STRUCTURE_PATTERN.search(content):
            # Replace existing
            return self.FOLDER_STRUCTURE_PATTERN.sub(structure_section, content)
        else:
            # Find a good insertion point
            insertion_point = self._find_insertion_point(content)
            if insertion_point >= 0:
                return content[:insertion_point] + "\n\n" + structure_section + "\n" + content[insertion_point:]
            else:
                # Append at end
                return content.rstrip() + "\n\n" + structure_section + "\n"

    def _build_module_index(self, folders: List[FolderInfo], link_to: str) -> str:
        """Build the module index section."""
        lines = [
            "<!-- AUTO-GENERATED: Documentation Index -->",
            "## 📚 Module Documentation",
            "",
        ]

        # Group folders by top-level directory
        grouped = self._group_folders_by_toplevel(folders)

        for group_name, group_folders in sorted(grouped.items()):
            lines.append(f"### {group_name.title()}")
            for folder in sorted(group_folders, key=lambda f: str(f.relative_path)):
                rel_path = str(folder.relative_path)
                description = self._get_folder_description(folder)
                lines.append(f"- **[{rel_path}/]({rel_path}/{link_to})** - {description}")
            lines.append("")

        lines.append("**💡 Tip**: When working in a specific module, read its AI-CONTEXT.md for detailed conventions and patterns.")
        lines.append("<!-- END AUTO-GENERATED -->")

        return "\n".join(lines)

    def _build_folder_structure(self, folders: List[FolderInfo], link_to: str) -> str:
        """Build the folder structure section."""
        lines = [
            "<!-- AUTO-GENERATED: Folder Structure -->",
            "## 📂 Repository Structure",
            "",
            "```",
        ]

        # Build tree
        tree_lines = self._build_tree(folders, link_to)
        lines.extend(tree_lines)

        lines.extend([
            "```",
            "",
            "**Navigation**: Each folder contains detailed documentation. Click 📖 Docs links.",
            "<!-- END AUTO-GENERATED -->",
        ])

        return "\n".join(lines)

    def _group_folders_by_toplevel(self, folders: List[FolderInfo]) -> dict[str, List[FolderInfo]]:
        """Group folders by their top-level directory."""
        grouped: dict[str, List[FolderInfo]] = {}

        for folder in folders:
            parts = folder.relative_path.parts
            if parts:
                top_level = parts[0]
            else:
                top_level = "root"

            if top_level not in grouped:
                grouped[top_level] = []
            grouped[top_level].append(folder)

        return grouped

    def _get_folder_description(self, folder: FolderInfo) -> str:
        """Get a brief description for a folder."""
        name = folder.relative_path.name
        
        # Common folder descriptions
        descriptions = {
            "agents": "Agent implementations",
            "api": "API routes and endpoints",
            "core": "Core utilities and configuration",
            "cli": "Command-line interface",
            "utils": "Utility functions",
            "models": "Data models",
            "services": "Business logic services",
            "tests": "Test suite",
            "generators": "Documentation generators",
            "lib": "Library code",
            "handlers": "Request handlers",
            "controllers": "Route controllers",
            "routes": "Route definitions",
        }

        return descriptions.get(name, f"{folder.file_count} files ({folder.primary_language})")

    def _build_tree(self, folders: List[FolderInfo], link_to: str) -> List[str]:
        """Build an ASCII tree representation."""
        lines = []
        
        # Sort folders by path
        sorted_folders = sorted(folders, key=lambda f: str(f.relative_path))
        
        # Build simple tree structure
        shown_dirs: set[str] = set()
        
        for folder in sorted_folders:
            parts = folder.relative_path.parts
            
            # Show parent directories
            for i in range(len(parts)):
                dir_path = "/".join(parts[:i+1])
                if dir_path not in shown_dirs:
                    indent = "│   " * i
                    if i < len(parts) - 1:
                        lines.append(f"{indent}├── {parts[i]}/")
                    else:
                        rel = str(folder.relative_path)
                        lines.append(f"{indent}├── {parts[i]}/ → [📖 Docs]({rel}/{link_to})")
                    shown_dirs.add(dir_path)

        return lines if lines else ["└── (no documented folders)"]

    def _find_insertion_point(self, content: str) -> int:
        """Find a good point to insert the index section.
        
        Looks for:
        1. After "## Overview" or "## About"
        2. After first paragraph of content
        3. Returns -1 to append at end
        """
        # Look for common sections to insert after
        patterns = [
            r"## Overview.*?\n\n",
            r"## About.*?\n\n",
            r"## Introduction.*?\n\n",
            r"# .*?\n\n.*?\n\n",  # After title and first paragraph
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.end()

        return -1
