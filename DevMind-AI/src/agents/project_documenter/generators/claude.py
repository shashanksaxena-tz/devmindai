"""Claude Code CLAUDE.md documentation generator."""

from __future__ import annotations

from typing import Any

from .base import BaseDocGenerator, GeneratedDoc
from ..analyzer import CodebaseProfile


class ClaudeDocGenerator(BaseDocGenerator):
    """Generates CLAUDE.md files for Claude Code.

    CLAUDE.md is a concise, human-readable file that becomes part of Claude's
    system prompt, providing project context and guidelines.

    Reference: https://claude.com/blog/using-claude-md-files
    """

    format_name = "claude"
    format_description = "CLAUDE.md for Claude Code"

    async def generate(self, profile: CodebaseProfile, **kwargs: Any) -> list[GeneratedDoc]:
        """Generate CLAUDE.md documentation.

        Args:
            profile: Analyzed codebase profile
            **kwargs: Additional options

        Returns:
            List with CLAUDE.md file
        """
        include_detailed_context = kwargs.get("detailed", False)

        # Build the CLAUDE.md content
        sections = []

        # Project overview - concise
        sections.append(f"# {profile.name}")
        if profile.description:
            sections.append(f"\n{profile.description}")

        # Tech stack - brief
        sections.append("\n## Tech Stack")
        sections.append(f"- **Language**: {profile.primary_language.capitalize()}")
        if profile.frameworks:
            sections.append(f"- **Frameworks**: {', '.join(profile.frameworks)}")
        if profile.api_style:
            sections.append(f"- **API Style**: {profile.api_style}")

        # Commands - essential for Claude
        sections.append("\n## Commands")
        if profile.build_commands:
            sections.append(f"- **Build**: `{profile.build_commands[0]}`")
        if profile.test_commands:
            sections.append(f"- **Test**: `{profile.test_commands[0]}`")
        if profile.lint_commands:
            sections.append(f"- **Lint**: `{profile.lint_commands[0]}`")

        # Code style - keep concise
        sections.append("\n## Code Style")
        style_items = []
        for tool in profile.code_style:
            style_items.append(f"Uses {tool}")
        if style_items:
            sections.append("- " + ", ".join(style_items))

        # Naming conventions
        if profile.naming_conventions:
            conventions = []
            for item, convention in profile.naming_conventions.items():
                conventions.append(f"{item}: {convention}")
            if conventions:
                sections.append(f"- Naming: {', '.join(conventions)}")

        # Project structure - brief overview
        sections.append("\n## Structure")
        key_dirs = self._get_key_directories(profile)
        for dir_info in key_dirs[:6]:  # Limit to 6 key directories
            sections.append(f"- `{dir_info['path']}/` - {dir_info['purpose']}")

        # Important guidelines
        sections.append("\n## Guidelines")
        guidelines = await self._generate_guidelines(profile)
        sections.append(guidelines)

        # Warnings/gotchas if any
        gotchas = self._detect_gotchas(profile)
        if gotchas:
            sections.append("\n## Gotchas")
            for gotcha in gotchas[:5]:
                sections.append(f"- {gotcha}")

        content = "\n".join(sections)

        return [
            GeneratedDoc(
                path="CLAUDE.md",
                content=content,
                format_name=self.format_name,
                description="Claude Code context file with project overview and guidelines",
            )
        ]

    def _get_key_directories(self, profile: CodebaseProfile) -> list[dict[str, str]]:
        """Identify key directories and their purposes."""
        key_dirs = []
        dir_purposes = {
            "src": "Main source code",
            "lib": "Library code",
            "app": "Application code",
            "api": "API endpoints",
            "routes": "Route handlers",
            "controllers": "Request handlers",
            "services": "Business logic",
            "models": "Data models",
            "components": "UI components",
            "pages": "Page components",
            "utils": "Utility functions",
            "helpers": "Helper functions",
            "tests": "Test files",
            "test": "Test files",
            "__tests__": "Test files",
            "spec": "Test specifications",
            "config": "Configuration",
            "scripts": "Build/utility scripts",
            "public": "Static assets",
            "static": "Static files",
            "assets": "Asset files",
            "docs": "Documentation",
            "types": "Type definitions",
            "interfaces": "Interface definitions",
            "hooks": "React hooks",
            "store": "State management",
            "middleware": "Middleware",
            "db": "Database layer",
            "migrations": "Database migrations",
        }

        for directory in profile.structure.directories:
            base_dir = directory.split("/")[0]
            if base_dir in dir_purposes:
                if not any(d["path"] == base_dir for d in key_dirs):
                    key_dirs.append({"path": base_dir, "purpose": dir_purposes[base_dir]})

        return key_dirs

    async def _generate_guidelines(self, profile: CodebaseProfile) -> str:
        """Generate concise coding guidelines."""
        # Get language-specific base guidelines
        base_guidelines = self._get_language_specific_guidelines(profile).strip()

        # Build prompt for LLM to generate specific guidelines
        prompt = f"""Generate 5-7 concise, actionable coding guidelines for this project.
Keep each guideline to ONE line. Be specific, not generic.

Project info:
- Language: {profile.primary_language}
- Frameworks: {', '.join(profile.frameworks) if profile.frameworks else 'None'}
- Architecture: {', '.join(profile.architecture_patterns) if profile.architecture_patterns else 'Standard'}
- Code style tools: {', '.join(profile.code_style.keys()) if profile.code_style else 'None specified'}

Base language guidelines:
{base_guidelines}

Output format (markdown bullet points, one line each):
- Guideline 1
- Guideline 2
..."""

        system_prompt = """You are a technical documentation expert. Generate concise,
actionable coding guidelines. Each guideline should be specific and useful for an AI
coding assistant. Avoid generic advice like "write clean code". Focus on project-specific
patterns and conventions."""

        try:
            guidelines = await self._generate_content(prompt, system_prompt)
            # Clean up - ensure it's bullet points
            lines = guidelines.strip().split("\n")
            cleaned = []
            for line in lines:
                line = line.strip()
                if line and (line.startswith("-") or line.startswith("*")):
                    cleaned.append(line)
            return "\n".join(cleaned[:7])  # Max 7 guidelines
        except Exception:
            # Fallback to basic guidelines
            return base_guidelines

    def _detect_gotchas(self, profile: CodebaseProfile) -> list[str]:
        """Detect potential gotchas or warnings."""
        gotchas = []

        # Check for common issues
        if profile.primary_language == "python":
            if "pyproject.toml" in profile.key_files_content:
                content = profile.key_files_content["pyproject.toml"]
                if "python = " in content and "3.12" in content:
                    gotchas.append("Requires Python 3.12+")

        if "typescript" in profile.languages:
            if "tsconfig.json" in profile.key_files_content:
                content = profile.key_files_content["tsconfig.json"]
                if '"strict": true' in content:
                    gotchas.append("TypeScript strict mode enabled - ensure proper typing")

        # Check for monorepo
        if "Monorepo" in profile.architecture_patterns:
            gotchas.append("Monorepo structure - changes may affect multiple packages")

        # Check for required environment variables
        if any(".env" in f.relative_path for f in profile.structure.files):
            gotchas.append("Requires environment variables - check .env.example")

        return gotchas
