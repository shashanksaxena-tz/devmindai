"""Cursor AI rules documentation generator."""

from __future__ import annotations

from typing import Any

from .base import BaseDocGenerator, GeneratedDoc
from ..analyzer import CodebaseProfile


class CursorDocGenerator(BaseDocGenerator):
    """Generates .cursor/rules/*.mdc files for Cursor AI.

    Cursor uses .mdc files with frontmatter for rules that can be:
    - Always applied (alwaysApply: true)
    - Auto-attached based on glob patterns
    - Manually included with @ruleName

    Reference: https://cursor.com/docs/context/rules
    """

    format_name = "cursor"
    format_description = "Cursor AI rules (.mdc files)"

    async def generate(self, profile: CodebaseProfile, **kwargs: Any) -> list[GeneratedDoc]:
        """Generate Cursor rules documentation.

        Args:
            profile: Analyzed codebase profile
            **kwargs: Additional options

        Returns:
            List of .mdc rule files
        """
        docs = []

        # 1. Main index rule (always applied)
        index_rule = await self._generate_index_rule(profile)
        docs.append(index_rule)

        # 2. Language-specific rules
        lang_rule = await self._generate_language_rule(profile)
        if lang_rule:
            docs.append(lang_rule)

        # 3. Testing rules
        test_rule = await self._generate_testing_rule(profile)
        docs.append(test_rule)

        # 4. API rules (if applicable)
        if profile.api_style:
            api_rule = await self._generate_api_rule(profile)
            docs.append(api_rule)

        # 5. Framework-specific rules
        for framework in profile.frameworks[:2]:  # Limit to 2 framework rules
            framework_rule = await self._generate_framework_rule(profile, framework)
            if framework_rule:
                docs.append(framework_rule)

        return docs

    async def _generate_index_rule(self, profile: CodebaseProfile) -> GeneratedDoc:
        """Generate the main index.mdc rule."""
        content = f"""---
description: {profile.name} project rules
alwaysApply: true
---

# {profile.name}

{profile.description if profile.description else f"A {profile.primary_language} project."}

## Tech Stack
- Language: {profile.primary_language.capitalize()}
{self._format_list_item("Frameworks", profile.frameworks)}
{self._format_list_item("API Style", [profile.api_style] if profile.api_style else [])}

## Commands
{self._format_commands(profile)}

## Code Style
{self._format_code_style(profile)}

## Key Directories
{self._format_directories(profile)}

## Guidelines
{await self._generate_short_guidelines(profile)}
"""
        return GeneratedDoc(
            path=".cursor/rules/index.mdc",
            content=content.strip(),
            format_name=self.format_name,
            description="Main Cursor rules file (always applied)",
        )

    async def _generate_language_rule(self, profile: CodebaseProfile) -> GeneratedDoc | None:
        """Generate language-specific rule."""
        lang = profile.primary_language
        ext_map = {
            "python": "py",
            "typescript": "ts,tsx",
            "javascript": "js,jsx",
            "go": "go",
            "rust": "rs",
            "java": "java",
            "kotlin": "kt",
        }

        if lang not in ext_map:
            return None

        ext = ext_map[lang]
        glob_pattern = f"**/*.{{{ext}}}" if "," in ext else f"**/*.{ext}"

        guidelines = await self._get_language_guidelines(lang)

        content = f"""---
description: {lang.capitalize()} coding standards
globs:
  - "{glob_pattern}"
alwaysApply: false
---

# {lang.capitalize()} Guidelines

{guidelines}
"""
        return GeneratedDoc(
            path=f".cursor/rules/{lang}.mdc",
            content=content.strip(),
            format_name=self.format_name,
            description=f"{lang.capitalize()} language rules",
        )

    async def _generate_testing_rule(self, profile: CodebaseProfile) -> GeneratedDoc:
        """Generate testing rules."""
        test_globs = self._get_test_globs(profile)

        content = f"""---
description: Testing standards and conventions
globs:
{test_globs}
alwaysApply: false
---

# Testing Guidelines

## Test Commands
{self._format_test_commands(profile)}

## Conventions
{await self._generate_testing_conventions(profile)}
"""
        return GeneratedDoc(
            path=".cursor/rules/testing.mdc",
            content=content.strip(),
            format_name=self.format_name,
            description="Testing rules and conventions",
        )

    async def _generate_api_rule(self, profile: CodebaseProfile) -> GeneratedDoc:
        """Generate API development rules."""
        api_globs = self._get_api_globs(profile)

        content = f"""---
description: API development standards
globs:
{api_globs}
alwaysApply: false
---

# API Development Guidelines

## API Style: {profile.api_style}

{await self._generate_api_conventions(profile)}
"""
        return GeneratedDoc(
            path=".cursor/rules/api.mdc",
            content=content.strip(),
            format_name=self.format_name,
            description="API development rules",
        )

    async def _generate_framework_rule(
        self, profile: CodebaseProfile, framework: str
    ) -> GeneratedDoc | None:
        """Generate framework-specific rules."""
        framework_info = self._get_framework_info(framework)
        if not framework_info:
            return None

        content = f"""---
description: {framework.capitalize()} framework conventions
globs:
{framework_info['globs']}
alwaysApply: false
---

# {framework.capitalize()} Guidelines

{await self._generate_framework_conventions(profile, framework)}
"""
        return GeneratedDoc(
            path=f".cursor/rules/{framework}.mdc",
            content=content.strip(),
            format_name=self.format_name,
            description=f"{framework.capitalize()} framework rules",
        )

    def _format_list_item(self, label: str, items: list) -> str:
        """Format a list item."""
        if items:
            return f"- {label}: {', '.join(items)}"
        return ""

    def _format_commands(self, profile: CodebaseProfile) -> str:
        """Format commands section."""
        lines = []
        if profile.build_commands:
            lines.append(f"- Build: `{profile.build_commands[0]}`")
        if profile.test_commands:
            lines.append(f"- Test: `{profile.test_commands[0]}`")
        if profile.lint_commands:
            lines.append(f"- Lint: `{profile.lint_commands[0]}`")
        return "\n".join(lines) if lines else "- No commands configured"

    def _format_code_style(self, profile: CodebaseProfile) -> str:
        """Format code style section."""
        lines = []
        if profile.code_style:
            lines.append(f"- Tools: {', '.join(profile.code_style.keys())}")
        if profile.naming_conventions:
            for item, conv in list(profile.naming_conventions.items())[:3]:
                lines.append(f"- {item}: {conv}")
        return "\n".join(lines) if lines else "- Follow language defaults"

    def _format_directories(self, profile: CodebaseProfile) -> str:
        """Format key directories."""
        key_dirs = []
        important = ["src", "lib", "api", "components", "services", "models", "tests"]
        for d in profile.structure.directories:
            base = d.split("/")[0]
            if base in important and base not in key_dirs:
                key_dirs.append(base)
        return "\n".join([f"- `{d}/`" for d in key_dirs[:6]]) if key_dirs else "- Standard structure"

    async def _generate_short_guidelines(self, profile: CodebaseProfile) -> str:
        """Generate short guidelines."""
        base = self._get_language_specific_guidelines(profile)
        lines = [l.strip() for l in base.strip().split("\n") if l.strip().startswith("-")]
        return "\n".join(lines[:5])

    async def _get_language_guidelines(self, lang: str) -> str:
        """Get detailed language guidelines."""
        guidelines = {
            "python": """- Use type hints for all function signatures
- Write docstrings for public functions and classes
- Use async/await for I/O operations
- Prefer pathlib over os.path
- Use dataclasses or Pydantic for data structures
- Handle exceptions explicitly with specific exception types""",
            "typescript": """- Enable strict mode in tsconfig.json
- Define interfaces for all complex types
- Use explicit return types on functions
- Prefer async/await over Promise chains
- Use readonly where applicable
- Avoid 'any' type - use 'unknown' if type is truly unknown""",
            "javascript": """- Use const by default, let only when reassignment is needed
- Use arrow functions for callbacks and short functions
- Use template literals for string interpolation
- Use async/await for asynchronous operations
- Destructure objects and arrays where it improves readability""",
            "go": """- Handle all errors explicitly
- Use meaningful variable names
- Keep functions focused and small
- Use interfaces for abstraction
- Follow effective Go guidelines
- Use context for cancellation and timeouts""",
            "rust": """- Use Result<T, E> for recoverable errors
- Prefer &str over String for function parameters
- Use meaningful error types
- Document public items with /// comments
- Use clippy for additional linting
- Prefer iterators over explicit loops where appropriate""",
        }
        return guidelines.get(lang, "- Follow language best practices")

    def _get_test_globs(self, profile: CodebaseProfile) -> str:
        """Get test file glob patterns."""
        globs = []
        if profile.primary_language == "python":
            globs = ['  - "**/test_*.py"', '  - "**/*_test.py"', '  - "**/tests/**/*.py"']
        elif profile.primary_language in ["typescript", "javascript"]:
            globs = ['  - "**/*.test.ts"', '  - "**/*.spec.ts"', '  - "**/__tests__/**/*"']
        elif profile.primary_language == "go":
            globs = ['  - "**/*_test.go"']
        elif profile.primary_language == "rust":
            globs = ['  - "**/tests/**/*.rs"']
        else:
            globs = ['  - "**/test*"', '  - "**/spec*"']
        return "\n".join(globs)

    def _format_test_commands(self, profile: CodebaseProfile) -> str:
        """Format test commands."""
        if profile.test_commands:
            return "\n".join([f"- `{cmd}`" for cmd in profile.test_commands])
        return "- Run tests with standard tooling"

    async def _generate_testing_conventions(self, profile: CodebaseProfile) -> str:
        """Generate testing conventions."""
        lang = profile.primary_language
        conventions = {
            "python": """- Use pytest for testing
- Name test functions with test_ prefix
- Use fixtures for common setup
- Use parametrize for multiple test cases
- Mock external dependencies
- Aim for high coverage on critical paths""",
            "typescript": """- Use Jest or Vitest for testing
- Use describe/it blocks for organization
- Mock external modules and APIs
- Test both success and error cases
- Use snapshot tests sparingly
- Write integration tests for API endpoints""",
            "javascript": """- Use Jest for unit tests
- Use meaningful test descriptions
- Mock external dependencies
- Test error handling
- Use beforeEach/afterEach for setup/teardown""",
            "go": """- Place tests in same package with _test.go suffix
- Use table-driven tests for multiple cases
- Use testify/assert for cleaner assertions
- Mock interfaces, not concrete types
- Use t.Parallel() for independent tests""",
            "rust": """- Write unit tests in #[cfg(test)] modules
- Write integration tests in tests/ directory
- Use #[should_panic] for expected panics
- Use proptest for property-based testing
- Document test preconditions""",
        }
        return conventions.get(lang, "- Write comprehensive tests\n- Test edge cases\n- Mock external dependencies")

    def _get_api_globs(self, profile: CodebaseProfile) -> str:
        """Get API file glob patterns."""
        globs = []
        if profile.primary_language == "python":
            globs = ['  - "**/api/**/*.py"', '  - "**/routes/**/*.py"', '  - "**/endpoints/**/*.py"']
        elif profile.primary_language in ["typescript", "javascript"]:
            globs = ['  - "**/api/**/*"', '  - "**/routes/**/*"', '  - "**/controllers/**/*"']
        elif profile.primary_language == "go":
            globs = ['  - "**/handlers/**/*.go"', '  - "**/api/**/*.go"']
        else:
            globs = ['  - "**/api/**/*"']
        return "\n".join(globs)

    async def _generate_api_conventions(self, profile: CodebaseProfile) -> str:
        """Generate API conventions."""
        style = profile.api_style
        if style == "REST":
            return """- Use proper HTTP methods (GET, POST, PUT, DELETE, PATCH)
- Return appropriate status codes
- Use consistent URL patterns
- Validate request input
- Return structured error responses
- Document endpoints with OpenAPI/Swagger"""
        elif style == "GraphQL":
            return """- Define clear type schemas
- Use resolvers for data fetching
- Implement proper error handling
- Use DataLoader for N+1 query prevention
- Document queries and mutations"""
        elif style == "gRPC":
            return """- Define services in .proto files
- Use streaming for large data
- Implement proper error codes
- Handle deadlines and cancellation
- Version your APIs"""
        return "- Follow API best practices\n- Validate input\n- Return consistent responses"

    def _get_framework_info(self, framework: str) -> dict | None:
        """Get framework-specific glob patterns."""
        info = {
            "react": {"globs": '  - "**/*.tsx"\n  - "**/*.jsx"'},
            "vue": {"globs": '  - "**/*.vue"'},
            "nextjs": {"globs": '  - "**/app/**/*"\n  - "**/pages/**/*"'},
            "fastapi": {"globs": '  - "**/api/**/*.py"\n  - "**/routers/**/*.py"'},
            "django": {"globs": '  - "**/views.py"\n  - "**/models.py"\n  - "**/urls.py"'},
            "express": {"globs": '  - "**/routes/**/*"\n  - "**/middleware/**/*"'},
            "nestjs": {"globs": '  - "**/*.controller.ts"\n  - "**/*.service.ts"\n  - "**/*.module.ts"'},
        }
        return info.get(framework)

    async def _generate_framework_conventions(self, profile: CodebaseProfile, framework: str) -> str:
        """Generate framework-specific conventions."""
        conventions = {
            "react": """- Use functional components with hooks
- Keep components small and focused
- Use proper state management
- Memoize expensive computations
- Handle loading and error states""",
            "vue": """- Use Composition API for complex components
- Keep templates clean and readable
- Use computed properties for derived state
- Handle async operations properly""",
            "nextjs": """- Use App Router conventions
- Implement proper data fetching patterns
- Use server components where possible
- Handle loading and error states
- Optimize images with next/image""",
            "fastapi": """- Use Pydantic models for request/response
- Implement proper dependency injection
- Use async endpoints for I/O operations
- Handle errors with HTTPException
- Document with OpenAPI annotations""",
            "django": """- Follow Django conventions
- Use class-based views appropriately
- Implement proper model validation
- Use Django REST framework for APIs
- Write model tests""",
            "express": """- Use middleware for cross-cutting concerns
- Implement proper error handling
- Validate request input
- Use async/await with proper error handling
- Structure routes logically""",
            "nestjs": """- Use decorators appropriately
- Implement proper dependency injection
- Use DTOs for validation
- Handle exceptions with filters
- Write unit and e2e tests""",
        }
        return conventions.get(framework, f"- Follow {framework} best practices")
