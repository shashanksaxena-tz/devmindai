"""GitHub Copilot instructions documentation generator."""

from __future__ import annotations

from typing import Any

from .base import BaseDocGenerator, GeneratedDoc
from ..analyzer import CodebaseProfile


class CopilotDocGenerator(BaseDocGenerator):
    """Generates .github/copilot-instructions.md for GitHub Copilot.

    This file provides repository-wide custom instructions that apply to all
    Copilot requests made in the context of the repository.

    Reference: https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot
    """

    format_name = "copilot"
    format_description = "GitHub Copilot custom instructions"

    async def generate(self, profile: CodebaseProfile, **kwargs: Any) -> list[GeneratedDoc]:
        """Generate Copilot instructions documentation.

        Args:
            profile: Analyzed codebase profile
            **kwargs: Additional options

        Returns:
            List with copilot-instructions.md file
        """
        sections = []

        # Project context
        sections.append(f"# {profile.name} - Copilot Instructions")
        sections.append("")
        if profile.description:
            sections.append(profile.description)
            sections.append("")

        # Technology context
        sections.append("## Project Context")
        sections.append("")
        sections.append(f"This is a {profile.primary_language.capitalize()} project.")
        if profile.frameworks:
            sections.append(f"It uses {', '.join(profile.frameworks)}.")
        if profile.api_style:
            sections.append(f"The API follows {profile.api_style} conventions.")
        sections.append("")

        # Coding standards
        sections.append("## Coding Standards")
        sections.append("")
        standards = await self._generate_coding_standards(profile)
        sections.append(standards)
        sections.append("")

        # File structure context
        sections.append("## File Structure")
        sections.append("")
        structure_info = self._generate_structure_context(profile)
        sections.append(structure_info)
        sections.append("")

        # Testing guidelines
        sections.append("## Testing")
        sections.append("")
        testing_info = self._generate_testing_guidelines(profile)
        sections.append(testing_info)
        sections.append("")

        # Dependencies context
        if profile.dependencies:
            sections.append("## Key Dependencies")
            sections.append("")
            for dep_info in profile.dependencies[:2]:  # Limit to first 2
                key_deps = dep_info.dependencies[:10]
                if key_deps:
                    sections.append(f"Main packages: {', '.join(key_deps)}")
            sections.append("")

        # Important conventions
        sections.append("## Important Conventions")
        sections.append("")
        conventions = await self._generate_conventions(profile)
        sections.append(conventions)

        content = "\n".join(sections)

        return [
            GeneratedDoc(
                path=".github/copilot-instructions.md",
                content=content,
                format_name=self.format_name,
                description="GitHub Copilot repository-wide custom instructions",
            )
        ]

    async def _generate_coding_standards(self, profile: CodebaseProfile) -> str:
        """Generate coding standards section."""
        lines = []

        # Naming conventions
        if profile.naming_conventions:
            for item, convention in profile.naming_conventions.items():
                lines.append(f"- Use {convention} for {item}")

        # Code style tools
        if profile.code_style:
            tools = list(profile.code_style.keys())
            lines.append(f"- Format code using: {', '.join(tools)}")

        # Language-specific standards
        lang_standards = {
            "python": [
                "- Include type hints for all function parameters and return values",
                "- Use docstrings for public functions and classes",
                "- Prefer f-strings over .format() or % formatting",
            ],
            "typescript": [
                "- Always define explicit types, avoid 'any'",
                "- Use interfaces for object shapes",
                "- Prefer async/await over Promise chains",
            ],
            "javascript": [
                "- Use const by default, let when reassignment is needed",
                "- Prefer arrow functions for callbacks",
                "- Use template literals for string interpolation",
            ],
            "go": [
                "- Handle all errors explicitly",
                "- Use meaningful variable names",
                "- Keep functions small and focused",
            ],
            "rust": [
                "- Prefer Result over panic for recoverable errors",
                "- Use meaningful error types",
                "- Document public APIs with doc comments",
            ],
        }

        if profile.primary_language in lang_standards:
            lines.extend(lang_standards[profile.primary_language])

        return "\n".join(lines) if lines else "Follow language best practices."

    def _generate_structure_context(self, profile: CodebaseProfile) -> str:
        """Generate file structure context."""
        lines = []

        # Key directories
        dir_info = {
            "src": "contains main source code",
            "lib": "contains library code",
            "api": "contains API route handlers",
            "components": "contains UI components",
            "services": "contains business logic",
            "models": "contains data models",
            "utils": "contains utility functions",
            "tests": "contains test files",
            "config": "contains configuration files",
        }

        for directory in profile.structure.directories:
            base_dir = directory.split("/")[0]
            if base_dir in dir_info and base_dir not in [l.split("`")[1] if "`" in l else "" for l in lines]:
                lines.append(f"- `{base_dir}/` {dir_info[base_dir]}")

        # Entry points
        if profile.structure.entry_points:
            lines.append(f"- Main entry point(s): {', '.join(profile.structure.entry_points[:3])}")

        return "\n".join(lines[:8]) if lines else "Standard project structure."

    def _generate_testing_guidelines(self, profile: CodebaseProfile) -> str:
        """Generate testing guidelines."""
        lines = []

        if profile.test_commands:
            lines.append(f"Run tests with: `{profile.test_commands[0]}`")

        if profile.structure.test_directories:
            lines.append(f"Test files are located in: {', '.join(profile.structure.test_directories[:3])}")

        # Language-specific testing
        test_conventions = {
            "python": [
                "- Write tests using pytest conventions",
                "- Name test files with test_ prefix",
                "- Use fixtures for common test setup",
            ],
            "typescript": [
                "- Write tests using Jest or Vitest",
                "- Co-locate tests with source files or in __tests__ directory",
                "- Use describe/it blocks for test organization",
            ],
            "javascript": [
                "- Write tests using Jest",
                "- Use meaningful test descriptions",
                "- Mock external dependencies",
            ],
            "go": [
                "- Write tests in _test.go files",
                "- Use table-driven tests where appropriate",
                "- Use testify for assertions if available",
            ],
            "rust": [
                "- Write unit tests in the same file with #[cfg(test)]",
                "- Write integration tests in tests/ directory",
                "- Use assert! and assert_eq! macros",
            ],
        }

        if profile.primary_language in test_conventions:
            lines.extend(test_conventions[profile.primary_language])

        return "\n".join(lines) if lines else "Write comprehensive tests for new code."

    async def _generate_conventions(self, profile: CodebaseProfile) -> str:
        """Generate important conventions using LLM."""
        prompt = f"""Generate 5-8 specific coding conventions for this project.
Each convention should be a short, actionable instruction.

Project details:
- Language: {profile.primary_language}
- Frameworks: {', '.join(profile.frameworks) if profile.frameworks else 'None'}
- Architecture patterns: {', '.join(profile.architecture_patterns) if profile.architecture_patterns else 'Standard'}

Output as bullet points (- prefix), one convention per line.
Focus on:
1. Error handling patterns
2. Code organization
3. Documentation requirements
4. Import/export patterns
5. Async/await usage (if applicable)"""

        system_prompt = """You are a senior developer writing coding conventions for GitHub Copilot.
Be specific and actionable. Avoid generic advice. Each convention should help Copilot
generate better, more consistent code for this specific project."""

        try:
            conventions = await self._generate_content(prompt, system_prompt)
            # Clean up
            lines = []
            for line in conventions.strip().split("\n"):
                line = line.strip()
                if line.startswith("-") or line.startswith("*"):
                    lines.append(line)
            return "\n".join(lines[:8])
        except Exception:
            return """- Follow existing code patterns in the repository
- Handle errors appropriately
- Add comments for complex logic
- Write self-documenting code"""
