"""Codebase analyzer for project documentation generation."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class FileInfo:
    """Information about a single file."""

    path: str
    relative_path: str
    extension: str
    size: int
    lines: int = 0
    language: str = "unknown"


@dataclass
class DependencyInfo:
    """Project dependency information."""

    package_manager: str  # npm, pip, cargo, go, maven, etc.
    dependencies: list[str] = field(default_factory=list)
    dev_dependencies: list[str] = field(default_factory=list)
    manifest_file: str = ""


@dataclass
class ProjectStructure:
    """Analyzed project structure."""

    directories: list[str] = field(default_factory=list)
    files: list[FileInfo] = field(default_factory=list)
    entry_points: list[str] = field(default_factory=list)
    test_directories: list[str] = field(default_factory=list)
    config_files: list[str] = field(default_factory=list)


@dataclass
class CodebaseProfile:
    """Complete profile of an analyzed codebase."""

    root_path: str
    name: str
    description: str = ""

    # Languages and frameworks
    primary_language: str = "unknown"
    languages: dict[str, int] = field(default_factory=dict)  # lang -> file count
    frameworks: list[str] = field(default_factory=list)

    # Structure
    structure: ProjectStructure = field(default_factory=ProjectStructure)
    dependencies: list[DependencyInfo] = field(default_factory=list)

    # Conventions
    code_style: dict[str, Any] = field(default_factory=dict)
    naming_conventions: dict[str, str] = field(default_factory=dict)

    # Commands
    build_commands: list[str] = field(default_factory=list)
    test_commands: list[str] = field(default_factory=list)
    lint_commands: list[str] = field(default_factory=list)

    # Documentation
    existing_docs: list[str] = field(default_factory=list)
    has_readme: bool = False
    has_contributing: bool = False
    has_changelog: bool = False

    # Git info
    has_git: bool = False
    default_branch: str = "main"

    # Architecture patterns
    architecture_patterns: list[str] = field(default_factory=list)
    api_style: str = ""  # REST, GraphQL, gRPC, etc.

    # Key files content (for context)
    key_files_content: dict[str, str] = field(default_factory=dict)


class CodebaseAnalyzer:
    """Analyzes codebases to extract structure, patterns, and conventions."""

    # Language detection by extension
    LANGUAGE_MAP = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".jsx": "javascript",
        ".java": "java",
        ".kt": "kotlin",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php",
        ".cs": "csharp",
        ".cpp": "cpp",
        ".c": "c",
        ".h": "c",
        ".hpp": "cpp",
        ".swift": "swift",
        ".scala": "scala",
        ".vue": "vue",
        ".svelte": "svelte",
    }

    # Framework detection patterns
    FRAMEWORK_PATTERNS = {
        "react": [r"from\s+['\"]react['\"]", r"import\s+React"],
        "vue": [r"from\s+['\"]vue['\"]", r"\.vue$"],
        "angular": [r"@angular/core", r"@Component"],
        "nextjs": [r"from\s+['\"]next", r"next\.config"],
        "fastapi": [r"from\s+fastapi", r"FastAPI\(\)"],
        "flask": [r"from\s+flask", r"Flask\(__name__\)"],
        "django": [r"from\s+django", r"INSTALLED_APPS"],
        "express": [r"require\(['\"]express['\"]", r"from\s+['\"]express['\"]"],
        "nestjs": [r"@nestjs/", r"@Module"],
        "spring": [r"org\.springframework", r"@SpringBootApplication"],
        "rails": [r"Rails\.application", r"class.*<.*ApplicationRecord"],
        "gin": [r"github\.com/gin-gonic/gin"],
        "actix": [r"actix_web", r"actix-web"],
        "tokio": [r"tokio::", r'\[dependencies\].*tokio'],
    }

    # Files to always read for context
    KEY_FILES = [
        "README.md",
        "readme.md",
        "package.json",
        "pyproject.toml",
        "setup.py",
        "Cargo.toml",
        "go.mod",
        "pom.xml",
        "build.gradle",
        "Makefile",
        "docker-compose.yml",
        "Dockerfile",
        ".eslintrc.js",
        ".eslintrc.json",
        ".prettierrc",
        "tsconfig.json",
        "jest.config.js",
        "pytest.ini",
        "setup.cfg",
        ".editorconfig",
    ]

    # Directories to ignore
    IGNORE_DIRS = {
        "node_modules",
        ".git",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "venv",
        ".venv",
        "env",
        ".env",
        "dist",
        "build",
        "target",
        ".next",
        ".nuxt",
        "coverage",
        ".coverage",
        ".tox",
        "vendor",
    }

    def __init__(self, max_file_size: int = 100_000, max_files: int = 1000):
        """Initialize the analyzer.

        Args:
            max_file_size: Maximum file size in bytes to read
            max_files: Maximum number of files to analyze
        """
        self.max_file_size = max_file_size
        self.max_files = max_files

    def analyze(self, root_path: str) -> CodebaseProfile:
        """Analyze a codebase and return its profile.

        Args:
            root_path: Path to the root of the codebase

        Returns:
            CodebaseProfile with analyzed information
        """
        root = Path(root_path).resolve()

        if not root.exists():
            raise ValueError(f"Path does not exist: {root_path}")

        profile = CodebaseProfile(
            root_path=str(root),
            name=root.name,
        )

        # Check for git
        profile.has_git = (root / ".git").exists()
        if profile.has_git:
            profile.default_branch = self._detect_default_branch(root)

        # Scan files and directories
        self._scan_structure(root, profile)

        # Detect languages
        self._detect_languages(profile)

        # Read key files
        self._read_key_files(root, profile)

        # Detect frameworks
        self._detect_frameworks(profile)

        # Detect dependencies
        self._detect_dependencies(root, profile)

        # Detect commands
        self._detect_commands(profile)

        # Detect architecture patterns
        self._detect_architecture(profile)

        # Detect code style
        self._detect_code_style(root, profile)

        # Check existing documentation
        self._check_existing_docs(root, profile)

        return profile

    def _scan_structure(self, root: Path, profile: CodebaseProfile) -> None:
        """Scan the directory structure."""
        files_scanned = 0

        for dirpath, dirnames, filenames in os.walk(root):
            # Filter out ignored directories
            dirnames[:] = [d for d in dirnames if d not in self.IGNORE_DIRS]

            rel_dir = os.path.relpath(dirpath, root)
            if rel_dir != ".":
                profile.structure.directories.append(rel_dir)

            for filename in filenames:
                if files_scanned >= self.max_files:
                    break

                filepath = Path(dirpath) / filename
                rel_path = os.path.relpath(filepath, root)
                ext = filepath.suffix.lower()

                try:
                    stat = filepath.stat()
                    size = stat.st_size
                except OSError:
                    continue

                file_info = FileInfo(
                    path=str(filepath),
                    relative_path=rel_path,
                    extension=ext,
                    size=size,
                    language=self.LANGUAGE_MAP.get(ext, "unknown"),
                )

                # Count lines for code files
                if ext in self.LANGUAGE_MAP and size < self.max_file_size:
                    try:
                        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                            file_info.lines = sum(1 for _ in f)
                    except Exception:
                        pass

                profile.structure.files.append(file_info)
                files_scanned += 1

                # Detect test directories
                if "test" in rel_path.lower() or "spec" in rel_path.lower():
                    parent = os.path.dirname(rel_path)
                    if parent and parent not in profile.structure.test_directories:
                        profile.structure.test_directories.append(parent)

                # Detect config files
                if filename in self.KEY_FILES or filename.startswith("."):
                    profile.structure.config_files.append(rel_path)

                # Detect entry points
                if filename in ["main.py", "index.js", "index.ts", "main.go", "main.rs", "app.py"]:
                    profile.structure.entry_points.append(rel_path)

    def _detect_languages(self, profile: CodebaseProfile) -> None:
        """Detect programming languages used."""
        lang_counts: dict[str, int] = {}

        for file_info in profile.structure.files:
            if file_info.language != "unknown":
                lang_counts[file_info.language] = lang_counts.get(file_info.language, 0) + 1

        profile.languages = lang_counts

        if lang_counts:
            profile.primary_language = max(lang_counts, key=lang_counts.get)

    def _read_key_files(self, root: Path, profile: CodebaseProfile) -> None:
        """Read content of key configuration files."""
        for filename in self.KEY_FILES:
            filepath = root / filename
            if filepath.exists() and filepath.stat().st_size < self.max_file_size:
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        profile.key_files_content[filename] = content

                        # Extract description from README
                        if filename.lower() == "readme.md":
                            desc = self._extract_description(content)
                            if desc:
                                profile.description = desc
                except Exception:
                    pass

    def _extract_description(self, readme_content: str) -> str:
        """Extract project description from README."""
        lines = readme_content.split("\n")
        in_header = False
        description_lines = []

        for line in lines:
            stripped = line.strip()

            # Skip title
            if stripped.startswith("# "):
                in_header = True
                continue

            # Skip badges and empty lines at start
            if in_header and (not stripped or stripped.startswith("[![") or stripped.startswith("![")):
                continue

            # Stop at next section
            if stripped.startswith("#"):
                break

            if stripped:
                description_lines.append(stripped)
                if len(description_lines) >= 3:  # Limit to 3 lines
                    break

        return " ".join(description_lines)[:500]  # Limit length

    def _detect_frameworks(self, profile: CodebaseProfile) -> None:
        """Detect frameworks used in the project."""
        # Check in key files content
        all_content = "\n".join(profile.key_files_content.values())

        for framework, patterns in self.FRAMEWORK_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, all_content, re.IGNORECASE):
                    if framework not in profile.frameworks:
                        profile.frameworks.append(framework)
                    break

        # Also check some source files for framework detection
        for file_info in profile.structure.files[:50]:  # Check first 50 files
            if file_info.size < self.max_file_size and file_info.language != "unknown":
                try:
                    with open(file_info.path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        for framework, patterns in self.FRAMEWORK_PATTERNS.items():
                            if framework in profile.frameworks:
                                continue
                            for pattern in patterns:
                                if re.search(pattern, content, re.IGNORECASE):
                                    profile.frameworks.append(framework)
                                    break
                except Exception:
                    pass

    def _detect_dependencies(self, root: Path, profile: CodebaseProfile) -> None:
        """Detect project dependencies."""
        # Python - pyproject.toml, requirements.txt, setup.py
        if "pyproject.toml" in profile.key_files_content:
            deps = self._parse_python_deps(profile.key_files_content["pyproject.toml"])
            if deps:
                profile.dependencies.append(deps)

        req_file = root / "requirements.txt"
        if req_file.exists():
            deps = self._parse_requirements_txt(req_file)
            if deps:
                profile.dependencies.append(deps)

        # JavaScript/TypeScript - package.json
        if "package.json" in profile.key_files_content:
            deps = self._parse_package_json(profile.key_files_content["package.json"])
            if deps:
                profile.dependencies.append(deps)

        # Rust - Cargo.toml
        if "Cargo.toml" in profile.key_files_content:
            deps = self._parse_cargo_toml(profile.key_files_content["Cargo.toml"])
            if deps:
                profile.dependencies.append(deps)

        # Go - go.mod
        if "go.mod" in profile.key_files_content:
            deps = self._parse_go_mod(profile.key_files_content["go.mod"])
            if deps:
                profile.dependencies.append(deps)

    def _parse_python_deps(self, content: str) -> DependencyInfo | None:
        """Parse Python dependencies from pyproject.toml."""
        import re

        deps = []
        dev_deps = []

        # Simple parsing for dependencies section
        in_deps = False
        in_dev_deps = False

        for line in content.split("\n"):
            if "[project.dependencies]" in line or "[tool.poetry.dependencies]" in line:
                in_deps = True
                in_dev_deps = False
                continue
            elif "[project.optional-dependencies]" in line or "[tool.poetry.group.dev.dependencies]" in line:
                in_deps = False
                in_dev_deps = True
                continue
            elif line.startswith("["):
                in_deps = False
                in_dev_deps = False
                continue

            if in_deps or in_dev_deps:
                # Extract package name
                match = re.match(r'^["\']?([a-zA-Z0-9_-]+)', line.strip())
                if match:
                    pkg = match.group(1)
                    if pkg and pkg != "python":
                        if in_deps:
                            deps.append(pkg)
                        else:
                            dev_deps.append(pkg)

        if deps or dev_deps:
            return DependencyInfo(
                package_manager="pip",
                dependencies=deps,
                dev_dependencies=dev_deps,
                manifest_file="pyproject.toml",
            )
        return None

    def _parse_requirements_txt(self, filepath: Path) -> DependencyInfo | None:
        """Parse requirements.txt."""
        try:
            with open(filepath, "r") as f:
                deps = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and not line.startswith("-"):
                        # Extract package name (before ==, >=, etc.)
                        pkg = re.split(r'[=<>!~\[]', line)[0].strip()
                        if pkg:
                            deps.append(pkg)

                if deps:
                    return DependencyInfo(
                        package_manager="pip",
                        dependencies=deps,
                        manifest_file="requirements.txt",
                    )
        except Exception:
            pass
        return None

    def _parse_package_json(self, content: str) -> DependencyInfo | None:
        """Parse package.json dependencies."""
        import json
        try:
            data = json.loads(content)
            deps = list(data.get("dependencies", {}).keys())
            dev_deps = list(data.get("devDependencies", {}).keys())

            if deps or dev_deps:
                return DependencyInfo(
                    package_manager="npm",
                    dependencies=deps,
                    dev_dependencies=dev_deps,
                    manifest_file="package.json",
                )
        except json.JSONDecodeError:
            pass
        return None

    def _parse_cargo_toml(self, content: str) -> DependencyInfo | None:
        """Parse Cargo.toml dependencies."""
        deps = []
        dev_deps = []
        in_deps = False
        in_dev_deps = False

        for line in content.split("\n"):
            if "[dependencies]" in line:
                in_deps = True
                in_dev_deps = False
                continue
            elif "[dev-dependencies]" in line:
                in_deps = False
                in_dev_deps = True
                continue
            elif line.startswith("["):
                in_deps = False
                in_dev_deps = False
                continue

            if in_deps or in_dev_deps:
                match = re.match(r'^([a-zA-Z0-9_-]+)\s*=', line.strip())
                if match:
                    pkg = match.group(1)
                    if in_deps:
                        deps.append(pkg)
                    else:
                        dev_deps.append(pkg)

        if deps or dev_deps:
            return DependencyInfo(
                package_manager="cargo",
                dependencies=deps,
                dev_dependencies=dev_deps,
                manifest_file="Cargo.toml",
            )
        return None

    def _parse_go_mod(self, content: str) -> DependencyInfo | None:
        """Parse go.mod dependencies."""
        deps = []
        in_require = False

        for line in content.split("\n"):
            if line.strip().startswith("require"):
                in_require = True
                continue
            elif line.strip() == ")":
                in_require = False
                continue

            if in_require:
                match = re.match(r'^\s*([^\s]+)\s+v', line)
                if match:
                    deps.append(match.group(1))

        if deps:
            return DependencyInfo(
                package_manager="go",
                dependencies=deps,
                manifest_file="go.mod",
            )
        return None

    def _detect_commands(self, profile: CodebaseProfile) -> None:
        """Detect build, test, and lint commands."""
        # From package.json scripts
        if "package.json" in profile.key_files_content:
            import json
            try:
                data = json.loads(profile.key_files_content["package.json"])
                scripts = data.get("scripts", {})

                for name, cmd in scripts.items():
                    if "build" in name.lower():
                        profile.build_commands.append(f"npm run {name}")
                    if "test" in name.lower():
                        profile.test_commands.append(f"npm run {name}")
                    if "lint" in name.lower() or "eslint" in name.lower():
                        profile.lint_commands.append(f"npm run {name}")
            except json.JSONDecodeError:
                pass

        # From pyproject.toml
        if "pyproject.toml" in profile.key_files_content:
            content = profile.key_files_content["pyproject.toml"]
            if "pytest" in content:
                profile.test_commands.append("pytest")
            if "ruff" in content:
                profile.lint_commands.append("ruff check .")
            if "black" in content:
                profile.lint_commands.append("black .")
            if "mypy" in content:
                profile.lint_commands.append("mypy .")

        # From Makefile
        if "Makefile" in profile.key_files_content:
            content = profile.key_files_content["Makefile"]
            if "test:" in content:
                profile.test_commands.append("make test")
            if "build:" in content:
                profile.build_commands.append("make build")
            if "lint:" in content:
                profile.lint_commands.append("make lint")

        # Defaults based on language
        if not profile.test_commands:
            if profile.primary_language == "python":
                profile.test_commands.append("pytest")
            elif profile.primary_language in ["javascript", "typescript"]:
                profile.test_commands.append("npm test")
            elif profile.primary_language == "go":
                profile.test_commands.append("go test ./...")
            elif profile.primary_language == "rust":
                profile.test_commands.append("cargo test")

    def _detect_architecture(self, profile: CodebaseProfile) -> None:
        """Detect architecture patterns."""
        dirs = set(profile.structure.directories)
        files = [f.relative_path for f in profile.structure.files]

        # MVC pattern
        if any(d for d in dirs if "controller" in d.lower() or "view" in d.lower() or "model" in d.lower()):
            profile.architecture_patterns.append("MVC")

        # Layered architecture
        if any(d for d in dirs if d in ["api", "services", "repositories", "models"]):
            profile.architecture_patterns.append("Layered")

        # Domain-driven design
        if any(d for d in dirs if d in ["domain", "entities", "aggregates", "value_objects"]):
            profile.architecture_patterns.append("DDD")

        # Microservices
        if "docker-compose.yml" in files and len([d for d in dirs if "service" in d.lower()]) > 2:
            profile.architecture_patterns.append("Microservices")

        # Monorepo
        if any(d for d in dirs if d in ["packages", "apps", "libs"]):
            profile.architecture_patterns.append("Monorepo")

        # API style detection
        if any("graphql" in f.lower() for f in files):
            profile.api_style = "GraphQL"
        elif any("grpc" in f.lower() or "proto" in f.lower() for f in files):
            profile.api_style = "gRPC"
        elif any(fw in profile.frameworks for fw in ["fastapi", "flask", "express", "nestjs", "gin"]):
            profile.api_style = "REST"

    def _detect_code_style(self, root: Path, profile: CodebaseProfile) -> None:
        """Detect code style conventions."""
        # Check for style config files
        style_configs = {
            ".eslintrc.js": "ESLint",
            ".eslintrc.json": "ESLint",
            ".prettierrc": "Prettier",
            ".prettierrc.json": "Prettier",
            "prettier.config.js": "Prettier",
            ".editorconfig": "EditorConfig",
            "pyproject.toml": None,  # Check for ruff/black
            "setup.cfg": None,
            ".flake8": "Flake8",
            "rustfmt.toml": "Rustfmt",
            ".golangci.yml": "GolangCI-Lint",
        }

        for config_file, tool in style_configs.items():
            if config_file in profile.key_files_content:
                if tool:
                    profile.code_style[tool.lower()] = True
                else:
                    # Check pyproject.toml for tools
                    content = profile.key_files_content.get(config_file, "")
                    if "ruff" in content:
                        profile.code_style["ruff"] = True
                    if "black" in content:
                        profile.code_style["black"] = True
                    if "isort" in content:
                        profile.code_style["isort"] = True

        # Detect naming conventions from sample files
        self._detect_naming_conventions(profile)

    def _detect_naming_conventions(self, profile: CodebaseProfile) -> None:
        """Detect naming conventions used in the codebase."""
        # Analyze file names
        file_names = [f.relative_path for f in profile.structure.files]

        # Check file naming style
        snake_case = sum(1 for f in file_names if "_" in os.path.basename(f))
        kebab_case = sum(1 for f in file_names if "-" in os.path.basename(f) and "_" not in os.path.basename(f))
        camel_case = sum(1 for f in file_names if re.match(r'^[a-z]+[A-Z]', os.path.basename(f)))

        total = snake_case + kebab_case + camel_case
        if total > 0:
            if snake_case / (total + 1) > 0.5:
                profile.naming_conventions["files"] = "snake_case"
            elif kebab_case / (total + 1) > 0.5:
                profile.naming_conventions["files"] = "kebab-case"
            elif camel_case / (total + 1) > 0.3:
                profile.naming_conventions["files"] = "camelCase"

        # Set defaults based on language
        if profile.primary_language == "python":
            profile.naming_conventions.setdefault("functions", "snake_case")
            profile.naming_conventions.setdefault("classes", "PascalCase")
            profile.naming_conventions.setdefault("constants", "UPPER_SNAKE_CASE")
        elif profile.primary_language in ["javascript", "typescript"]:
            profile.naming_conventions.setdefault("functions", "camelCase")
            profile.naming_conventions.setdefault("classes", "PascalCase")
            profile.naming_conventions.setdefault("constants", "UPPER_SNAKE_CASE")
        elif profile.primary_language == "go":
            profile.naming_conventions.setdefault("functions", "camelCase")
            profile.naming_conventions.setdefault("exported", "PascalCase")
        elif profile.primary_language == "rust":
            profile.naming_conventions.setdefault("functions", "snake_case")
            profile.naming_conventions.setdefault("types", "PascalCase")
            profile.naming_conventions.setdefault("constants", "UPPER_SNAKE_CASE")

    def _check_existing_docs(self, root: Path, profile: CodebaseProfile) -> None:
        """Check for existing documentation."""
        doc_files = ["README.md", "readme.md", "CONTRIBUTING.md", "CHANGELOG.md", "docs/"]

        for doc in doc_files:
            path = root / doc
            if path.exists():
                profile.existing_docs.append(doc)
                if "readme" in doc.lower():
                    profile.has_readme = True
                elif "contributing" in doc.lower():
                    profile.has_contributing = True
                elif "changelog" in doc.lower():
                    profile.has_changelog = True

        # Check for AI-specific docs
        ai_docs = ["CLAUDE.md", "GEMINI.md", "AGENTS.md", ".github/copilot-instructions.md"]
        for doc in ai_docs:
            if (root / doc).exists():
                profile.existing_docs.append(doc)

    def _detect_default_branch(self, root: Path) -> str:
        """Detect the default git branch."""
        head_file = root / ".git" / "HEAD"
        if head_file.exists():
            try:
                with open(head_file, "r") as f:
                    content = f.read().strip()
                    if content.startswith("ref: refs/heads/"):
                        return content.replace("ref: refs/heads/", "")
            except Exception:
                pass
        return "main"
