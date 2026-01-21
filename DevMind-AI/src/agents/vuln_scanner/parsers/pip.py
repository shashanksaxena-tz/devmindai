"""Python pip/poetry dependency parser."""

import re
import tomllib
from pathlib import Path
from typing import Any

from src.agents.vuln_scanner.parsers.base import Dependency, DependencyParser


class PipParser(DependencyParser):
    """Parser for Python requirements.txt and poetry.lock files."""

    ecosystem = "pypi"

    def parse(self, content: Any) -> list[Dependency]:
        """Parse content (auto-detect format).

        Args:
            content: String content or dict

        Returns:
            List of dependencies
        """
        if isinstance(content, str):
            if "[[package]]" in content:
                return self.parse_poetry_lock(content)
            else:
                return self.parse_requirements(content)
        elif isinstance(content, dict):
            return self.parse_pipfile_lock(content)
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")

    def parse_requirements(self, content: str) -> list[Dependency]:
        """Parse requirements.txt format.

        Args:
            content: Contents of requirements.txt

        Returns:
            List of dependencies
        """
        dependencies: list[Dependency] = []

        for line in content.strip().split("\n"):
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith("#") or line.startswith("-"):
                continue

            # Skip editable installs
            if line.startswith("-e"):
                continue

            # Parse the requirement
            dep = self._parse_requirement_line(line)
            if dep:
                dependencies.append(dep)

        return dependencies

    def _parse_requirement_line(self, line: str) -> Dependency | None:
        """Parse a single requirement line.

        Handles formats like:
        - requests==2.28.0
        - flask>=2.0.0,<3.0.0
        - sqlalchemy[asyncio]==2.0.25
        """
        # Remove comments
        line = line.split("#")[0].strip()
        if not line:
            return None

        # Extract extras like [asyncio]
        extras: list[str] = []
        extras_match = re.search(r"\[([^\]]+)\]", line)
        if extras_match:
            extras = [e.strip() for e in extras_match.group(1).split(",")]
            line = line.replace(extras_match.group(0), "")

        # Parse name and version
        # Match patterns: name==version, name>=version, name~=version, etc.
        match = re.match(r"^([a-zA-Z0-9_-]+)\s*([=<>~!]+)?\s*([0-9][^,;\s]*)?", line)

        if not match:
            return None

        name = match.group(1).lower()
        version = match.group(3) or "unknown"

        return Dependency(
            name=name,
            version=version,
            ecosystem=self.ecosystem,
            extras=extras,
        )

    def parse_poetry_lock(self, content: str) -> list[Dependency]:
        """Parse poetry.lock TOML format.

        Args:
            content: Contents of poetry.lock

        Returns:
            List of dependencies
        """
        dependencies: list[Dependency] = []

        try:
            data = tomllib.loads(content)
        except tomllib.TOMLDecodeError:
            # Fallback or empty if not valid TOML
            return []

        for package in data.get("package", []):
            name = package.get("name")
            version = package.get("version")

            if name and version:
                dep = Dependency(
                    name=name,
                    version=version,
                    ecosystem=self.ecosystem,
                )
                dependencies.append(dep)

        return dependencies

    def parse_pipfile_lock(self, content: dict[str, Any]) -> list[Dependency]:
        """Parse Pipfile.lock JSON format.

        Args:
            content: Parsed JSON content of Pipfile.lock

        Returns:
            List of dependencies
        """
        dependencies: list[Dependency] = []

        for section in ["default", "develop"]:
            is_dev = section == "develop"
            packages = content.get(section, {})

            for name, info in packages.items():
                version = info.get("version", "").lstrip("=")
                if not version:
                    continue

                dep = Dependency(
                    name=name.lower(),
                    version=version,
                    ecosystem=self.ecosystem,
                    is_dev=is_dev,
                )
                dependencies.append(dep)

        return dependencies

    def parse_file(self, file_path: str) -> list[Dependency]:
        """Parse dependencies from a file.

        Args:
            file_path: Path to requirements.txt, poetry.lock, or Pipfile.lock

        Returns:
            List of dependencies
        """
        path = Path(file_path)

        with open(path) as f:
            content = f.read()

        if path.name == "Pipfile.lock":
            import json
            return self.parse_pipfile_lock(json.loads(content))
        else:
            return self.parse(content)
