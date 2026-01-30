"""Windsurf/Codeium rules documentation generator."""

from __future__ import annotations

from typing import Any

from .base import BaseDocGenerator, GeneratedDoc
from ..analyzer import CodebaseProfile


class WindsurfDocGenerator(BaseDocGenerator):
    """Generates .windsurf/rules/*.md files for Windsurf (Codeium) Cascade.

    Windsurf uses markdown rules files that can be:
    - Always on
    - @mention-able
    - Requested by Cascade
    - Attached to file globs

    Reference: https://docs.codeium.com/windsurf/cascade
    """

    format_name = "windsurf"
    format_description = "Windsurf/Codeium Cascade rules"

    async def generate(self, profile: CodebaseProfile, **kwargs: Any) -> list[GeneratedDoc]:
        """Generate Windsurf rules documentation.

        Args:
            profile: Analyzed codebase profile
            **kwargs: Additional options

        Returns:
            List of Windsurf rule files
        """
        docs = []

        # 1. Main project rules (root .windsurfrules.md)
        main_rules = await self._generate_main_rules(profile)
        docs.append(main_rules)

        # 2. Global rules in .windsurf/rules/
        global_rules = await self._generate_global_rules(profile)
        docs.append(global_rules)

        # 3. Language-specific rules
        lang_rules = await self._generate_language_rules(profile)
        if lang_rules:
            docs.append(lang_rules)

        # 4. Testing rules
        test_rules = await self._generate_testing_rules(profile)
        docs.append(test_rules)

        # 5. API rules if applicable
        if profile.api_style:
            api_rules = await self._generate_api_rules(profile)
            docs.append(api_rules)

        return docs

    async def _generate_main_rules(self, profile: CodebaseProfile) -> GeneratedDoc:
        """Generate main project rules file."""
        sections = []

        sections.append(f"# {profile.name} - Project Rules")
        sections.append("")

        # Project overview
        if profile.description:
            sections.append(profile.description)
            sections.append("")

        # Tech stack
        sections.append("## Technology Stack")
        sections.append("")
        sections.append(f"- **Primary Language**: {profile.primary_language.capitalize()}")
        if profile.frameworks:
            sections.append(f"- **Frameworks**: {', '.join(profile.frameworks)}")
        if profile.api_style:
            sections.append(f"- **API Style**: {profile.api_style}")
        if profile.architecture_patterns:
            sections.append(f"- **Architecture**: {', '.join(profile.architecture_patterns)}")
        sections.append("")

        # Development commands
        sections.append("## Commands")
        sections.append("")
        if profile.build_commands:
            sections.append(f"- Build: `{profile.build_commands[0]}`")
        if profile.test_commands:
            sections.append(f"- Test: `{profile.test_commands[0]}`")
        if profile.lint_commands:
            sections.append(f"- Lint: `{profile.lint_commands[0]}`")
        sections.append("")

        # Project structure
        sections.append("## Project Structure")
        sections.append("")
        structure = self._format_project_structure(profile)
        sections.append(structure)
        sections.append("")

        # Code style
        sections.append("## Code Style")
        sections.append("")
        if profile.code_style:
            sections.append(f"Tools: {', '.join(profile.code_style.keys())}")
        if profile.naming_conventions:
            for item, conv in profile.naming_conventions.items():
                sections.append(f"- {item}: {conv}")
        sections.append("")

        # General guidelines
        sections.append("## Guidelines")
        sections.append("")
        guidelines = await self._generate_guidelines(profile)
        sections.append(guidelines)

        content = "\n".join(sections)

        return GeneratedDoc(
            path=".windsurfrules.md",
            content=content,
            format_name=self.format_name,
            description="Main Windsurf project rules",
        )

    async def _generate_global_rules(self, profile: CodebaseProfile) -> GeneratedDoc:
        """Generate global rules file."""
        sections = []

        sections.append("# Global Development Rules")
        sections.append("")
        sections.append("These rules apply to all code in this repository.")
        sections.append("")

        # Code quality rules
        sections.append("## Code Quality")
        sections.append("")
        sections.append("- Write clean, readable code")
        sections.append("- Follow existing patterns in the codebase")
        sections.append("- Keep functions focused and small")
        sections.append("- Add meaningful comments for complex logic")
        sections.append("- Handle errors appropriately")
        sections.append("")

        # Documentation rules
        sections.append("## Documentation")
        sections.append("")
        sections.append("- Document public APIs and functions")
        sections.append("- Keep comments up to date with code changes")
        sections.append("- Use clear, descriptive names")
        sections.append("")

        # Testing rules
        sections.append("## Testing")
        sections.append("")
        sections.append("- Write tests for new functionality")
        sections.append("- Test edge cases and error conditions")
        sections.append("- Keep tests focused and independent")
        sections.append("")

        # Security rules
        sections.append("## Security")
        sections.append("")
        sections.append("- Never commit secrets or credentials")
        sections.append("- Validate and sanitize input data")
        sections.append("- Use parameterized queries for database operations")
        sections.append("- Follow OWASP security guidelines")

        content = "\n".join(sections)

        return GeneratedDoc(
            path=".windsurf/rules/global.md",
            content=content,
            format_name=self.format_name,
            description="Global Windsurf rules for all code",
        )

    async def _generate_language_rules(self, profile: CodebaseProfile) -> GeneratedDoc | None:
        """Generate language-specific rules."""
        lang = profile.primary_language
        rules = self._get_language_rules(lang)

        if not rules:
            return None

        sections = []
        sections.append(f"# {lang.capitalize()} Development Rules")
        sections.append("")
        sections.append(f"Rules specific to {lang.capitalize()} code in this project.")
        sections.append("")
        sections.append("## Coding Standards")
        sections.append("")
        sections.append(rules)
        sections.append("")

        # Add framework-specific rules
        for framework in profile.frameworks[:2]:
            fw_rules = self._get_framework_rules(framework)
            if fw_rules:
                sections.append(f"## {framework.capitalize()} Guidelines")
                sections.append("")
                sections.append(fw_rules)
                sections.append("")

        content = "\n".join(sections)

        return GeneratedDoc(
            path=f".windsurf/rules/{lang}.md",
            content=content,
            format_name=self.format_name,
            description=f"{lang.capitalize()} language rules",
        )

    async def _generate_testing_rules(self, profile: CodebaseProfile) -> GeneratedDoc:
        """Generate testing rules."""
        sections = []

        sections.append("# Testing Rules")
        sections.append("")

        # Test commands
        sections.append("## Running Tests")
        sections.append("")
        if profile.test_commands:
            sections.append("```bash")
            for cmd in profile.test_commands[:3]:
                sections.append(cmd)
            sections.append("```")
        sections.append("")

        # Test directories
        if profile.structure.test_directories:
            sections.append("## Test Locations")
            sections.append("")
            for dir in profile.structure.test_directories[:5]:
                sections.append(f"- `{dir}/`")
            sections.append("")

        # Testing conventions
        sections.append("## Conventions")
        sections.append("")
        conventions = self._get_testing_conventions(profile)
        sections.append(conventions)

        content = "\n".join(sections)

        return GeneratedDoc(
            path=".windsurf/rules/testing.md",
            content=content,
            format_name=self.format_name,
            description="Testing rules and conventions",
        )

    async def _generate_api_rules(self, profile: CodebaseProfile) -> GeneratedDoc:
        """Generate API development rules."""
        sections = []

        sections.append(f"# {profile.api_style} API Rules")
        sections.append("")

        # API style-specific guidelines
        if profile.api_style == "REST":
            sections.append("""## REST API Guidelines

- Use proper HTTP methods:
  - GET for retrieving resources
  - POST for creating resources
  - PUT/PATCH for updating resources
  - DELETE for removing resources
- Return appropriate status codes
- Use consistent URL patterns
- Validate request input
- Document with OpenAPI/Swagger
""")
        elif profile.api_style == "GraphQL":
            sections.append("""## GraphQL Guidelines

- Define clear type schemas
- Use resolvers for data fetching
- Implement proper error handling
- Use DataLoader for batching
- Document queries and mutations
""")
        elif profile.api_style == "gRPC":
            sections.append("""## gRPC Guidelines

- Define services in .proto files
- Use streaming appropriately
- Handle deadlines and cancellation
- Implement proper error codes
- Version your APIs
""")

        # General API rules
        sections.append("""## General API Rules

- Always validate input data
- Return consistent error responses
- Handle authentication/authorization
- Implement rate limiting where appropriate
- Log important operations
- Write integration tests
""")

        content = "\n".join(sections)

        return GeneratedDoc(
            path=".windsurf/rules/api.md",
            content=content,
            format_name=self.format_name,
            description="API development rules",
        )

    def _format_project_structure(self, profile: CodebaseProfile) -> str:
        """Format project structure for display."""
        lines = []
        key_dirs = set()

        important_dirs = [
            "src", "lib", "api", "app", "components", "services",
            "models", "tests", "test", "config", "scripts", "public"
        ]

        for d in profile.structure.directories:
            top = d.split("/")[0]
            if top in important_dirs and top not in key_dirs:
                key_dirs.add(top)
                lines.append(f"- `{top}/` - {self._get_dir_description(top)}")

        return "\n".join(lines[:8]) if lines else "Standard project structure"

    def _get_dir_description(self, dir_name: str) -> str:
        """Get description for a directory."""
        descriptions = {
            "src": "Source code",
            "lib": "Library code",
            "api": "API endpoints",
            "app": "Application code",
            "components": "UI components",
            "services": "Business logic",
            "models": "Data models",
            "tests": "Test files",
            "test": "Test files",
            "config": "Configuration",
            "scripts": "Utility scripts",
            "public": "Static assets",
        }
        return descriptions.get(dir_name, "Project files")

    async def _generate_guidelines(self, profile: CodebaseProfile) -> str:
        """Generate development guidelines."""
        prompt = f"""Generate 6-8 concise development guidelines for this project.
Be specific and actionable.

Project:
- Language: {profile.primary_language}
- Frameworks: {', '.join(profile.frameworks) if profile.frameworks else 'None'}
- Architecture: {', '.join(profile.architecture_patterns) if profile.architecture_patterns else 'Standard'}

Format as markdown bullet points."""

        try:
            result = await self._generate_content(
                prompt,
                "You are a senior developer writing guidelines for an AI coding assistant."
            )
            lines = [l for l in result.strip().split("\n") if l.strip().startswith("-")]
            return "\n".join(lines[:8])
        except Exception:
            return self._get_language_specific_guidelines(profile)

    def _get_language_rules(self, lang: str) -> str:
        """Get language-specific rules."""
        rules = {
            "python": """- Use type hints for function signatures
- Write docstrings for public functions
- Use async/await for I/O operations
- Prefer pathlib over os.path
- Use dataclasses or Pydantic for data structures
- Follow PEP 8 style guidelines""",
            "typescript": """- Enable strict mode
- Define interfaces for complex types
- Use explicit return types
- Prefer async/await over Promise chains
- Avoid 'any' type
- Use readonly where applicable""",
            "javascript": """- Use const/let, never var
- Use arrow functions for callbacks
- Use async/await for async operations
- Destructure objects and arrays
- Use template literals for strings""",
            "go": """- Handle all errors explicitly
- Use meaningful names
- Keep functions small
- Use interfaces for abstraction
- Follow effective Go guidelines""",
            "rust": """- Use Result for recoverable errors
- Prefer &str over String for params
- Use clippy for linting
- Document public APIs
- Use iterators over explicit loops""",
        }
        return rules.get(lang, "")

    def _get_framework_rules(self, framework: str) -> str:
        """Get framework-specific rules."""
        rules = {
            "react": """- Use functional components
- Keep components small
- Use proper hooks
- Handle loading/error states""",
            "fastapi": """- Use Pydantic models
- Use async endpoints
- Handle errors with HTTPException
- Document with OpenAPI""",
            "nextjs": """- Use App Router
- Implement proper data fetching
- Use server components where possible""",
            "django": """- Follow Django conventions
- Use class-based views appropriately
- Implement proper validation""",
            "express": """- Use middleware for cross-cutting concerns
- Implement proper error handling
- Validate input data""",
        }
        return rules.get(framework, "")

    def _get_testing_conventions(self, profile: CodebaseProfile) -> str:
        """Get testing conventions."""
        lang = profile.primary_language
        conventions = {
            "python": """- Use pytest for testing
- Name tests with test_ prefix
- Use fixtures for setup
- Mock external dependencies
- Use parametrize for multiple cases""",
            "typescript": """- Use Jest or Vitest
- Use describe/it blocks
- Mock external modules
- Test success and error cases
- Write integration tests for APIs""",
            "javascript": """- Use Jest for testing
- Use meaningful test names
- Mock dependencies
- Test error handling""",
            "go": """- Use _test.go files
- Use table-driven tests
- Use testify for assertions
- Mock interfaces""",
            "rust": """- Use #[cfg(test)] modules
- Write integration tests in tests/
- Use proptest for property testing""",
        }
        return conventions.get(lang, """- Write comprehensive tests
- Test edge cases
- Mock external dependencies
- Keep tests focused""")
