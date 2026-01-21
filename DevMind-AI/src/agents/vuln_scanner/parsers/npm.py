"""NPM/Yarn dependency parser."""

import json
import re
from pathlib import Path
from typing import Any

from src.agents.vuln_scanner.parsers.base import Dependency, DependencyParser


class NpmParser(DependencyParser):
    """Parser for NPM package-lock.json and package.json files."""

    ecosystem = "npm"

    def parse(self, content: dict[str, Any]) -> list[Dependency]:
        """Parse package-lock.json content.

        Args:
            content: Parsed JSON content of package-lock.json

        Returns:
            List of dependencies
        """
        dependencies: list[Dependency] = []

        # Handle lockfileVersion 2/3 format
        packages = content.get("packages", {})
        for path, pkg_info in packages.items():
            # Skip the root package
            if path == "":
                continue

            # Extract package name from path
            name = path.replace("node_modules/", "").split("/node_modules/")[-1]

            # Handle scoped packages
            if name.startswith("@"):
                # Scoped package like @babel/core
                pass

            version = pkg_info.get("version", "")
            if not version:
                continue

            dep = Dependency(
                name=name,
                version=version,
                ecosystem=self.ecosystem,
                is_dev=pkg_info.get("dev", False),
                is_transitive="node_modules/" in path.replace("node_modules/", "", 1),
                metadata={
                    "resolved": pkg_info.get("resolved", ""),
                    "integrity": pkg_info.get("integrity", ""),
                },
            )
            dependencies.append(dep)

        # Handle older lockfileVersion 1 format
        if not packages and "dependencies" in content:
            dependencies.extend(self._parse_v1_dependencies(content["dependencies"]))

        return dependencies

    def _parse_v1_dependencies(
        self,
        deps: dict[str, Any],
        is_transitive: bool = False,
    ) -> list[Dependency]:
        """Parse lockfileVersion 1 dependencies recursively."""
        result: list[Dependency] = []

        for name, info in deps.items():
            version = info.get("version", "")
            if not version:
                continue

            dep = Dependency(
                name=name,
                version=version,
                ecosystem=self.ecosystem,
                is_dev=info.get("dev", False),
                is_transitive=is_transitive,
            )
            result.append(dep)

            # Parse nested dependencies
            if "dependencies" in info:
                result.extend(
                    self._parse_v1_dependencies(info["dependencies"], is_transitive=True)
                )

        return result

    def parse_package_json(
        self,
        content: dict[str, Any],
        include_dev: bool = True,
    ) -> list[Dependency]:
        """Parse package.json for direct dependencies.

        Note: This only gets version ranges, not resolved versions.
        Use package-lock.json for exact versions.

        Args:
            content: Parsed JSON content of package.json
            include_dev: Whether to include devDependencies

        Returns:
            List of dependencies with version ranges
        """
        dependencies: list[Dependency] = []

        # Production dependencies
        for name, version_range in content.get("dependencies", {}).items():
            # Strip version prefixes like ^, ~, >=
            version = re.sub(r"^[\^~>=<]+", "", version_range)
            dep = Dependency(
                name=name,
                version=version,
                ecosystem=self.ecosystem,
                is_dev=False,
            )
            dependencies.append(dep)

        # Dev dependencies
        if include_dev:
            for name, version_range in content.get("devDependencies", {}).items():
                version = re.sub(r"^[\^~>=<]+", "", version_range)
                dep = Dependency(
                    name=name,
                    version=version,
                    ecosystem=self.ecosystem,
                    is_dev=True,
                )
                dependencies.append(dep)

        return dependencies

    def parse_file(self, file_path: str) -> list[Dependency]:
        """Parse dependencies from a file.

        Args:
            file_path: Path to package-lock.json or package.json

        Returns:
            List of dependencies
        """
        path = Path(file_path)

        with open(path) as f:
            content = json.load(f)

        if path.name == "package-lock.json":
            return self.parse(content)
        elif path.name == "package.json":
            return self.parse_package_json(content)
        else:
            raise ValueError(f"Unsupported file: {path.name}")
