"""OpenCode documentation generator.

Generates AGENTS.md and .opencode.json for OpenCode AI coding assistant.
"""

import json
from typing import Any

from .base import BaseDocGenerator, GeneratedDoc
from ..analyzer import CodebaseProfile


class OpenCodeDocGenerator(BaseDocGenerator):
    """Generates OpenCode-compatible documentation."""

    def generate(self, profile: CodebaseProfile, **options: Any) -> list[GeneratedDoc]:
        """Generate OpenCode documentation files.

        Args:
            profile: Analyzed codebase profile
            **options: Generation options

        Returns:
            List of generated documents (AGENTS.md and .opencode.json)
        """
        docs = []

        # Generate AGENTS.md
        agents_md = self._generate_agents_md(profile)
        docs.append(GeneratedDoc(
            format_name="opencode",
            file_path="AGENTS.md",
            content=agents_md,
            description="OpenCode agent instructions file"
        ))

        # Generate .opencode.json
        config = self._generate_config(profile)
        docs.append(GeneratedDoc(
            format_name="opencode",
            file_path=".opencode.json",
            content=config,
            description="OpenCode configuration file"
        ))

        return docs

    def _generate_agents_md(self, profile: CodebaseProfile) -> str:
        """Generate AGENTS.md content."""
        lines = [
            f"# {profile.name} - OpenCode Agent Instructions",
            "",
            "This file provides workflow instructions for OpenCode AI assistant.",
            "",
        ]

        # Project Context
        lines.append("## Project Context")
        lines.append("")
        if profile.description:
            lines.append(profile.description)
            lines.append("")

        lines.append(f"- **Primary Language**: {profile.primary_language}")
        if profile.frameworks:
            lines.append(f"- **Frameworks**: {', '.join(profile.frameworks)}")
        lines.append("")

        # Workflow Rules
        lines.append("## Workflow Rules")
        lines.append("")
        lines.append("### Before Making Changes")
        lines.append("1. Read relevant files to understand existing code")
        lines.append("2. Check for existing patterns in similar files")
        lines.append("3. Verify the change aligns with project architecture")
        lines.append("")

        lines.append("### Code Changes")
        if profile.primary_language == "Python":
            lines.append("1. Use type hints for all functions")
            lines.append("2. Follow PEP 8 naming conventions")
        elif profile.primary_language in ["TypeScript"]:
            lines.append("1. Use TypeScript types, avoid `any`")
            lines.append("2. Follow existing component patterns")
        else:
            lines.append("1. Follow existing code patterns")
            lines.append("2. Use consistent naming conventions")
        lines.append("3. Update tests when modifying logic")
        lines.append("")

        lines.append("### After Changes")
        if profile.lint_commands:
            lines.append(f"1. Run linting: `{profile.lint_commands[0]}`")
        if profile.test_commands:
            lines.append(f"2. Run tests: `{profile.test_commands[0]}`")
        if profile.build_commands:
            lines.append(f"3. Verify build: `{profile.build_commands[0]}`")
        lines.append("")

        # Project Structure
        lines.append("## Project Structure")
        lines.append("")
        lines.append("```")
        lines.append(f"{profile.name}/")
        if profile.structure and profile.structure.directories:
            for dir_path in sorted(profile.structure.directories)[:15]:
                depth = dir_path.count("/")
                indent = "    " * depth
                dir_name = dir_path.split("/")[-1] if "/" in dir_path else dir_path
                lines.append(f"{indent}├── {dir_name}/")
        lines.append("```")
        lines.append("")

        # Key Files
        if profile.structure and profile.structure.files:
            lines.append("## Key Files")
            lines.append("")
            lines.append("| File | Purpose |")
            lines.append("|------|---------|")

            # Find important files
            important_patterns = [
                ("main", "Main entry point"),
                ("config", "Configuration"),
                ("index", "Module entry"),
                ("app", "Application"),
                ("server", "Server entry"),
                ("package.json", "Package manifest"),
                ("pyproject.toml", "Python project config"),
                ("Cargo.toml", "Rust project config"),
            ]

            shown = 0
            for file_info in profile.structure.files[:50]:
                if shown >= 10:
                    break
                file_name = file_info.path.split("/")[-1].lower()
                for pattern, desc in important_patterns:
                    if pattern in file_name:
                        lines.append(f"| `{file_info.path}` | {desc} |")
                        shown += 1
                        break
            lines.append("")

        # Commit Guidelines
        lines.append("## Commit Guidelines")
        lines.append("")
        lines.append("- Use descriptive commit messages")
        lines.append("- Reference issue numbers if applicable")
        lines.append("- Run tests before committing")
        lines.append("- Never commit API keys or credentials")

        return "\n".join(lines)

    def _generate_config(self, profile: CodebaseProfile) -> str:
        """Generate .opencode.json content."""
        config = {
            "$schema": "https://opencode.ai/schema/config.json",
            "data": {
                "directory": ".opencode"
            },
            "providers": {
                "gemini": {"disabled": False},
                "anthropic": {"disabled": False},
                "openai": {"disabled": False},
                "copilot": {"disabled": False}
            },
            "agents": {
                "coder": {
                    "model": "gemini/gemini-3-flash-preview",
                    "maxTokens": 8000
                },
                "task": {
                    "model": "gemini/gemini-3-flash-preview",
                    "maxTokens": 4000
                },
                "title": {
                    "model": "gemini/gemini-3-flash-preview",
                    "maxTokens": 100
                }
            },
            "shell": {
                "path": "/bin/bash",
                "args": ["-l"]
            },
            "autoCompact": True,
            "tools": {
                "edit": True,
                "bash": True,
                "read": True,
                "glob": True,
                "grep": True
            }
        }

        return json.dumps(config, indent=2)
