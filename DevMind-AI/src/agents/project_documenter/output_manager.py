"""Output manager for organized documentation generation."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any

from .generators.base import GeneratedDoc


class OutputManager:
    """Manages organized output for documentation generation.

    Creates a structured output folder:
    ```
    devmind-output/
    └── project-documenter/
        └── {project-name}-{timestamp}/
            ├── README.md           # Execution summary
            ├── claude/
            │   └── CLAUDE.md
            ├── copilot/
            │   └── copilot-instructions.md
            ├── cursor/
            │   └── rules/*.mdc
            └── ...
    ```
    """

    DEFAULT_OUTPUT_BASE = "devmind-output"
    AGENT_FOLDER = "project-documenter"

    def __init__(
        self,
        base_path: Path | None = None,
        project_name: str = "project",
    ):
        """Initialize output manager.

        Args:
            base_path: Base path for output (defaults to DevMind-AI/devmind-output)
            project_name: Name of the project being documented
        """
        self.project_name = self._sanitize_name(project_name)
        self.timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.run_id = f"{self.project_name}-{self.timestamp}"

        # Determine base path
        if base_path:
            self.base_path = Path(base_path)
        else:
            # Default to DevMind-AI/devmind-output
            self.base_path = Path(__file__).parent.parent.parent.parent / self.DEFAULT_OUTPUT_BASE

        # Full output path for this run
        self.output_path = self.base_path / self.AGENT_FOLDER / self.run_id

        # Track what's written
        self.written_files: list[str] = []
        self.errors: list[str] = []

    def _sanitize_name(self, name: str) -> str:
        """Sanitize project name for filesystem."""
        # Remove/replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        return name[:50]  # Limit length

    def ensure_output_dir(self) -> Path:
        """Ensure output directory exists.

        Returns:
            Path to output directory
        """
        self.output_path.mkdir(parents=True, exist_ok=True)
        return self.output_path

    def get_format_dir(self, format_name: str) -> Path:
        """Get directory for a specific format.

        Args:
            format_name: Name of the format (claude, copilot, etc.)

        Returns:
            Path to format-specific directory
        """
        format_dir = self.output_path / format_name
        format_dir.mkdir(parents=True, exist_ok=True)
        return format_dir

    def write_docs(
        self,
        docs: list[GeneratedDoc],
        organize_by_format: bool = True,
    ) -> list[str]:
        """Write documentation files to organized structure.

        Args:
            docs: List of generated documents
            organize_by_format: If True, organize into format subdirectories

        Returns:
            List of written file paths
        """
        self.ensure_output_dir()
        written = []

        for doc in docs:
            if doc.path.startswith("error_"):
                self.errors.append(doc.content)
                continue

            try:
                if organize_by_format:
                    # Put in format-specific subdirectory
                    format_dir = self.get_format_dir(doc.format_name)

                    # Simplify the path (remove leading directories like .github/)
                    simple_path = self._simplify_path(doc.path)
                    file_path = format_dir / simple_path
                else:
                    # Keep original structure
                    file_path = self.output_path / doc.path

                # Create parent directories
                file_path.parent.mkdir(parents=True, exist_ok=True)

                # Write file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(doc.content)

                written.append(str(file_path))

            except Exception as e:
                self.errors.append(f"Failed to write {doc.path}: {str(e)}")

        self.written_files.extend(written)
        return written

    def _simplify_path(self, path: str) -> str:
        """Simplify file path for organized output.

        Examples:
            .github/copilot-instructions.md → copilot-instructions.md
            .cursor/rules/index.mdc → rules/index.mdc
            CLAUDE.md → CLAUDE.md
        """
        # Remove leading dot directories
        parts = Path(path).parts
        if parts and parts[0].startswith('.'):
            # Keep subdirectories but remove the top-level dot directory
            if len(parts) > 1:
                return str(Path(*parts[1:]))
        return path

    def write_readme(
        self,
        profile: dict[str, Any],
        docs: list[dict[str, Any]],
        formats_generated: list[str],
    ) -> str:
        """Write execution summary README.

        Args:
            profile: Analyzed codebase profile
            docs: List of generated doc info
            formats_generated: List of format names generated

        Returns:
            Path to README file
        """
        self.ensure_output_dir()

        readme_content = self._generate_readme_content(
            profile, docs, formats_generated
        )

        readme_path = self.output_path / "README.md"
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)

        self.written_files.append(str(readme_path))
        return str(readme_path)

    def _generate_readme_content(
        self,
        profile: dict[str, Any],
        docs: list[dict[str, Any]],
        formats_generated: list[str],
    ) -> str:
        """Generate README content for execution summary."""
        lines = []

        # Header
        lines.append(f"# Documentation Output: {profile.get('name', 'Project')}")
        lines.append("")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Project Summary
        lines.append("## Project Summary")
        lines.append("")
        lines.append(f"- **Name**: {profile.get('name', 'Unknown')}")
        lines.append(f"- **Language**: {profile.get('primary_language', 'Unknown').capitalize()}")
        if profile.get('frameworks'):
            lines.append(f"- **Frameworks**: {', '.join(profile['frameworks'])}")
        if profile.get('api_style'):
            lines.append(f"- **API Style**: {profile['api_style']}")
        lines.append(f"- **Files Analyzed**: {profile.get('file_count', 0)}")
        lines.append(f"- **Directories**: {profile.get('directory_count', 0)}")
        lines.append("")

        # Commands
        if profile.get('build_commands') or profile.get('test_commands') or profile.get('lint_commands'):
            lines.append("## Detected Commands")
            lines.append("")
            if profile.get('build_commands'):
                lines.append(f"- **Build**: `{profile['build_commands'][0]}`")
            if profile.get('test_commands'):
                lines.append(f"- **Test**: `{profile['test_commands'][0]}`")
            if profile.get('lint_commands'):
                lines.append(f"- **Lint**: `{profile['lint_commands'][0]}`")
            lines.append("")

        # Generated Files
        lines.append("## Generated Documentation")
        lines.append("")
        lines.append(f"**Formats**: {', '.join(formats_generated)}")
        lines.append("")
        lines.append("| Format | File | Description |")
        lines.append("|--------|------|-------------|")

        for doc in docs:
            if not doc.get('path', '').startswith('error_'):
                lines.append(
                    f"| {doc.get('format', 'unknown')} | "
                    f"`{doc.get('path', '')}` | "
                    f"{doc.get('description', '')[:50]} |"
                )

        lines.append("")

        # Usage Instructions
        lines.append("## How to Use These Files")
        lines.append("")
        lines.append("### Copy to Your Project")
        lines.append("")
        lines.append("To use these files with AI assistants, copy them to your project:")
        lines.append("")
        lines.append("```bash")
        lines.append(f"# From this output directory ({self.run_id})")
        lines.append("")

        if 'claude' in formats_generated:
            lines.append("# For Claude Code:")
            lines.append("cp claude/CLAUDE.md /path/to/your/project/")
            lines.append("")

        if 'copilot' in formats_generated:
            lines.append("# For GitHub Copilot:")
            lines.append("mkdir -p /path/to/your/project/.github")
            lines.append("cp copilot/copilot-instructions.md /path/to/your/project/.github/")
            lines.append("")

        if 'cursor' in formats_generated:
            lines.append("# For Cursor AI:")
            lines.append("cp -r cursor/rules /path/to/your/project/.cursor/")
            lines.append("")

        if 'gemini' in formats_generated:
            lines.append("# For Google Gemini:")
            lines.append("cp gemini/GEMINI.md /path/to/your/project/")
            lines.append("")

        if 'windsurf' in formats_generated:
            lines.append("# For Windsurf/Codeium:")
            lines.append("cp -r windsurf/* /path/to/your/project/")
            lines.append("")

        lines.append("```")
        lines.append("")

        # Errors if any
        if self.errors:
            lines.append("## Errors")
            lines.append("")
            for error in self.errors:
                lines.append(f"- {error}")
            lines.append("")

        # Footer
        lines.append("---")
        lines.append(f"*Generated by DevMind AI Project Documenter*")

        return "\n".join(lines)

    def copy_to_project(
        self,
        target_path: Path,
        docs: list[GeneratedDoc],
    ) -> list[str]:
        """Copy generated docs directly to target project.

        This writes files in their original intended locations
        (e.g., CLAUDE.md at root, .github/copilot-instructions.md, etc.)

        Args:
            target_path: Path to target project
            docs: List of generated documents

        Returns:
            List of written file paths
        """
        written = []

        for doc in docs:
            if doc.path.startswith("error_"):
                continue

            try:
                file_path = target_path / doc.path
                file_path.parent.mkdir(parents=True, exist_ok=True)

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(doc.content)

                written.append(str(file_path))

            except Exception as e:
                self.errors.append(f"Failed to copy {doc.path}: {str(e)}")

        return written

    def get_summary(self) -> dict[str, Any]:
        """Get execution summary.

        Returns:
            Summary dictionary
        """
        return {
            "run_id": self.run_id,
            "output_path": str(self.output_path),
            "files_written": len(self.written_files),
            "errors": len(self.errors),
            "written_files": self.written_files,
            "error_messages": self.errors,
        }
