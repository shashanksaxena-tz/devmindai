"""Base classes for dependency parsing."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Dependency:
    """Represents a software dependency."""

    name: str
    version: str
    ecosystem: str  # npm, pypi, cargo, maven, go
    is_dev: bool = False
    is_transitive: bool = False
    parent: str | None = None
    extras: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_purl(self) -> str:
        """Convert to Package URL (purl) format.

        See: https://github.com/package-url/purl-spec
        """
        ecosystem_map = {
            "npm": "npm",
            "pypi": "pypi",
            "pip": "pypi",
            "cargo": "cargo",
            "maven": "maven",
            "go": "golang",
        }
        purl_type = ecosystem_map.get(self.ecosystem.lower(), self.ecosystem.lower())
        return f"pkg:{purl_type}/{self.name}@{self.version}"

    def __hash__(self) -> int:
        return hash((self.name, self.version, self.ecosystem))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Dependency):
            return False
        return (
            self.name == other.name
            and self.version == other.version
            and self.ecosystem == other.ecosystem
        )


class DependencyParser(ABC):
    """Abstract base class for dependency parsers."""

    ecosystem: str = "unknown"

    @abstractmethod
    def parse(self, content: Any) -> list[Dependency]:
        """Parse dependencies from content.

        Args:
            content: The content to parse (dict, string, etc.)

        Returns:
            List of parsed dependencies
        """
        pass

    @abstractmethod
    def parse_file(self, file_path: str) -> list[Dependency]:
        """Parse dependencies from a file.

        Args:
            file_path: Path to the dependency file

        Returns:
            List of parsed dependencies
        """
        pass
