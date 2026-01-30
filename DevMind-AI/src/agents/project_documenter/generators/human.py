"""Human-readable documentation generator."""

from __future__ import annotations

from typing import Any

from .base import BaseDocGenerator, GeneratedDoc
from ..analyzer import CodebaseProfile


class HumanDocGenerator(BaseDocGenerator):
    """Generates human-readable documentation.

    Creates documentation intended for developers:
    - README.md with project overview
    - ARCHITECTURE.md with system design
    - CONTRIBUTING.md with contribution guidelines
    - API documentation
    """

    format_name = "human"
    format_description = "Human-readable documentation"

    async def generate(self, profile: CodebaseProfile, **kwargs: Any) -> list[GeneratedDoc]:
        """Generate human-readable documentation.

        Args:
            profile: Analyzed codebase profile
            **kwargs: Additional options
                - include_readme: Generate README.md (default: True)
                - include_architecture: Generate ARCHITECTURE.md (default: True)
                - include_contributing: Generate CONTRIBUTING.md (default: True)
                - include_api: Generate API docs (default: False)

        Returns:
            List of documentation files
        """
        docs = []

        # README.md
        if kwargs.get("include_readme", True):
            readme = await self._generate_readme(profile)
            docs.append(readme)

        # ARCHITECTURE.md
        if kwargs.get("include_architecture", True):
            arch_doc = await self._generate_architecture_doc(profile)
            docs.append(arch_doc)

        # CONTRIBUTING.md
        if kwargs.get("include_contributing", True):
            contrib_doc = await self._generate_contributing_doc(profile)
            docs.append(contrib_doc)

        # API documentation
        if kwargs.get("include_api", False) and profile.api_style:
            api_doc = await self._generate_api_doc(profile)
            docs.append(api_doc)

        return docs

    async def _generate_readme(self, profile: CodebaseProfile) -> GeneratedDoc:
        """Generate README.md."""
        sections = []

        # Title and description
        sections.append(f"# {profile.name}")
        sections.append("")
        if profile.description:
            sections.append(profile.description)
        else:
            desc = await self._generate_description(profile)
            sections.append(desc)
        sections.append("")

        # Badges (placeholders)
        sections.append("<!-- Badges -->")
        sections.append("")

        # Features
        sections.append("## Features")
        sections.append("")
        features = await self._generate_features(profile)
        sections.append(features)
        sections.append("")

        # Tech Stack
        sections.append("## Tech Stack")
        sections.append("")
        sections.append(f"- **Language**: {profile.primary_language.capitalize()}")
        if profile.frameworks:
            sections.append(f"- **Frameworks**: {', '.join(profile.frameworks)}")
        if profile.api_style:
            sections.append(f"- **API**: {profile.api_style}")
        sections.append("")

        # Installation
        sections.append("## Installation")
        sections.append("")
        install_instructions = self._generate_installation(profile)
        sections.append(install_instructions)
        sections.append("")

        # Usage
        sections.append("## Usage")
        sections.append("")
        usage_instructions = await self._generate_usage(profile)
        sections.append(usage_instructions)
        sections.append("")

        # Development
        sections.append("## Development")
        sections.append("")
        dev_instructions = self._generate_development(profile)
        sections.append(dev_instructions)
        sections.append("")

        # Project Structure
        sections.append("## Project Structure")
        sections.append("")
        sections.append("```")
        sections.append(self._format_file_tree(profile, max_depth=2))
        sections.append("```")
        sections.append("")

        # Contributing
        sections.append("## Contributing")
        sections.append("")
        sections.append("See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.")
        sections.append("")

        # License
        sections.append("## License")
        sections.append("")
        sections.append("<!-- Add license information -->")

        content = "\n".join(sections)

        return GeneratedDoc(
            path="docs/README.generated.md",
            content=content,
            format_name=self.format_name,
            description="Generated README documentation",
        )

    async def _generate_architecture_doc(self, profile: CodebaseProfile) -> GeneratedDoc:
        """Generate ARCHITECTURE.md."""
        sections = []

        sections.append(f"# {profile.name} Architecture")
        sections.append("")
        sections.append("This document describes the architecture and design of the system.")
        sections.append("")

        # Overview
        sections.append("## Overview")
        sections.append("")
        overview = await self._generate_architecture_overview(profile)
        sections.append(overview)
        sections.append("")

        # Architecture Patterns
        sections.append("## Architecture Patterns")
        sections.append("")
        if profile.architecture_patterns:
            for pattern in profile.architecture_patterns:
                sections.append(f"### {pattern}")
                sections.append("")
                pattern_desc = self._get_pattern_details(pattern)
                sections.append(pattern_desc)
                sections.append("")
        else:
            sections.append("This project follows standard application architecture principles.")
            sections.append("")

        # System Components
        sections.append("## System Components")
        sections.append("")
        components = self._generate_components(profile)
        sections.append(components)
        sections.append("")

        # Data Flow
        if profile.api_style:
            sections.append("## API Architecture")
            sections.append("")
            api_arch = self._generate_api_architecture(profile)
            sections.append(api_arch)
            sections.append("")

        # Technology Stack
        sections.append("## Technology Stack")
        sections.append("")
        tech_stack = self._generate_tech_stack_details(profile)
        sections.append(tech_stack)
        sections.append("")

        # Directory Structure
        sections.append("## Directory Structure")
        sections.append("")
        dir_structure = self._generate_directory_explanation(profile)
        sections.append(dir_structure)
        sections.append("")

        # Design Decisions
        sections.append("## Key Design Decisions")
        sections.append("")
        decisions = await self._generate_design_decisions(profile)
        sections.append(decisions)

        content = "\n".join(sections)

        return GeneratedDoc(
            path="docs/ARCHITECTURE.md",
            content=content,
            format_name=self.format_name,
            description="Architecture documentation",
        )

    async def _generate_contributing_doc(self, profile: CodebaseProfile) -> GeneratedDoc:
        """Generate CONTRIBUTING.md."""
        sections = []

        sections.append(f"# Contributing to {profile.name}")
        sections.append("")
        sections.append("Thank you for your interest in contributing! This document provides guidelines")
        sections.append("for contributing to this project.")
        sections.append("")

        # Getting Started
        sections.append("## Getting Started")
        sections.append("")
        sections.append("### Prerequisites")
        sections.append("")
        prereqs = self._generate_prerequisites(profile)
        sections.append(prereqs)
        sections.append("")

        sections.append("### Setting Up the Development Environment")
        sections.append("")
        setup = self._generate_dev_setup(profile)
        sections.append(setup)
        sections.append("")

        # Development Workflow
        sections.append("## Development Workflow")
        sections.append("")
        workflow = self._generate_contribution_workflow(profile)
        sections.append(workflow)
        sections.append("")

        # Code Style
        sections.append("## Code Style")
        sections.append("")
        style_guide = self._generate_style_guide(profile)
        sections.append(style_guide)
        sections.append("")

        # Testing
        sections.append("## Testing")
        sections.append("")
        testing_guide = self._generate_testing_guide(profile)
        sections.append(testing_guide)
        sections.append("")

        # Commit Guidelines
        sections.append("## Commit Guidelines")
        sections.append("")
        sections.append("- Write clear, concise commit messages")
        sections.append("- Use present tense (\"Add feature\" not \"Added feature\")")
        sections.append("- Reference issues when applicable")
        sections.append("")
        sections.append("### Commit Message Format")
        sections.append("")
        sections.append("```")
        sections.append("<type>(<scope>): <description>")
        sections.append("")
        sections.append("[optional body]")
        sections.append("```")
        sections.append("")
        sections.append("Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`")
        sections.append("")

        # Pull Requests
        sections.append("## Pull Requests")
        sections.append("")
        sections.append("1. Fork the repository")
        sections.append("2. Create a feature branch (`git checkout -b feature/amazing-feature`)")
        sections.append("3. Make your changes")
        sections.append("4. Run tests and linting")
        sections.append("5. Commit your changes")
        sections.append("6. Push to your branch")
        sections.append("7. Open a Pull Request")
        sections.append("")

        # Code Review
        sections.append("## Code Review Process")
        sections.append("")
        sections.append("All submissions require review. We aim to review PRs within a few days.")
        sections.append("Please be responsive to feedback and be prepared to make changes.")

        content = "\n".join(sections)

        return GeneratedDoc(
            path="docs/CONTRIBUTING.md",
            content=content,
            format_name=self.format_name,
            description="Contribution guidelines",
        )

    async def _generate_api_doc(self, profile: CodebaseProfile) -> GeneratedDoc:
        """Generate API documentation."""
        sections = []

        sections.append(f"# {profile.name} API Documentation")
        sections.append("")

        # Overview
        sections.append("## Overview")
        sections.append("")
        sections.append(f"This project exposes a {profile.api_style} API.")
        sections.append("")

        # Authentication (placeholder)
        sections.append("## Authentication")
        sections.append("")
        sections.append("<!-- Document authentication requirements -->")
        sections.append("")

        # Base URL (placeholder)
        sections.append("## Base URL")
        sections.append("")
        sections.append("```")
        sections.append("http://localhost:8000/api")
        sections.append("```")
        sections.append("")

        # Endpoints placeholder
        sections.append("## Endpoints")
        sections.append("")
        sections.append("<!-- Document API endpoints -->")
        sections.append("")

        # Error Handling
        sections.append("## Error Handling")
        sections.append("")
        error_handling = self._generate_error_handling_doc(profile)
        sections.append(error_handling)

        content = "\n".join(sections)

        return GeneratedDoc(
            path="docs/API.md",
            content=content,
            format_name=self.format_name,
            description="API documentation",
        )

    async def _generate_description(self, profile: CodebaseProfile) -> str:
        """Generate project description using LLM."""
        prompt = f"""Generate a concise 2-3 sentence description for a {profile.primary_language} project.

Context:
- Frameworks: {', '.join(profile.frameworks) if profile.frameworks else 'None'}
- Architecture: {', '.join(profile.architecture_patterns) if profile.architecture_patterns else 'Standard'}
- API: {profile.api_style if profile.api_style else 'None'}

Be professional and informative. Do not use marketing language."""

        try:
            return await self._generate_content(prompt)
        except Exception:
            return f"A {profile.primary_language.capitalize()} application."

    async def _generate_features(self, profile: CodebaseProfile) -> str:
        """Generate features list."""
        features = []

        # Based on frameworks and patterns
        if profile.frameworks:
            for fw in profile.frameworks[:3]:
                features.append(f"- Built with {fw.capitalize()}")

        if profile.api_style:
            features.append(f"- {profile.api_style} API")

        if "Microservices" in profile.architecture_patterns:
            features.append("- Microservices architecture")
        elif "Monorepo" in profile.architecture_patterns:
            features.append("- Monorepo structure")

        if not features:
            features.append("- Modern development practices")
            features.append("- Well-structured codebase")

        return "\n".join(features)

    def _generate_installation(self, profile: CodebaseProfile) -> str:
        """Generate installation instructions."""
        lines = []

        if profile.primary_language == "python":
            lines.append("```bash")
            lines.append("# Clone the repository")
            lines.append("git clone <repository-url>")
            lines.append(f"cd {profile.name}")
            lines.append("")
            lines.append("# Create virtual environment")
            lines.append("python -m venv venv")
            lines.append("source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
            lines.append("")
            lines.append("# Install dependencies")
            if "pyproject.toml" in profile.key_files_content:
                lines.append("pip install -e .")
            else:
                lines.append("pip install -r requirements.txt")
            lines.append("```")

        elif profile.primary_language in ["typescript", "javascript"]:
            lines.append("```bash")
            lines.append("# Clone the repository")
            lines.append("git clone <repository-url>")
            lines.append(f"cd {profile.name}")
            lines.append("")
            lines.append("# Install dependencies")
            lines.append("npm install")
            lines.append("```")

        elif profile.primary_language == "go":
            lines.append("```bash")
            lines.append("# Clone the repository")
            lines.append("git clone <repository-url>")
            lines.append(f"cd {profile.name}")
            lines.append("")
            lines.append("# Download dependencies")
            lines.append("go mod download")
            lines.append("```")

        elif profile.primary_language == "rust":
            lines.append("```bash")
            lines.append("# Clone the repository")
            lines.append("git clone <repository-url>")
            lines.append(f"cd {profile.name}")
            lines.append("")
            lines.append("# Build the project")
            lines.append("cargo build")
            lines.append("```")

        else:
            lines.append("```bash")
            lines.append("git clone <repository-url>")
            lines.append(f"cd {profile.name}")
            lines.append("# Install dependencies according to your package manager")
            lines.append("```")

        return "\n".join(lines)

    async def _generate_usage(self, profile: CodebaseProfile) -> str:
        """Generate usage instructions."""
        lines = []

        if profile.structure.entry_points:
            ep = profile.structure.entry_points[0]
            lines.append(f"The main entry point is `{ep}`.")
            lines.append("")

        lines.append("```bash")
        if profile.build_commands:
            lines.append(f"# Build: {profile.build_commands[0]}")
        if profile.primary_language == "python":
            if "fastapi" in profile.frameworks:
                lines.append("# Run the server")
                lines.append("uvicorn main:app --reload")
            elif "flask" in profile.frameworks:
                lines.append("# Run the server")
                lines.append("flask run")
            elif "django" in profile.frameworks:
                lines.append("# Run the server")
                lines.append("python manage.py runserver")
        elif profile.primary_language in ["typescript", "javascript"]:
            lines.append("# Run the application")
            lines.append("npm start")
        lines.append("```")

        return "\n".join(lines)

    def _generate_development(self, profile: CodebaseProfile) -> str:
        """Generate development instructions."""
        lines = []

        lines.append("### Running Tests")
        lines.append("")
        lines.append("```bash")
        if profile.test_commands:
            lines.append(profile.test_commands[0])
        else:
            lines.append("# Run tests")
        lines.append("```")
        lines.append("")

        if profile.lint_commands:
            lines.append("### Linting")
            lines.append("")
            lines.append("```bash")
            lines.append(profile.lint_commands[0])
            lines.append("```")

        return "\n".join(lines)

    async def _generate_architecture_overview(self, profile: CodebaseProfile) -> str:
        """Generate architecture overview."""
        prompt = f"""Write a brief (3-4 sentences) architecture overview for a {profile.primary_language} project.

Context:
- Frameworks: {', '.join(profile.frameworks) if profile.frameworks else 'None'}
- Patterns: {', '.join(profile.architecture_patterns) if profile.architecture_patterns else 'Standard'}
- API Style: {profile.api_style if profile.api_style else 'None'}

Be technical but accessible."""

        try:
            return await self._generate_content(prompt)
        except Exception:
            return f"This is a {profile.primary_language.capitalize()} application following modern development practices."

    def _get_pattern_details(self, pattern: str) -> str:
        """Get details for architecture pattern."""
        details = {
            "MVC": """The project follows the Model-View-Controller pattern:
- **Models**: Data structures and business logic
- **Views**: Presentation layer
- **Controllers**: Request handlers and orchestration""",
            "Layered": """The project uses a layered architecture:
- **API Layer**: HTTP handlers and routing
- **Service Layer**: Business logic and orchestration
- **Repository Layer**: Data access and persistence""",
            "DDD": """The project follows Domain-Driven Design principles:
- **Domain Layer**: Core business logic and entities
- **Application Layer**: Use cases and orchestration
- **Infrastructure Layer**: External integrations""",
            "Microservices": """The project is structured as microservices:
- Each service has a single responsibility
- Services communicate via APIs
- Independent deployment and scaling""",
            "Monorepo": """The project uses a monorepo structure:
- Multiple packages in a single repository
- Shared dependencies and tooling
- Coordinated releases""",
        }
        return details.get(pattern, f"The project follows {pattern} patterns.")

    def _generate_components(self, profile: CodebaseProfile) -> str:
        """Generate system components description."""
        lines = []

        component_map = {
            "src": "Core application source code",
            "api": "API endpoint handlers",
            "services": "Business logic services",
            "models": "Data models and schemas",
            "components": "UI components",
            "utils": "Utility functions and helpers",
            "config": "Configuration management",
        }

        for d in profile.structure.directories:
            base = d.split("/")[0]
            if base in component_map:
                lines.append(f"### {base.capitalize()}")
                lines.append("")
                lines.append(component_map[base])
                lines.append("")

        return "\n".join(lines) if lines else "See project structure for component organization."

    def _generate_api_architecture(self, profile: CodebaseProfile) -> str:
        """Generate API architecture description."""
        if profile.api_style == "REST":
            return """### REST API

The API follows RESTful conventions:
- Resources identified by URLs
- Standard HTTP methods (GET, POST, PUT, DELETE)
- JSON request/response bodies
- Proper status codes for responses"""
        elif profile.api_style == "GraphQL":
            return """### GraphQL API

The API uses GraphQL:
- Single endpoint for all queries
- Strongly typed schema
- Client-specified data requirements
- Efficient data fetching"""
        elif profile.api_style == "gRPC":
            return """### gRPC API

The API uses gRPC:
- Protocol Buffers for serialization
- Efficient binary protocol
- Strong typing from .proto definitions
- Support for streaming"""
        return "See API documentation for details."

    def _generate_tech_stack_details(self, profile: CodebaseProfile) -> str:
        """Generate detailed tech stack information."""
        lines = []

        lines.append(f"### {profile.primary_language.capitalize()}")
        lines.append("")
        lines.append(f"Primary development language.")
        lines.append("")

        if profile.frameworks:
            lines.append("### Frameworks")
            lines.append("")
            for fw in profile.frameworks:
                lines.append(f"- **{fw.capitalize()}**: ")
            lines.append("")

        if profile.dependencies:
            lines.append("### Key Dependencies")
            lines.append("")
            for dep_info in profile.dependencies[:1]:
                for dep in dep_info.dependencies[:10]:
                    lines.append(f"- {dep}")
            lines.append("")

        return "\n".join(lines)

    def _generate_directory_explanation(self, profile: CodebaseProfile) -> str:
        """Generate directory structure explanation."""
        lines = []
        lines.append("```")
        lines.append(f"{profile.name}/")

        explanations = {
            "src": "Source code",
            "lib": "Library code",
            "api": "API routes",
            "app": "Application",
            "components": "Components",
            "services": "Services",
            "models": "Data models",
            "utils": "Utilities",
            "tests": "Tests",
            "config": "Config",
            "docs": "Documentation",
        }

        shown = set()
        for d in profile.structure.directories[:20]:
            base = d.split("/")[0]
            if base in explanations and base not in shown:
                shown.add(base)
                lines.append(f"├── {base}/        # {explanations[base]}")

        lines.append("```")
        return "\n".join(lines)

    async def _generate_design_decisions(self, profile: CodebaseProfile) -> str:
        """Generate design decisions section."""
        prompt = f"""Generate 3-4 key design decisions for a {profile.primary_language} project.

Context:
- Frameworks: {', '.join(profile.frameworks) if profile.frameworks else 'None'}
- Architecture: {', '.join(profile.architecture_patterns) if profile.architecture_patterns else 'Standard'}

Format as numbered list with brief rationale for each."""

        try:
            return await self._generate_content(prompt)
        except Exception:
            return """1. **Language Choice**: Selected for ecosystem and developer productivity
2. **Architecture**: Chosen for maintainability and scalability
3. **Testing Strategy**: Comprehensive testing for reliability"""

    def _generate_prerequisites(self, profile: CodebaseProfile) -> str:
        """Generate prerequisites list."""
        lines = []

        if profile.primary_language == "python":
            lines.append("- Python 3.9 or higher")
            lines.append("- pip (Python package installer)")
        elif profile.primary_language in ["typescript", "javascript"]:
            lines.append("- Node.js 18 or higher")
            lines.append("- npm or yarn")
        elif profile.primary_language == "go":
            lines.append("- Go 1.21 or higher")
        elif profile.primary_language == "rust":
            lines.append("- Rust (latest stable)")
            lines.append("- Cargo")

        lines.append("- Git")

        return "\n".join([f"- {l[2:]}" if l.startswith("- ") else f"- {l}" for l in lines])

    def _generate_dev_setup(self, profile: CodebaseProfile) -> str:
        """Generate development setup instructions."""
        return self._generate_installation(profile)

    def _generate_contribution_workflow(self, profile: CodebaseProfile) -> str:
        """Generate contribution workflow."""
        lines = []

        lines.append("1. **Fork** the repository")
        lines.append("2. **Clone** your fork locally")
        lines.append(f"3. **Create a branch** from `{profile.default_branch}`")
        lines.append("4. **Make your changes**")
        if profile.lint_commands:
            lines.append(f"5. **Run linting**: `{profile.lint_commands[0]}`")
        if profile.test_commands:
            lines.append(f"6. **Run tests**: `{profile.test_commands[0]}`")
        lines.append("7. **Commit** with a clear message")
        lines.append("8. **Push** to your fork")
        lines.append("9. **Open a Pull Request**")

        return "\n".join(lines)

    def _generate_style_guide(self, profile: CodebaseProfile) -> str:
        """Generate code style guide."""
        lines = []

        if profile.code_style:
            lines.append(f"This project uses: {', '.join(profile.code_style.keys())}")
            lines.append("")

        if profile.naming_conventions:
            lines.append("### Naming Conventions")
            lines.append("")
            for item, conv in profile.naming_conventions.items():
                lines.append(f"- **{item}**: {conv}")
            lines.append("")

        lines.append("### General Guidelines")
        lines.append("")
        guidelines = self._get_language_specific_guidelines(profile)
        lines.append(guidelines)

        return "\n".join(lines)

    def _generate_testing_guide(self, profile: CodebaseProfile) -> str:
        """Generate testing guide."""
        lines = []

        lines.append("### Running Tests")
        lines.append("")
        if profile.test_commands:
            lines.append("```bash")
            for cmd in profile.test_commands:
                lines.append(cmd)
            lines.append("```")
        lines.append("")

        lines.append("### Writing Tests")
        lines.append("")
        lines.append("- Write tests for all new functionality")
        lines.append("- Test both success and error cases")
        lines.append("- Use meaningful test names")
        lines.append("- Keep tests focused and independent")

        return "\n".join(lines)

    def _generate_error_handling_doc(self, profile: CodebaseProfile) -> str:
        """Generate error handling documentation."""
        if profile.api_style == "REST":
            return """### Error Response Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message"
  }
}
```

### Common Status Codes

- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error"""
        return "See API implementation for error handling details."
