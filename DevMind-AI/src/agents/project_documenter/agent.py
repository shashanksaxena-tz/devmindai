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
from .generators.aider import AiderDocGenerator
from .generators.cline import ClineDocGenerator
from .generators.opencode import OpenCodeDocGenerator

# Per-folder documentation components
from .folder_analyzer import FolderAnalyzer
from .per_folder_generator import PerFolderGenerator
from .smart_merger import SmartMerger
from .metadata_manager import MetadataManager
from .index_builder import IndexBuilder


class ProjectDocumenterAgent(BaseAgent):
    """Agent that generates documentation for existing codebases.

    This agent analyzes a project and generates documentation in multiple formats:

    **AI Agent Formats:**
    - `claude`: CLAUDE.md for Claude Code
    - `copilot`: .github/copilot-instructions.md for GitHub Copilot
    - `cursor`: .cursor/rules/*.mdc for Cursor AI
    - `gemini`: GEMINI.md for Google Gemini Code Assist
    - `windsurf`: .windsurf/rules/*.md for Windsurf/Codeium
    - `aider`: CONVENTIONS.md and .aider.conf.yml for Aider
    - `cline`: .clinerules/*.md for Cline VS Code extension
    - `opencode`: AGENTS.md and .opencode.json for OpenCode

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
        "aider",
        "cline",
        "opencode",
        "speckit",
        "human",
    ]

    # Default formats (AI-focused)
    DEFAULT_FORMATS = ["claude", "copilot", "cursor", "gemini", "windsurf", "aider", "cline", "opencode"]

    def __init__(self, router: LLMRouter | None = None):
        """Initialize the Project Documenter agent.

        Args:
            router: LLM router instance (uses global if not provided)
        """
        super().__init__(router)
        self.analyzer = CodebaseAnalyzer()

        # Per-folder documentation components
        self.folder_analyzer = FolderAnalyzer()
        self.per_folder_generator = PerFolderGenerator(self.llm_client)
        self.smart_merger = SmartMerger()
        self.metadata_manager = MetadataManager()
        self.index_builder = IndexBuilder()

        # Initialize generators
        self._generators = {
            "claude": ClaudeDocGenerator(self.llm_client),
            "copilot": CopilotDocGenerator(self.llm_client),
            "cursor": CursorDocGenerator(self.llm_client),
            "gemini": GeminiDocGenerator(self.llm_client),
            "windsurf": WindsurfDocGenerator(self.llm_client),
            "aider": AiderDocGenerator(self.llm_client),
            "cline": ClineDocGenerator(self.llm_client),
            "opencode": OpenCodeDocGenerator(self.llm_client),
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
                per_folder_docs: Generate per-folder AI-CONTEXT.md and README.md (default: True)
                incremental: Only regenerate changed folders (default: False)

        Returns:
            Dictionary with:
                - profile: Analyzed codebase profile
                - generated_docs: List of generated documentation files
                - written_files: List of files written (if write_files=True)
                - output_path: Path to output directory
                - folder_docs_count: Number of per-folder docs generated
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
                            content=f"Error generating {format_name} docs: {e!s}",
                            format_name=format_name,
                            description=f"Error generating {format_name}",
                        )
                    )

        # Generate per-folder documentation
        folder_docs: list[GeneratedDoc] = []
        folder_docs_count = 0

        if kwargs.get("per_folder_docs", True):
            try:
                folder_docs, folder_docs_count = await self._generate_per_folder_docs(
                    project_path=project_path,
                    profile=profile,
                    incremental=kwargs.get("incremental", False),
                    write_files=kwargs.get("write_files", False),
                )
                generated_docs.extend(folder_docs)

                # Add navigation index to top-level docs
                folders = self.folder_analyzer.analyze_folders(project_path)
                for doc in generated_docs:
                    if doc.format_name in ["claude", "copilot", "cursor", "gemini"]:
                        doc.content = self.index_builder.add_module_index(
                            doc.content, folders, link_to="AI-CONTEXT.md"
                        )
                    elif doc.format_name == "human" and "README" in doc.path:
                        doc.content = self.index_builder.add_folder_structure(
                            doc.content, folders, link_to="README.md"
                        )
            except Exception as e:
                # Log error but continue
                folder_docs.append(
                    GeneratedDoc(
                        path="error_per_folder.txt",
                        content=f"Error generating per-folder docs: {e!s}",
                        format_name="per_folder",
                        description="Error in per-folder generation",
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
            "folder_docs_count": folder_docs_count,
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

    async def _generate_per_folder_docs(
        self,
        project_path: Path,
        profile: CodebaseProfile,
        incremental: bool = False,
        write_files: bool = False,
    ) -> tuple[list[GeneratedDoc], int]:
        """Generate per-folder documentation (AI-CONTEXT.md and README.md).

        Args:
            project_path: Root path of the project
            profile: Analyzed codebase profile
            incremental: Only regenerate changed folders
            write_files: Whether to write files to disk

        Returns:
            Tuple of (list of generated docs, count of folders processed)
        """
        folder_docs: list[GeneratedDoc] = []
        folders_processed = 0

        # Initialize metadata manager
        self.metadata_manager.initialize(project_path)

        # Analyze folders
        folders = self.folder_analyzer.analyze_folders(project_path)

        # Filter for incremental mode
        if incremental:
            folders = [
                f for f in folders if self.metadata_manager.has_folder_changed(f.path)
            ]

        # Generate docs for each folder
        for folder_info in folders:
            try:
                # Generate AI-CONTEXT.md
                ai_context = await self.per_folder_generator.generate_ai_context(
                    folder_info, profile
                )

                # Smart merge if exists
                ai_context_path = folder_info.path / "AI-CONTEXT.md"
                if ai_context_path.exists():
                    try:
                        existing_content = ai_context_path.read_text(encoding="utf-8")
                        if self.smart_merger.has_markers(existing_content):
                            ai_context.content = self.smart_merger.merge(
                                existing_content, ai_context.content
                            )
                    except Exception:
                        pass  # Use fresh content if merge fails

                folder_docs.append(ai_context)

                # Generate README.md
                readme = await self.per_folder_generator.generate_readme(
                    folder_info, profile
                )

                # Smart merge if exists
                readme_path = folder_info.path / "README.md"
                if readme_path.exists():
                    try:
                        existing_content = readme_path.read_text(encoding="utf-8")
                        if self.smart_merger.has_markers(existing_content):
                            readme.content = self.smart_merger.merge(
                                existing_content, readme.content
                            )
                    except Exception:
                        pass  # Use fresh content if merge fails

                folder_docs.append(readme)

                # Update metadata if writing files
                if write_files:
                    self.metadata_manager.update_folder(
                        folder_info.path, folder_info.file_count
                    )

                folders_processed += 1

            except Exception as e:
                # Log error but continue with other folders
                folder_docs.append(
                    GeneratedDoc(
                        path=f"error_{folder_info.relative_path}.txt",
                        content=f"Error generating docs for {folder_info.relative_path}: {e!s}",
                        format_name="per_folder",
                        description=f"Error for {folder_info.relative_path}",
                    )
                )

        # Mark full run complete if not incremental
        if not incremental and write_files:
            self.metadata_manager.mark_full_run()

        return folder_docs, folders_processed

