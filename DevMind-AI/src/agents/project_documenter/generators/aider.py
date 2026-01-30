"""Aider documentation generator.

Generates CONVENTIONS.md and .aider.conf.yml for Aider AI pair programming.
"""

from typing import Any

from .base import BaseDocGenerator, GeneratedDoc
from ..analyzer import CodebaseProfile


class AiderDocGenerator(BaseDocGenerator):
    """Generates Aider-compatible documentation."""

    def generate(self, profile: CodebaseProfile, **options: Any) -> list[GeneratedDoc]:
        """Generate Aider documentation files.

        Args:
            profile: Analyzed codebase profile
            **options: Generation options

        Returns:
            List of generated documents (CONVENTIONS.md and .aider.conf.yml)
        """
        docs = []

        # Generate CONVENTIONS.md
        conventions = self._generate_conventions(profile)
        docs.append(GeneratedDoc(
            format_name="aider",
            file_path="CONVENTIONS.md",
            content=conventions,
            description="Aider coding conventions file"
        ))

        # Generate .aider.conf.yml
        config = self._generate_config(profile)
        docs.append(GeneratedDoc(
            format_name="aider",
            file_path=".aider.conf.yml",
            content=config,
            description="Aider configuration file"
        ))

        return docs

    def _generate_conventions(self, profile: CodebaseProfile) -> str:
        """Generate CONVENTIONS.md content."""
        sections = []

        # Header
        sections.append(f"# {profile.name} - Coding Conventions for Aider\n")
        sections.append("This file defines coding conventions and project context for Aider AI pair programming.\n")

        # Project Overview
        sections.append("## Project Overview\n")
        if profile.description:
            sections.append(f"{profile.description}\n")

        # Technology Stack
        sections.append("## Technology Stack\n")
        sections.append(f"- **Primary Language**: {profile.primary_language}")
        if profile.languages:
            sections.append(f"- **Languages**: {', '.join(profile.languages)}")
        if profile.frameworks:
            sections.append(f"- **Frameworks**: {', '.join(profile.frameworks)}")
        sections.append("")

        # Code Style
        sections.append("## Code Style Guidelines\n")
        if profile.code_style:
            for key, value in profile.code_style.items():
                sections.append(f"- **{key}**: {value}")
        else:
            sections.append("- Follow language-specific best practices")
            sections.append("- Use consistent naming conventions")
            sections.append("- Write clear, documented code")
        sections.append("")

        # Commands
        sections.append("## Common Commands\n")
        if profile.build_commands:
            sections.append("### Build")
            sections.append("```bash")
            for cmd in profile.build_commands[:3]:
                sections.append(cmd)
            sections.append("```\n")

        if profile.test_commands:
            sections.append("### Test")
            sections.append("```bash")
            for cmd in profile.test_commands[:3]:
                sections.append(cmd)
            sections.append("```\n")

        if profile.lint_commands:
            sections.append("### Lint")
            sections.append("```bash")
            for cmd in profile.lint_commands[:3]:
                sections.append(cmd)
            sections.append("```\n")

        # Directory Structure
        sections.append("## Directory Structure\n")
        sections.append("```")
        sections.append(f"{profile.name}/")
        if profile.structure and profile.structure.directories:
            for dir_path in sorted(profile.structure.directories)[:15]:
                depth = dir_path.count("/")
                indent = "    " * depth
                dir_name = dir_path.split("/")[-1] if "/" in dir_path else dir_path
                sections.append(f"{indent}├── {dir_name}/")
        sections.append("```\n")

        # Important Notes
        sections.append("## Important Notes\n")
        sections.append("- Never commit API keys or secrets")
        sections.append("- Run tests before committing changes")
        sections.append("- Follow existing patterns in the codebase")

        return "\n".join(sections)

    def _generate_config(self, profile: CodebaseProfile) -> str:
        """Generate .aider.conf.yml content."""
        lines = [
            f"# Aider Configuration for {profile.name}",
            "# Load with: aider --config .aider.conf.yml",
            "",
            "# Read conventions file for context",
            "read:",
            "  - CONVENTIONS.md",
        ]

        # Add CLAUDE.md if it might exist
        lines.append("  - CLAUDE.md")
        lines.append("")

        # Model settings based on language
        lines.append("# Model settings")
        lines.append("model: gemini/gemini-2.0-flash")
        lines.append("")

        # Repository map
        lines.append("# Repository map for better context")
        lines.append("repo-map: true")
        lines.append("map-tokens: 2048")
        lines.append("")

        # Auto-commit settings
        lines.append("# Auto-commit settings")
        lines.append("auto-commits: false")
        lines.append("dirty-commits: false")
        lines.append("")

        # Lint command based on language
        lines.append("# Code style")
        if profile.lint_commands:
            lines.append(f'lint-cmd: "{profile.lint_commands[0]}"')
        elif profile.primary_language == "Python":
            lines.append('lint-cmd: "black --check"')
        elif profile.primary_language in ["JavaScript", "TypeScript"]:
            lines.append('lint-cmd: "eslint"')
        lines.append("auto-lint: true")
        lines.append("")

        # Test command
        if profile.test_commands:
            lines.append("# Testing")
            lines.append(f'test-cmd: "{profile.test_commands[0]}"')
            lines.append("")

        # Git settings
        lines.append("# Git settings")
        lines.append("git: true")
        lines.append("gitignore: true")
        lines.append("")

        # Encoding and output
        lines.append("# Encoding")
        lines.append("encoding: utf-8")
        lines.append("")
        lines.append("# Streaming output")
        lines.append("stream: true")
        lines.append("pretty: true")

        return "\n".join(lines)
