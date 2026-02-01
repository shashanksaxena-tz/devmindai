"""Cline documentation generator.

Generates .clinerules/ directory with markdown rules for Cline VS Code extension.
"""

from typing import Any

from .base import BaseDocGenerator, GeneratedDoc
from ..analyzer import CodebaseProfile


class ClineDocGenerator(BaseDocGenerator):
    """Generates Cline-compatible documentation."""

    def generate(self, profile: CodebaseProfile, **options: Any) -> list[GeneratedDoc]:
        """Generate Cline documentation files.

        Args:
            profile: Analyzed codebase profile
            **options: Generation options

        Returns:
            List of generated documents (.clinerules/*.md files)
        """
        docs = []

        # Generate main overview
        overview = self._generate_overview(profile)
        docs.append(GeneratedDoc(
            format_name="cline",
            file_path=".clinerules/project-overview.md",
            content=overview,
            description="Cline project overview rules"
        ))

        # Generate development guidelines
        guidelines = self._generate_guidelines(profile)
        docs.append(GeneratedDoc(
            format_name="cline",
            file_path=".clinerules/development-guidelines.md",
            content=guidelines,
            description="Cline development guidelines"
        ))

        # Generate commands reference
        commands = self._generate_commands(profile)
        docs.append(GeneratedDoc(
            format_name="cline",
            file_path=".clinerules/commands-reference.md",
            content=commands,
            description="Cline commands reference"
        ))

        return docs

    def _generate_overview(self, profile: CodebaseProfile) -> str:
        """Generate project overview rules."""
        lines = [
            "---",
            f"description: {profile.name} project overview and architecture guide",
            "version: 1.0.0",
            "globs:",
        ]

        # Add globs based on primary language
        if profile.primary_language == "Python":
            lines.append('  - "**/*.py"')
        elif profile.primary_language in ["JavaScript", "TypeScript"]:
            lines.append('  - "**/*.js"')
            lines.append('  - "**/*.ts"')
            lines.append('  - "**/*.tsx"')
        elif profile.primary_language == "Go":
            lines.append('  - "**/*.go"')
        elif profile.primary_language == "Rust":
            lines.append('  - "**/*.rs"')
        else:
            lines.append('  - "**/*"')

        lines.append('  - "**/*.md"')
        lines.append("---")
        lines.append("")
        lines.append(f"# {profile.name} - Project Overview")
        lines.append("")

        if profile.description:
            lines.append(profile.description)
            lines.append("")

        # Critical rules
        lines.append("## CRITICAL RULES")
        lines.append("")

        if profile.primary_language == "Python":
            lines.append("- **ALWAYS** use type hints in Python code")
        elif profile.primary_language in ["TypeScript"]:
            lines.append("- **ALWAYS** use TypeScript types, avoid `any`")

        lines.append("- **NEVER** commit API keys or secrets")
        lines.append("- **NEVER** modify files in `.env` or credentials")
        lines.append("- **ALWAYS** follow existing code patterns")
        lines.append("")

        # Project structure
        lines.append("## Project Structure")
        lines.append("")
        lines.append("```")
        lines.append(f"{profile.name}/")
        if profile.structure and profile.structure.directories:
            for dir_path in sorted(profile.structure.directories)[:12]:
                depth = dir_path.count("/")
                indent = "    " * depth
                dir_name = dir_path.split("/")[-1] if "/" in dir_path else dir_path
                lines.append(f"{indent}├── {dir_name}/")
        lines.append("```")
        lines.append("")

        # Technology stack
        lines.append("## Technology Stack")
        lines.append("")
        lines.append(f"- **Primary Language**: {profile.primary_language}")
        if profile.frameworks:
            lines.append(f"- **Frameworks**: {', '.join(profile.frameworks)}")
        lines.append("")

        return "\n".join(lines)

    def _generate_guidelines(self, profile: CodebaseProfile) -> str:
        """Generate development guidelines."""
        lines = [
            "---",
            f"description: Development guidelines for {profile.name}",
            "version: 1.0.0",
            "globs:",
        ]

        if profile.primary_language == "Python":
            lines.append('  - "**/*.py"')
        elif profile.primary_language in ["JavaScript", "TypeScript"]:
            lines.append('  - "**/*.js"')
            lines.append('  - "**/*.ts"')
        lines.append("---")
        lines.append("")
        lines.append("# Development Guidelines")
        lines.append("")

        # Code style
        lines.append("## Code Style")
        lines.append("")
        if profile.code_style:
            for key, value in profile.code_style.items():
                lines.append(f"- **{key}**: {value}")
        else:
            if profile.primary_language == "Python":
                lines.append("- Use type hints for all functions")
                lines.append("- Follow PEP 8 naming conventions")
                lines.append("- Use Black for formatting")
            elif profile.primary_language in ["JavaScript", "TypeScript"]:
                lines.append("- Use ESLint for linting")
                lines.append("- Use Prettier for formatting")
                lines.append("- Prefer const over let")
        lines.append("")

        # Naming conventions
        lines.append("## Naming Conventions")
        lines.append("")
        if profile.naming_conventions:
            for key, value in profile.naming_conventions.items():
                lines.append(f"- **{key}**: {value}")
        else:
            if profile.primary_language == "Python":
                lines.append("- `snake_case` for functions and variables")
                lines.append("- `PascalCase` for classes")
                lines.append("- `UPPER_CASE` for constants")
            elif profile.primary_language in ["JavaScript", "TypeScript"]:
                lines.append("- `camelCase` for functions and variables")
                lines.append("- `PascalCase` for components and classes")
                lines.append("- `UPPER_CASE` for constants")
        lines.append("")

        # File organization
        lines.append("## File Organization")
        lines.append("")
        lines.append("- Keep related code together")
        lines.append("- Use meaningful file and folder names")
        lines.append("- Follow existing project structure")
        lines.append("")

        return "\n".join(lines)

    def _generate_commands(self, profile: CodebaseProfile) -> str:
        """Generate commands reference."""
        lines = [
            "---",
            f"description: Common commands for {profile.name}",
            "version: 1.0.0",
            "globs:",
            '  - "**/*"',
            "---",
            "",
            "# Commands Reference",
            "",
        ]

        # Build commands
        if profile.build_commands:
            lines.append("## Build")
            lines.append("")
            lines.append("```bash")
            for cmd in profile.build_commands[:3]:
                lines.append(cmd)
            lines.append("```")
            lines.append("")

        # Test commands
        if profile.test_commands:
            lines.append("## Test")
            lines.append("")
            lines.append("```bash")
            for cmd in profile.test_commands[:3]:
                lines.append(cmd)
            lines.append("```")
            lines.append("")

        # Lint commands
        if profile.lint_commands:
            lines.append("## Lint")
            lines.append("")
            lines.append("```bash")
            for cmd in profile.lint_commands[:3]:
                lines.append(cmd)
            lines.append("```")
            lines.append("")

        # Default commands if none found
        if not profile.build_commands and not profile.test_commands:
            lines.append("## Getting Started")
            lines.append("")
            if profile.primary_language == "Python":
                lines.append("```bash")
                lines.append("# Install dependencies")
                lines.append("pip install -r requirements.txt")
                lines.append("# or with poetry")
                lines.append("poetry install")
                lines.append("```")
            elif profile.primary_language in ["JavaScript", "TypeScript"]:
                lines.append("```bash")
                lines.append("# Install dependencies")
                lines.append("npm install")
                lines.append("# or with yarn")
                lines.append("yarn")
                lines.append("```")
            lines.append("")

        return "\n".join(lines)
