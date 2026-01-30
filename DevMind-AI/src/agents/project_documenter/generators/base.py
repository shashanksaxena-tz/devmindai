"""Base class for documentation generators."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from src.core.llm import BaseLLMClient

from ..analyzer import CodebaseProfile


@dataclass
class GeneratedDoc:
    """A generated documentation file."""

    path: str  # Relative path where the file should be written
    content: str  # File content
    format_name: str  # Name of the format (e.g., "claude", "copilot")
    description: str = ""  # Description of what this file does
    overwrite: bool = True  # Whether to overwrite existing files


class BaseDocGenerator(ABC):
    """Base class for all documentation generators."""

    # Override in subclasses
    format_name: str = "base"
    format_description: str = "Base documentation format"

    def __init__(self, llm_client: BaseLLMClient):
        """Initialize the generator.

        Args:
            llm_client: LLM client for generating content
        """
        self.llm_client = llm_client

    @abstractmethod
    async def generate(self, profile: CodebaseProfile, **kwargs: Any) -> list[GeneratedDoc]:
        """Generate documentation files.

        Args:
            profile: Analyzed codebase profile
            **kwargs: Additional generator-specific options

        Returns:
            List of generated documentation files
        """
        pass

    async def _generate_content(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> str:
        """Generate content using the LLM.

        Args:
            prompt: The prompt to generate from
            system_prompt: Optional system prompt

        Returns:
            Generated content
        """
        return await self.llm_client.generate(prompt, system_prompt=system_prompt)

    def _format_file_tree(self, profile: CodebaseProfile, max_depth: int = 3) -> str:
        """Format the project file tree.

        Args:
            profile: Codebase profile
            max_depth: Maximum directory depth to show

        Returns:
            Formatted file tree string
        """
        lines = [f"{profile.name}/"]

        # Group files by directory
        dirs_shown: set[str] = set()

        for file_info in profile.structure.files[:100]:  # Limit to 100 files
            parts = file_info.relative_path.split("/")

            # Show directory structure
            for i, part in enumerate(parts[:-1]):
                if i >= max_depth:
                    break
                dir_path = "/".join(parts[: i + 1])
                if dir_path not in dirs_shown:
                    indent = "  " * (i + 1)
                    lines.append(f"{indent}├── {part}/")
                    dirs_shown.add(dir_path)

            # Show file
            if len(parts) <= max_depth + 1:
                indent = "  " * len(parts)
                lines.append(f"{indent}├── {parts[-1]}")

        return "\n".join(lines[:50])  # Limit output

    def _format_dependencies(self, profile: CodebaseProfile) -> str:
        """Format dependencies information.

        Args:
            profile: Codebase profile

        Returns:
            Formatted dependencies string
        """
        if not profile.dependencies:
            return "No dependencies detected"

        lines = []
        for dep_info in profile.dependencies:
            lines.append(f"\n## {dep_info.package_manager.upper()} ({dep_info.manifest_file})")
            if dep_info.dependencies:
                lines.append("Dependencies: " + ", ".join(dep_info.dependencies[:20]))
            if dep_info.dev_dependencies:
                lines.append("Dev dependencies: " + ", ".join(dep_info.dev_dependencies[:10]))

        return "\n".join(lines)

    def _format_commands(self, profile: CodebaseProfile) -> str:
        """Format build/test/lint commands.

        Args:
            profile: Codebase profile

        Returns:
            Formatted commands string
        """
        lines = []

        if profile.build_commands:
            lines.append("Build: " + ", ".join(profile.build_commands))
        if profile.test_commands:
            lines.append("Test: " + ", ".join(profile.test_commands))
        if profile.lint_commands:
            lines.append("Lint: " + ", ".join(profile.lint_commands))

        return "\n".join(lines) if lines else "No commands detected"

    def _get_language_specific_guidelines(self, profile: CodebaseProfile) -> str:
        """Get language-specific coding guidelines.

        Args:
            profile: Codebase profile

        Returns:
            Language-specific guidelines
        """
        guidelines = {
            "python": """
- Use type hints for function parameters and return values
- Follow PEP 8 style guidelines
- Use docstrings for public functions and classes
- Prefer pathlib over os.path for path operations
- Use async/await for I/O operations where applicable
""",
            "typescript": """
- Use TypeScript strict mode
- Define interfaces for complex object shapes
- Prefer const over let, avoid var
- Use async/await over raw promises
- Export types alongside implementations
""",
            "javascript": """
- Use const/let instead of var
- Prefer arrow functions for callbacks
- Use async/await for asynchronous code
- Follow ESLint rules configured in the project
""",
            "go": """
- Follow effective Go guidelines
- Use gofmt for formatting
- Handle all errors explicitly
- Use interfaces for abstraction
- Keep packages focused and small
""",
            "rust": """
- Follow Rust API guidelines
- Use Result for recoverable errors
- Prefer &str over String for function parameters
- Use clippy for linting
- Document public APIs with rustdoc
""",
        }

        return guidelines.get(profile.primary_language, "- Follow language best practices")
