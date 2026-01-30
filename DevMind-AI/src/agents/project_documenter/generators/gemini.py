"""Google Gemini Code Assist GEMINI.md documentation generator."""

from __future__ import annotations

from typing import Any

from .base import BaseDocGenerator, GeneratedDoc
from ..analyzer import CodebaseProfile


class GeminiDocGenerator(BaseDocGenerator):
    """Generates GEMINI.md files for Google Gemini Code Assist / Gemini CLI.

    GEMINI.md provides instructional context to the Gemini model with
    project-specific instructions, persona definitions, and coding style guides.
    Supports hierarchical context (global, project, subdirectory).

    Reference: https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html
    """

    format_name = "gemini"
    format_description = "GEMINI.md for Google Gemini Code Assist"

    async def generate(self, profile: CodebaseProfile, **kwargs: Any) -> list[GeneratedDoc]:
        """Generate GEMINI.md documentation.

        Args:
            profile: Analyzed codebase profile
            **kwargs: Additional options
                - include_subdirs: Generate subdirectory-specific files

        Returns:
            List of GEMINI.md files
        """
        docs = []

        # Main project GEMINI.md
        main_doc = await self._generate_main_gemini_md(profile)
        docs.append(main_doc)

        # Generate subdirectory GEMINI.md files if requested
        if kwargs.get("include_subdirs", True):
            subdir_docs = await self._generate_subdirectory_docs(profile)
            docs.extend(subdir_docs)

        return docs

    async def _generate_main_gemini_md(self, profile: CodebaseProfile) -> GeneratedDoc:
        """Generate the main project GEMINI.md."""
        sections = []

        # Project header
        sections.append(f"# {profile.name}")
        sections.append("")
        if profile.description:
            sections.append(profile.description)
            sections.append("")

        # Project context
        sections.append("## Project Context")
        sections.append("")
        sections.append(f"This is a {profile.primary_language.capitalize()} project.")
        if profile.frameworks:
            sections.append(f"Frameworks: {', '.join(profile.frameworks)}")
        if profile.architecture_patterns:
            sections.append(f"Architecture: {', '.join(profile.architecture_patterns)}")
        if profile.api_style:
            sections.append(f"API Style: {profile.api_style}")
        sections.append("")

        # Commands
        sections.append("## Development Commands")
        sections.append("")
        sections.append("```bash")
        if profile.build_commands:
            sections.append(f"# Build")
            sections.append(profile.build_commands[0])
        if profile.test_commands:
            sections.append(f"# Test")
            sections.append(profile.test_commands[0])
        if profile.lint_commands:
            sections.append(f"# Lint")
            sections.append(profile.lint_commands[0])
        sections.append("```")
        sections.append("")

        # Code style
        sections.append("## Code Style")
        sections.append("")
        if profile.code_style:
            sections.append(f"This project uses: {', '.join(profile.code_style.keys())}")
        if profile.naming_conventions:
            sections.append("")
            sections.append("### Naming Conventions")
            for item, convention in profile.naming_conventions.items():
                sections.append(f"- {item}: {convention}")
        sections.append("")

        # Coding guidelines
        sections.append("## Coding Guidelines")
        sections.append("")
        guidelines = await self._generate_guidelines(profile)
        sections.append(guidelines)
        sections.append("")

        # Project structure
        sections.append("## Project Structure")
        sections.append("")
        structure = self._format_structure(profile)
        sections.append(structure)
        sections.append("")

        # Important files
        sections.append("## Key Files")
        sections.append("")
        key_files = self._get_key_files_info(profile)
        sections.append(key_files)

        content = "\n".join(sections)

        return GeneratedDoc(
            path="GEMINI.md",
            content=content,
            format_name=self.format_name,
            description="Main Gemini Code Assist context file",
        )

    async def _generate_subdirectory_docs(self, profile: CodebaseProfile) -> list[GeneratedDoc]:
        """Generate GEMINI.md files for key subdirectories."""
        docs = []

        # Identify key directories that would benefit from specific context
        key_dirs = self._identify_key_directories(profile)

        for dir_info in key_dirs[:4]:  # Limit to 4 subdirectory docs
            doc = await self._generate_subdir_gemini_md(profile, dir_info)
            if doc:
                docs.append(doc)

        return docs

    def _identify_key_directories(self, profile: CodebaseProfile) -> list[dict]:
        """Identify directories that need specific GEMINI.md files."""
        key_dirs = []

        dir_purposes = {
            "src/api": {"purpose": "API endpoints", "type": "api"},
            "src/routes": {"purpose": "Route handlers", "type": "api"},
            "api": {"purpose": "API layer", "type": "api"},
            "src/components": {"purpose": "UI components", "type": "components"},
            "components": {"purpose": "UI components", "type": "components"},
            "src/services": {"purpose": "Business logic", "type": "services"},
            "services": {"purpose": "Business logic", "type": "services"},
            "tests": {"purpose": "Test files", "type": "tests"},
            "test": {"purpose": "Test files", "type": "tests"},
            "src/models": {"purpose": "Data models", "type": "models"},
            "models": {"purpose": "Data models", "type": "models"},
        }

        for directory in profile.structure.directories:
            for key_path, info in dir_purposes.items():
                if directory == key_path or directory.startswith(f"{key_path}/"):
                    if not any(d["path"] == key_path for d in key_dirs):
                        key_dirs.append({
                            "path": key_path,
                            "purpose": info["purpose"],
                            "type": info["type"],
                        })
                    break

        return key_dirs

    async def _generate_subdir_gemini_md(
        self, profile: CodebaseProfile, dir_info: dict
    ) -> GeneratedDoc | None:
        """Generate GEMINI.md for a specific subdirectory."""
        dir_path = dir_info["path"]
        dir_type = dir_info["type"]
        purpose = dir_info["purpose"]

        sections = []
        sections.append(f"# {purpose}")
        sections.append("")

        # Type-specific content
        if dir_type == "api":
            sections.append(await self._generate_api_context(profile))
        elif dir_type == "components":
            sections.append(await self._generate_components_context(profile))
        elif dir_type == "services":
            sections.append(await self._generate_services_context(profile))
        elif dir_type == "tests":
            sections.append(await self._generate_tests_context(profile))
        elif dir_type == "models":
            sections.append(await self._generate_models_context(profile))

        content = "\n".join(sections)

        return GeneratedDoc(
            path=f"{dir_path}/GEMINI.md",
            content=content,
            format_name=self.format_name,
            description=f"Gemini context for {purpose.lower()}",
        )

    async def _generate_guidelines(self, profile: CodebaseProfile) -> str:
        """Generate coding guidelines."""
        prompt = f"""Generate 6-8 concise coding guidelines for this {profile.primary_language} project.
Each guideline should be actionable and specific.

Context:
- Frameworks: {', '.join(profile.frameworks) if profile.frameworks else 'None'}
- Architecture: {', '.join(profile.architecture_patterns) if profile.architecture_patterns else 'Standard'}
- Code tools: {', '.join(profile.code_style.keys()) if profile.code_style else 'None'}

Format as markdown bullet points, one guideline per line."""

        try:
            result = await self._generate_content(
                prompt,
                "You are a senior developer writing guidelines for an AI coding assistant. Be specific and actionable."
            )
            lines = [l.strip() for l in result.strip().split("\n") if l.strip().startswith("-")]
            return "\n".join(lines[:8])
        except Exception:
            return self._get_language_specific_guidelines(profile)

    def _format_structure(self, profile: CodebaseProfile) -> str:
        """Format project structure."""
        lines = ["```"]
        lines.append(f"{profile.name}/")

        # Group by top-level directory
        top_dirs = set()
        for d in profile.structure.directories:
            top = d.split("/")[0]
            if top not in top_dirs:
                top_dirs.add(top)
                lines.append(f"├── {top}/")

        lines.append("```")
        return "\n".join(lines)

    def _get_key_files_info(self, profile: CodebaseProfile) -> str:
        """Get information about key files."""
        lines = []

        # Entry points
        if profile.structure.entry_points:
            lines.append(f"- Entry points: {', '.join(profile.structure.entry_points[:3])}")

        # Config files
        config_files = [f for f in profile.structure.config_files if not f.startswith(".")][:5]
        if config_files:
            lines.append(f"- Config files: {', '.join(config_files)}")

        return "\n".join(lines) if lines else "See project root for configuration files."

    async def _generate_api_context(self, profile: CodebaseProfile) -> str:
        """Generate API-specific context."""
        return f"""## API Development Guidelines

This directory contains {profile.api_style or 'API'} endpoints.

### Conventions
- Validate all input data
- Return appropriate HTTP status codes
- Handle errors consistently
- Document endpoints
- Write integration tests

### Response Format
- Use consistent response structure
- Include proper error messages
- Set appropriate headers
"""

    async def _generate_components_context(self, profile: CodebaseProfile) -> str:
        """Generate components-specific context."""
        framework = profile.frameworks[0] if profile.frameworks else "UI"
        return f"""## Component Guidelines

This directory contains {framework} components.

### Conventions
- Keep components small and focused
- Use proper prop typing
- Handle loading and error states
- Write unit tests for components
- Follow accessibility best practices
"""

    async def _generate_services_context(self, profile: CodebaseProfile) -> str:
        """Generate services-specific context."""
        return """## Service Layer Guidelines

This directory contains business logic services.

### Conventions
- Keep services focused on single responsibility
- Use dependency injection
- Handle errors appropriately
- Write unit tests with mocked dependencies
- Document public methods
"""

    async def _generate_tests_context(self, profile: CodebaseProfile) -> str:
        """Generate tests-specific context."""
        test_cmd = profile.test_commands[0] if profile.test_commands else "standard test command"
        return f"""## Testing Guidelines

Run tests: `{test_cmd}`

### Conventions
- Write descriptive test names
- Test both success and error cases
- Mock external dependencies
- Aim for high coverage on critical paths
- Use fixtures/setup for common test data
"""

    async def _generate_models_context(self, profile: CodebaseProfile) -> str:
        """Generate models-specific context."""
        return """## Data Model Guidelines

This directory contains data models and schemas.

### Conventions
- Define clear validation rules
- Use proper typing
- Document model fields
- Write serialization/deserialization methods
- Keep models focused
"""
