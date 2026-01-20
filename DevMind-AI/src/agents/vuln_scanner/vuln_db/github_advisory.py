"""GitHub Advisory Database client.

Uses GitHub's GraphQL API to query the Security Advisory Database.
"""

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.config import settings
from src.agents.vuln_scanner.vuln_db.base import VulnerabilityDB, VulnerabilityInfo


class GitHubAdvisoryClient(VulnerabilityDB):
    """Client for GitHub Advisory Database."""

    GRAPHQL_URL = "https://api.github.com/graphql"

    def __init__(self, token: str | None = None):
        """Initialize GitHub Advisory client.

        Args:
            token: GitHub personal access token (optional, for higher rate limits)
        """
        self.token = token
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy-loaded HTTP client."""
        if self._client is None:
            headers = {"Accept": "application/vnd.github+json"}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            self._client = httpx.AsyncClient(headers=headers, timeout=30.0)
        return self._client

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def query_package(
        self,
        package_name: str,
        version: str,
        ecosystem: str,
    ) -> list[VulnerabilityInfo]:
        """Query GitHub Advisory for vulnerabilities."""
        # Map ecosystem to GitHub ecosystem
        ecosystem_map = {
            "npm": "NPM",
            "pypi": "PIP",
            "pip": "PIP",
            "cargo": "RUST",
            "maven": "MAVEN",
            "go": "GO",
            "composer": "COMPOSER",
            "nuget": "NUGET",
        }

        gh_ecosystem = ecosystem_map.get(ecosystem.lower(), ecosystem.upper())

        # GraphQL query
        query = """
        query($ecosystem: SecurityAdvisoryEcosystem!, $package: String!) {
            securityVulnerabilities(
                ecosystem: $ecosystem,
                package: $package,
                first: 100
            ) {
                nodes {
                    advisory {
                        ghsaId
                        summary
                        description
                        severity
                        cvss {
                            score
                        }
                        references {
                            url
                        }
                        publishedAt
                        withdrawnAt
                        identifiers {
                            type
                            value
                        }
                    }
                    vulnerableVersionRange
                    firstPatchedVersion {
                        identifier
                    }
                }
            }
        }
        """

        variables = {
            "ecosystem": gh_ecosystem,
            "package": package_name,
        }

        try:
            response = await self.client.post(
                self.GRAPHQL_URL,
                json={"query": query, "variables": variables},
            )
            response.raise_for_status()

            data = response.json()

            if "errors" in data:
                return []

            nodes = data.get("data", {}).get("securityVulnerabilities", {}).get("nodes", [])
            vulns = []

            for node in nodes:
                vuln = self._parse_vulnerability(node, package_name)
                if vuln and self._version_in_range(version, node.get("vulnerableVersionRange", "")):
                    vulns.append(vuln)

            return vulns

        except Exception:
            # Fall back to empty list on errors
            return []

    async def query_batch(
        self,
        packages: list[tuple[str, str, str]],
    ) -> dict[str, list[VulnerabilityInfo]]:
        """Query vulnerabilities for multiple packages."""
        results: dict[str, list[VulnerabilityInfo]] = {}

        # GitHub GraphQL doesn't have efficient batch queries for this,
        # so we query packages individually
        for name, version, ecosystem in packages:
            vulns = await self.query_package(name, version, ecosystem)
            results[name] = vulns

        return results

    def _parse_vulnerability(self, node: dict, package_name: str) -> VulnerabilityInfo | None:
        """Parse GitHub Advisory node into VulnerabilityInfo."""
        advisory = node.get("advisory", {})
        if not advisory:
            return None

        # Get CVE ID if available
        vuln_id = advisory.get("ghsaId", "")
        for ident in advisory.get("identifiers", []):
            if ident.get("type") == "CVE":
                vuln_id = ident.get("value", vuln_id)
                break

        # Parse severity
        severity_map = {
            "CRITICAL": "critical",
            "HIGH": "high",
            "MODERATE": "medium",
            "LOW": "low",
        }
        severity = severity_map.get(advisory.get("severity", ""), "unknown")

        # Get CVSS score
        cvss = advisory.get("cvss", {})
        cvss_score = cvss.get("score") if cvss else None

        # Get fixed version
        first_patched = node.get("firstPatchedVersion", {})
        fixed_version = first_patched.get("identifier") if first_patched else None

        return VulnerabilityInfo(
            id=vuln_id,
            package_name=package_name,
            affected_versions=[node.get("vulnerableVersionRange", "")],
            fixed_version=fixed_version,
            severity=severity,
            cvss_score=cvss_score,
            title=advisory.get("summary", ""),
            description=advisory.get("description", ""),
            references=[ref.get("url", "") for ref in advisory.get("references", [])],
            published_at=advisory.get("publishedAt"),
            withdrawn_at=advisory.get("withdrawnAt"),
        )

    def _version_in_range(self, version: str, version_range: str) -> bool:
        """Check if version is in the vulnerable range.

        This is a simplified check. Real implementation would use
        proper semver comparison.
        """
        if not version_range:
            return True

        # Parse range like "< 4.17.21" or ">= 1.0.0, < 2.0.0"
        version_parts = [int(p) for p in version.split(".")[:3] if p.isdigit()]

        for constraint in version_range.split(","):
            constraint = constraint.strip()
            if constraint.startswith("< "):
                max_ver = constraint[2:].strip()
                max_parts = [int(p) for p in max_ver.split(".")[:3] if p.isdigit()]
                if version_parts >= max_parts:
                    return False
            elif constraint.startswith(">= "):
                min_ver = constraint[3:].strip()
                min_parts = [int(p) for p in min_ver.split(".")[:3] if p.isdigit()]
                if version_parts < min_parts:
                    return False

        return True

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
