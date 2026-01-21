"""Base classes for vulnerability databases."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class VulnerabilityInfo:
    """Information about a vulnerability."""

    id: str  # CVE ID or GHSA ID
    package_name: str
    affected_versions: list[str]
    fixed_version: str | None = None
    severity: Literal["critical", "high", "medium", "low", "unknown"] = "unknown"
    cvss_score: float | None = None
    title: str = ""
    description: str = ""
    references: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    published_at: str | None = None
    withdrawn_at: str | None = None

    def is_version_affected(self, version: str) -> bool:
        """Check if a specific version is affected.

        This is a simplified check. Real implementation would use
        semver comparison.
        """
        # Simple containment check for now
        for affected in self.affected_versions:
            if version in affected or affected == "*":
                return True
            # Check if version is less than fixed version
            if self.fixed_version and version < self.fixed_version:
                return True
        return False


class VulnerabilityDB(ABC):
    """Abstract base class for vulnerability database clients."""

    @abstractmethod
    async def query_package(
        self,
        package_name: str,
        version: str,
        ecosystem: str,
    ) -> list[VulnerabilityInfo]:
        """Query vulnerabilities for a package.

        Args:
            package_name: Name of the package
            version: Version of the package
            ecosystem: Package ecosystem (npm, pypi, etc.)

        Returns:
            List of vulnerabilities affecting the package
        """
        pass

    @abstractmethod
    async def query_batch(
        self,
        packages: list[tuple[str, str, str]],  # (name, version, ecosystem)
    ) -> dict[str, list[VulnerabilityInfo]]:
        """Query vulnerabilities for multiple packages.

        Args:
            packages: List of (name, version, ecosystem) tuples

        Returns:
            Dict mapping package names to their vulnerabilities
        """
        pass
