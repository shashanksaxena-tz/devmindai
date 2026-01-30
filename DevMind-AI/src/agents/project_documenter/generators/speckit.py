"""GitHub Spec Kit constitution generator."""

from __future__ import annotations

from typing import Any

from .base import BaseDocGenerator, GeneratedDoc
from ..analyzer import CodebaseProfile


class SpecKitGenerator(BaseDocGenerator):
    """Generates GitHub Spec Kit constitution files.

    The constitution establishes foundational governance principles and development
    guidelines for spec-driven development. It creates a persistent governance
    document that AI agents reference throughout specification, planning, and
    implementation phases.

    Reference: https://github.com/github/spec-kit
    """

    format_name = "speckit"
    format_description = "GitHub Spec Kit constitution"

    async def generate(self, profile: CodebaseProfile, **kwargs: Any) -> list[GeneratedDoc]:
        """Generate Spec Kit constitution files.

        Args:
            profile: Analyzed codebase profile
            **kwargs: Additional options

        Returns:
            List of Spec Kit files
        """
        docs = []

        # 1. Main constitution file
        constitution = await self._generate_constitution(profile)
        docs.append(constitution)

        # 2. Tech stack context file
        tech_context = await self._generate_tech_context(profile)
        docs.append(tech_context)

        # 3. Architecture context file
        arch_context = await self._generate_architecture_context(profile)
        docs.append(arch_context)

        return docs

    async def _generate_constitution(self, profile: CodebaseProfile) -> GeneratedDoc:
        """Generate the main constitution file."""
        sections = []

        # Header
        sections.append(f"# {profile.name} Constitution")
        sections.append("")
        sections.append("This document establishes the non-negotiable principles and governance")
        sections.append("guidelines for this project. All specifications, plans, and implementations")
        sections.append("must align with these principles.")
        sections.append("")

        # Article I: Project Identity
        sections.append("## Article I: Project Identity")
        sections.append("")
        if profile.description:
            sections.append(f"**Purpose**: {profile.description}")
        sections.append(f"**Primary Language**: {profile.primary_language.capitalize()}")
        if profile.frameworks:
            sections.append(f"**Core Frameworks**: {', '.join(profile.frameworks)}")
        if profile.api_style:
            sections.append(f"**API Style**: {profile.api_style}")
        sections.append("")

        # Article II: Code Quality Standards
        sections.append("## Article II: Code Quality Standards")
        sections.append("")
        sections.append("All code contributions MUST adhere to the following standards:")
        sections.append("")
        quality_standards = await self._generate_quality_standards(profile)
        sections.append(quality_standards)
        sections.append("")

        # Article III: Testing Requirements
        sections.append("## Article III: Testing Requirements")
        sections.append("")
        sections.append("All features MUST include appropriate tests:")
        sections.append("")
        testing_reqs = self._generate_testing_requirements(profile)
        sections.append(testing_reqs)
        sections.append("")

        # Article IV: Documentation Requirements
        sections.append("## Article IV: Documentation Requirements")
        sections.append("")
        sections.append("All public APIs and significant features MUST be documented:")
        sections.append("")
        doc_reqs = self._generate_documentation_requirements(profile)
        sections.append(doc_reqs)
        sections.append("")

        # Article V: Security Requirements
        sections.append("## Article V: Security Requirements")
        sections.append("")
        sections.append("All code MUST follow security best practices:")
        sections.append("")
        security_reqs = self._generate_security_requirements()
        sections.append(security_reqs)
        sections.append("")

        # Article VI: Architecture Constraints
        sections.append("## Article VI: Architecture Constraints")
        sections.append("")
        arch_constraints = await self._generate_architecture_constraints(profile)
        sections.append(arch_constraints)
        sections.append("")

        # Article VII: Development Workflow
        sections.append("## Article VII: Development Workflow")
        sections.append("")
        workflow = self._generate_workflow_requirements(profile)
        sections.append(workflow)
        sections.append("")

        # Article VIII: Performance Requirements
        sections.append("## Article VIII: Performance Requirements")
        sections.append("")
        sections.append("All implementations SHOULD consider performance:")
        sections.append("")
        sections.append("1. Avoid premature optimization, but consider scalability")
        sections.append("2. Use appropriate data structures for the use case")
        sections.append("3. Consider memory usage for large datasets")
        sections.append("4. Implement caching where beneficial")
        sections.append("5. Profile and optimize critical paths")
        sections.append("")

        # Article IX: Compatibility Requirements
        sections.append("## Article IX: Compatibility Requirements")
        sections.append("")
        compat_reqs = self._generate_compatibility_requirements(profile)
        sections.append(compat_reqs)

        content = "\n".join(sections)

        return GeneratedDoc(
            path=".specify/memory/constitution.md",
            content=content,
            format_name=self.format_name,
            description="GitHub Spec Kit constitution - governance principles",
        )

    async def _generate_tech_context(self, profile: CodebaseProfile) -> GeneratedDoc:
        """Generate tech stack context file."""
        sections = []

        sections.append("# Technology Context")
        sections.append("")
        sections.append("This file provides context about the technology stack for AI agents")
        sections.append("working on specifications and implementations.")
        sections.append("")

        # Languages
        sections.append("## Languages")
        sections.append("")
        sections.append(f"**Primary**: {profile.primary_language.capitalize()}")
        if len(profile.languages) > 1:
            others = [l for l in profile.languages.keys() if l != profile.primary_language]
            if others:
                sections.append(f"**Secondary**: {', '.join(others)}")
        sections.append("")

        # Frameworks
        sections.append("## Frameworks & Libraries")
        sections.append("")
        if profile.frameworks:
            for fw in profile.frameworks:
                sections.append(f"- {fw}")
        else:
            sections.append("No specific frameworks detected.")
        sections.append("")

        # Dependencies
        sections.append("## Key Dependencies")
        sections.append("")
        for dep_info in profile.dependencies[:2]:
            sections.append(f"### {dep_info.package_manager.upper()}")
            if dep_info.dependencies[:15]:
                sections.append(f"- {', '.join(dep_info.dependencies[:15])}")
            sections.append("")

        # Build/Test Commands
        sections.append("## Development Commands")
        sections.append("")
        sections.append("```bash")
        if profile.build_commands:
            sections.append(f"# Build: {profile.build_commands[0]}")
        if profile.test_commands:
            sections.append(f"# Test: {profile.test_commands[0]}")
        if profile.lint_commands:
            sections.append(f"# Lint: {profile.lint_commands[0]}")
        sections.append("```")
        sections.append("")

        # Code Style
        sections.append("## Code Style")
        sections.append("")
        if profile.code_style:
            sections.append(f"Tools: {', '.join(profile.code_style.keys())}")
        if profile.naming_conventions:
            sections.append("")
            sections.append("### Naming Conventions")
            for item, conv in profile.naming_conventions.items():
                sections.append(f"- {item}: `{conv}`")

        content = "\n".join(sections)

        return GeneratedDoc(
            path=".specify/memory/tech-context.md",
            content=content,
            format_name=self.format_name,
            description="Technology stack context for Spec Kit",
        )

    async def _generate_architecture_context(self, profile: CodebaseProfile) -> GeneratedDoc:
        """Generate architecture context file."""
        sections = []

        sections.append("# Architecture Context")
        sections.append("")
        sections.append("This file describes the architectural patterns and structure of the project.")
        sections.append("")

        # Patterns
        sections.append("## Architecture Patterns")
        sections.append("")
        if profile.architecture_patterns:
            for pattern in profile.architecture_patterns:
                sections.append(f"- {pattern}")
                desc = self._get_pattern_description(pattern)
                if desc:
                    sections.append(f"  {desc}")
        else:
            sections.append("Standard application architecture.")
        sections.append("")

        # API Style
        if profile.api_style:
            sections.append("## API Architecture")
            sections.append("")
            sections.append(f"**Style**: {profile.api_style}")
            sections.append("")
            api_desc = self._get_api_style_description(profile.api_style)
            sections.append(api_desc)
            sections.append("")

        # Project Structure
        sections.append("## Project Structure")
        sections.append("")
        sections.append("```")
        sections.append(self._format_file_tree(profile, max_depth=2))
        sections.append("```")
        sections.append("")

        # Key Directories
        sections.append("## Key Directories")
        sections.append("")
        key_dirs = self._get_directory_purposes(profile)
        for dir_path, purpose in key_dirs.items():
            sections.append(f"- `{dir_path}/`: {purpose}")
        sections.append("")

        # Entry Points
        if profile.structure.entry_points:
            sections.append("## Entry Points")
            sections.append("")
            for ep in profile.structure.entry_points[:5]:
                sections.append(f"- `{ep}`")

        content = "\n".join(sections)

        return GeneratedDoc(
            path=".specify/memory/architecture-context.md",
            content=content,
            format_name=self.format_name,
            description="Architecture context for Spec Kit",
        )

    async def _generate_quality_standards(self, profile: CodebaseProfile) -> str:
        """Generate code quality standards."""
        standards = []

        # Type safety
        if profile.primary_language in ["python", "typescript"]:
            standards.append("1. **Type Safety**: All public functions MUST have type annotations")

        # Code style
        if profile.code_style:
            tools = ", ".join(profile.code_style.keys())
            standards.append(f"2. **Code Formatting**: Code MUST pass {tools} checks")

        # Testing
        standards.append("3. **Test Coverage**: New features MUST include unit tests")

        # Error handling
        standards.append("4. **Error Handling**: All errors MUST be handled appropriately")

        # Documentation
        standards.append("5. **Documentation**: Public APIs MUST be documented")

        # Naming
        if profile.naming_conventions:
            conventions = ", ".join([f"{k}: {v}" for k, v in profile.naming_conventions.items()])
            standards.append(f"6. **Naming**: Follow conventions - {conventions}")

        return "\n".join(standards)

    def _generate_testing_requirements(self, profile: CodebaseProfile) -> str:
        """Generate testing requirements."""
        reqs = []

        reqs.append("1. **Unit Tests**: All business logic MUST have unit tests")
        reqs.append("2. **Integration Tests**: API endpoints MUST have integration tests")
        reqs.append("3. **Edge Cases**: Tests MUST cover edge cases and error conditions")

        if profile.test_commands:
            reqs.append(f"4. **Test Execution**: Tests MUST pass via `{profile.test_commands[0]}`")

        reqs.append("5. **Mocking**: External dependencies MUST be mocked in unit tests")

        return "\n".join(reqs)

    def _generate_documentation_requirements(self, profile: CodebaseProfile) -> str:
        """Generate documentation requirements."""
        reqs = []

        if profile.primary_language == "python":
            reqs.append("1. **Docstrings**: All public functions and classes MUST have docstrings")
            reqs.append("2. **Type Hints**: All function signatures MUST include type hints")
        elif profile.primary_language in ["typescript", "javascript"]:
            reqs.append("1. **JSDoc**: Public APIs SHOULD have JSDoc comments")
            reqs.append("2. **Types**: All functions MUST have explicit type definitions")
        elif profile.primary_language == "go":
            reqs.append("1. **Go Doc**: Exported functions MUST have doc comments")
        elif profile.primary_language == "rust":
            reqs.append("1. **Rustdoc**: Public items MUST have /// documentation")

        reqs.append("3. **README**: Significant features SHOULD update the README")
        reqs.append("4. **API Docs**: API changes MUST be reflected in API documentation")

        return "\n".join(reqs)

    def _generate_security_requirements(self) -> str:
        """Generate security requirements."""
        return """1. **No Secrets**: NEVER commit secrets, API keys, or credentials
2. **Input Validation**: ALL user input MUST be validated and sanitized
3. **SQL Injection**: Use parameterized queries for all database operations
4. **XSS Prevention**: Sanitize output in web applications
5. **Dependency Security**: Regularly update dependencies for security patches
6. **Authentication**: Protect sensitive endpoints with proper authentication
7. **Authorization**: Implement proper access control checks"""

    async def _generate_architecture_constraints(self, profile: CodebaseProfile) -> str:
        """Generate architecture constraints."""
        constraints = []

        if profile.architecture_patterns:
            if "MVC" in profile.architecture_patterns:
                constraints.append("1. **MVC Pattern**: Maintain separation between Models, Views, and Controllers")
            if "Layered" in profile.architecture_patterns:
                constraints.append("2. **Layered Architecture**: Respect layer boundaries (API → Service → Repository)")
            if "DDD" in profile.architecture_patterns:
                constraints.append("3. **Domain-Driven Design**: Keep domain logic in domain layer")
            if "Microservices" in profile.architecture_patterns:
                constraints.append("4. **Service Boundaries**: Respect service boundaries and communication protocols")

        if not constraints:
            constraints.append("1. **Separation of Concerns**: Keep code organized by responsibility")
            constraints.append("2. **Single Responsibility**: Each module should have one primary purpose")
            constraints.append("3. **Dependency Direction**: Higher-level modules should not depend on lower-level details")

        return "\n".join(constraints)

    def _generate_workflow_requirements(self, profile: CodebaseProfile) -> str:
        """Generate workflow requirements."""
        reqs = []

        if profile.has_git:
            reqs.append(f"1. **Branching**: Create feature branches from `{profile.default_branch}`")
            reqs.append("2. **Commits**: Write clear, descriptive commit messages")
            reqs.append("3. **Pull Requests**: All changes MUST go through pull request review")

        if profile.lint_commands:
            reqs.append(f"4. **Linting**: Run `{profile.lint_commands[0]}` before committing")

        if profile.test_commands:
            reqs.append(f"5. **Testing**: Run `{profile.test_commands[0]}` before pushing")

        reqs.append("6. **Review**: Code MUST be reviewed before merging")

        return "\n".join(reqs)

    def _generate_compatibility_requirements(self, profile: CodebaseProfile) -> str:
        """Generate compatibility requirements."""
        reqs = []

        # Check pyproject.toml for Python version
        if "pyproject.toml" in profile.key_files_content:
            content = profile.key_files_content["pyproject.toml"]
            if "python" in content:
                reqs.append("1. **Python Version**: Maintain compatibility with specified Python version")

        # Check package.json for Node version
        if "package.json" in profile.key_files_content:
            content = profile.key_files_content["package.json"]
            if "engines" in content:
                reqs.append("1. **Node Version**: Maintain compatibility with specified Node.js version")

        if not reqs:
            reqs.append("1. **Runtime Compatibility**: Maintain compatibility with current runtime version")

        reqs.append("2. **API Compatibility**: Breaking changes MUST be documented and versioned")
        reqs.append("3. **Dependencies**: Keep dependencies up to date while maintaining stability")

        return "\n".join(reqs)

    def _get_pattern_description(self, pattern: str) -> str:
        """Get description for architecture pattern."""
        descriptions = {
            "MVC": "Model-View-Controller separation",
            "Layered": "Horizontal layers with clear boundaries",
            "DDD": "Domain-driven design with bounded contexts",
            "Microservices": "Distributed services with independent deployment",
            "Monorepo": "Multiple packages in single repository",
        }
        return descriptions.get(pattern, "")

    def _get_api_style_description(self, style: str) -> str:
        """Get description for API style."""
        descriptions = {
            "REST": "RESTful API following HTTP semantics and resource-based URLs.",
            "GraphQL": "GraphQL API with schema-first design and type safety.",
            "gRPC": "gRPC API using Protocol Buffers for efficient communication.",
        }
        return descriptions.get(style, "")

    def _get_directory_purposes(self, profile: CodebaseProfile) -> dict[str, str]:
        """Get purposes for key directories."""
        purposes = {}
        dir_map = {
            "src": "Main source code",
            "lib": "Library code",
            "api": "API endpoints",
            "app": "Application code",
            "components": "UI components",
            "services": "Business logic services",
            "models": "Data models",
            "utils": "Utility functions",
            "tests": "Test files",
            "test": "Test files",
            "config": "Configuration files",
            "scripts": "Build and utility scripts",
            "docs": "Documentation",
            "public": "Static assets",
        }

        for d in profile.structure.directories:
            base = d.split("/")[0]
            if base in dir_map and base not in purposes:
                purposes[base] = dir_map[base]

        return dict(list(purposes.items())[:8])
