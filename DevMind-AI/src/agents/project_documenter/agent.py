"""Project Documenter Agent - Generates AI-ready documentation for existing codebases.

This agent analyzes codebases and generates documentation in multiple formats
for both AI coding assistants and human developers.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from src.agents.base import BaseAgent, AgentContext
from src.core.llm import TaskComplexity, LLMRouter

from .analyzer import CodebaseAnalyzer, CodebaseProfile
from .output_manager import OutputManager
from .generators.base import GeneratedDoc
from .generators.claude import ClaudeDocGenerator
from .generators.copilot import CopilotDocGenerator
from .generators.cursor import CursorDocGenerator
from .generators.gemini import GeminiDocGenerator
from .generators.windsurf import WindsurfDocGenerator
from .generators.speckit import SpecKitGenerator
from .generators.human import HumanDocGenerator


class ProjectDocumenterAgent(BaseAgent):
    """Agent that generates documentation for existing codebases.

    This agent analyzes a project and generates documentation in multiple formats:

    **AI Agent Formats:**
    - `claude`: CLAUDE.md for Claude Code
    - `copilot`: .github/copilot-instructions.md for GitHub Copilot
    - `cursor`: .cursor/rules/*.mdc for Cursor AI
    - `gemini`: GEMINI.md for Google Gemini Code Assist
    - `windsurf`: .windsurf/rules/*.md for Windsurf/Codeium

    **Governance Formats:**
    - `speckit`: GitHub Spec Kit constitution files (.specify/memory/)

    **Human Formats:**
    - `human`: README, ARCHITECTURE, CONTRIBUTING docs

    Usage:
        agent = ProjectDocumenterAgent()
        result = await agent.execute(
            context,
            path="/path/to/project",
            formats=["claude", "copilot", "cursor", "gemini", "windsurf"],
            write_files=True
        )
    """

    name = "project_documenter"
    description = "Generates AI-agent and human documentation for existing codebases"
    complexity = TaskComplexity.MODERATE

    # All available output formats
    AVAILABLE_FORMATS = [
        "claude",
        "copilot",
        "cursor",
        "gemini",
        "windsurf",
        "speckit",
        "human",
    ]

    # Default formats (AI-focused)
    DEFAULT_FORMATS = ["claude", "copilot", "cursor", "gemini", "windsurf"]

    def __init__(self, router: LLMRouter | None = None):
        """Initialize the Project Documenter agent.

        Args:
            router: LLM router instance (uses global if not provided)
        """
        super().__init__(router)
        self.analyzer = CodebaseAnalyzer()

        # Initialize generators
        self._generators = {
            "claude": ClaudeDocGenerator(self.llm_client),
            "copilot": CopilotDocGenerator(self.llm_client),
            "cursor": CursorDocGenerator(self.llm_client),
            "gemini": GeminiDocGenerator(self.llm_client),
            "windsurf": WindsurfDocGenerator(self.llm_client),
            "speckit": SpecKitGenerator(self.llm_client),
            "human": HumanDocGenerator(self.llm_client),
        }

    async def execute(
        self,
        context: AgentContext,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Execute the documentation generation.

        Args:
            context: Execution context
            **kwargs:
                path: Path to the project to analyze (required)
                formats: List of output formats (default: all AI formats)
                write_files: Whether to write files to disk (default: False)
                output_to_project: Write directly to project (default: False)
                output_dir: Custom output directory (default: devmind-output/)
                include_human: Include human-readable docs (default: False)
                include_speckit: Include Spec Kit constitution (default: False)
                generator_options: Dict of format-specific options

        Returns:
            Dictionary with:
                - profile: Analyzed codebase profile
                - generated_docs: List of generated documentation files
                - written_files: List of files written (if write_files=True)
                - output_path: Path to output directory
        """
        path = kwargs.get("path")
        if not path:
            return {"error": "Path to project is required"}

        # Resolve path
        project_path = Path(path).resolve()
        if not project_path.exists():
            return {"error": f"Path does not exist: {path}"}

        # Determine formats to generate
        formats = kwargs.get("formats", self.DEFAULT_FORMATS.copy())

        # Handle convenience flags
        if kwargs.get("include_human", False) and "human" not in formats:
            formats.append("human")
        if kwargs.get("include_speckit", False) and "speckit" not in formats:
            formats.append("speckit")
        if kwargs.get("all_formats", False):
            formats = self.AVAILABLE_FORMATS.copy()

        # Validate formats
        invalid_formats = [f for f in formats if f not in self.AVAILABLE_FORMATS]
        if invalid_formats:
            return {"error": f"Invalid formats: {invalid_formats}. Available: {self.AVAILABLE_FORMATS}"}

        # Analyze the codebase
        try:
            profile = self.analyzer.analyze(str(project_path))
        except Exception as e:
            return {"error": f"Failed to analyze codebase: {str(e)}"}

        # Generate documentation
        generated_docs: list[GeneratedDoc] = []
        generator_options = kwargs.get("generator_options", {})

        for format_name in formats:
            generator = self._generators.get(format_name)
            if generator:
                try:
                    options = generator_options.get(format_name, {})
                    docs = await generator.generate(profile, **options)
                    generated_docs.extend(docs)
                except Exception as e:
                    # Log error but continue with other formats
                    generated_docs.append(
                        GeneratedDoc(
                            path=f"error_{format_name}.txt",
                            content=f"Error generating {format_name} docs: {str(e)}",
                            format_name=format_name,
                            description=f"Error generating {format_name}",
                        )
                    )

        # Prepare result
        profile_dict = self._profile_to_dict(profile)
        doc_list = [
            {
                "path": doc.path,
                "format": doc.format_name,
                "description": doc.description,
                "content_preview": doc.content[:500] + "..." if len(doc.content) > 500 else doc.content,
                "content": doc.content,  # Full content for internal use
            }
            for doc in generated_docs
        ]
        formats_generated = list(set(doc.format_name for doc in generated_docs if not doc.path.startswith("error_")))

        # Write files if requested
        written_files = []
        output_path = None
        readme_path = None

        if kwargs.get("write_files", False):
            output_to_project = kwargs.get("output_to_project", False)
            custom_output_dir = kwargs.get("output_dir")

            if output_to_project:
                # Write directly to project directory
                written_files = await self._write_files(project_path, generated_docs)
                output_path = str(project_path)
            else:
                # Use organized output manager
                output_manager = OutputManager(
                    base_path=Path(custom_output_dir) if custom_output_dir else None,
                    project_name=profile.name,
                )

                # Write organized docs
                written_files = output_manager.write_docs(generated_docs, organize_by_format=True)

                # Write summary README
                readme_path = output_manager.write_readme(
                    profile_dict, doc_list, formats_generated
                )

                output_path = str(output_manager.output_path)

        # Remove full content from public result
        for doc in doc_list:
            doc.pop("content", None)

        return {
            "success": True,
            "profile": profile_dict,
            "generated_docs": doc_list,
            "written_files": written_files,
            "formats_generated": formats_generated,
            "output_path": output_path,
            "readme_path": readme_path,
        }

    async def analyze_only(
        self,
        path: str,
    ) -> CodebaseProfile:
        """Analyze a codebase without generating documentation.

        Args:
            path: Path to the project

        Returns:
            CodebaseProfile with analysis results
        """
        return self.analyzer.analyze(path)

    async def generate_format(
        self,
        profile: CodebaseProfile,
        format_name: str,
        **options: Any,
    ) -> list[GeneratedDoc]:
        """Generate documentation for a specific format.

        Args:
            profile: Analyzed codebase profile
            format_name: Output format to generate
            **options: Format-specific options

        Returns:
            List of generated documentation files
        """
        generator = self._generators.get(format_name)
        if not generator:
            raise ValueError(f"Unknown format: {format_name}")

        return await generator.generate(profile, **options)

    async def _write_files(
        self,
        root_path: Path,
        docs: list[GeneratedDoc],
    ) -> list[str]:
        """Write generated documentation files to disk.

        Args:
            root_path: Root path of the project
            docs: List of generated documents

        Returns:
            List of written file paths
        """
        written = []

        for doc in docs:
            if doc.path.startswith("error_"):
                continue  # Skip error placeholders

            file_path = root_path / doc.path

            # Create directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Check if file exists and whether to overwrite
            if file_path.exists() and not doc.overwrite:
                continue

            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(doc.content)
                written.append(str(file_path))
            except Exception as e:
                # Log error but continue
                pass

        return written

    def _profile_to_dict(self, profile: CodebaseProfile) -> dict[str, Any]:
        """Convert CodebaseProfile to a serializable dictionary."""
        return {
            "name": profile.name,
            "root_path": profile.root_path,
            "description": profile.description,
            "primary_language": profile.primary_language,
            "languages": profile.languages,
            "frameworks": profile.frameworks,
            "architecture_patterns": profile.architecture_patterns,
            "api_style": profile.api_style,
            "has_git": profile.has_git,
            "default_branch": profile.default_branch,
            "build_commands": profile.build_commands,
            "test_commands": profile.test_commands,
            "lint_commands": profile.lint_commands,
            "code_style": profile.code_style,
            "naming_conventions": profile.naming_conventions,
            "existing_docs": profile.existing_docs,
            "file_count": len(profile.structure.files),
            "directory_count": len(profile.structure.directories),
        }

    def get_available_formats(self) -> list[str]:
        """Get list of available output formats.

        Returns:
            List of format names
        """
        return self.AVAILABLE_FORMATS.copy()

    def get_format_description(self, format_name: str) -> str:
        """Get description of a specific format.

        Args:
            format_name: Name of the format

        Returns:
            Format description
        """
        generator = self._generators.get(format_name)
        if generator:
            return generator.format_description
        return f"Unknown format: {format_name}"
