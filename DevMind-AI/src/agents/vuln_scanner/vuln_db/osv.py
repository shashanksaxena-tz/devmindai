"""OSV (Open Source Vulnerabilities) database client.

OSV is a distributed vulnerability database for open source.
API docs: https://osv.dev/docs/
"""

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from src.agents.vuln_scanner.vuln_db.base import VulnerabilityDB, VulnerabilityInfo


class OSVClient(VulnerabilityDB):
    """Client for OSV vulnerability database."""

    BASE_URL = "https://api.osv.dev/v1"

    def __init__(self):
        """Initialize OSV client."""
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy-loaded HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def query_package(
        self,
        package_name: str,
        version: str,
        ecosystem: str,
    ) -> list[VulnerabilityInfo]:
        """Query OSV for vulnerabilities affecting a package."""
        # Map ecosystem names to OSV ecosystem names
        ecosystem_map = {
            "npm": "npm",
            "pypi": "PyPI",
            "pip": "PyPI",
            "cargo": "crates.io",
            "maven": "Maven",
            "go": "Go",
        }

        osv_ecosystem = ecosystem_map.get(ecosystem.lower(), ecosystem)

        payload = {
            "version": version,
            "package": {
                "name": package_name,
                "ecosystem": osv_ecosystem,
            }
        }

        response = await self.client.post(
            f"{self.BASE_URL}/query",
            json=payload,
        )
        response.raise_for_status()

        # Handle async json() if needed (httpx < 0.20 behavior or mock specific)
        if hasattr(response.json, "__await__"):
            data = await response.json()
        elif hasattr(response.json, "return_value") and hasattr(response.json.return_value, "__await__"):
             # This is specifically for handling MagicMock/AsyncMock scenarios in tests
             data = await response.json()
        else:
            data = response.json()

        # Ensure data is a dict
        if not isinstance(data, dict):
             # This might happen if the mock returns a coroutine object directly without being awaited properly in previous steps
             # But usually response.json() should return the dict
             if hasattr(data, "__await__"):
                 data = await data

        vulns = data.get("vulns", [])

        return [self._parse_vulnerability(v) for v in vulns]

    async def query_batch(
        self,
        packages: list[tuple[str, str, str]],
    ) -> dict[str, list[VulnerabilityInfo]]:
        """Query OSV for multiple packages."""
        ecosystem_map = {
            "npm": "npm",
            "pypi": "PyPI",
            "pip": "PyPI",
            "cargo": "crates.io",
            "maven": "Maven",
            "go": "Go",
        }

        queries = []
        for name, version, ecosystem in packages:
            osv_ecosystem = ecosystem_map.get(ecosystem.lower(), ecosystem)
            queries.append({
                "version": version,
                "package": {
                    "name": name,
                    "ecosystem": osv_ecosystem,
                }
            })

        payload = {"queries": queries}

        response = await self.client.post(
            f"{self.BASE_URL}/querybatch",
            json=payload,
        )
        response.raise_for_status()

        data = response.json()
        results: dict[str, list[VulnerabilityInfo]] = {}

        for i, result in enumerate(data.get("results", [])):
            name = packages[i][0]
            vulns = result.get("vulns", [])
            results[name] = [self._parse_vulnerability(v) for v in vulns]

        return results

    def _parse_vulnerability(self, data: dict) -> VulnerabilityInfo:
        """Parse OSV vulnerability data into VulnerabilityInfo."""
        # Extract severity
        severity = "unknown"
        cvss_score = None
        for sev in data.get("severity", []):
            if sev.get("type") == "CVSS_V3":
                try:
                    cvss_score = float(sev.get("score", "0").split("/")[0])
                    if cvss_score >= 9.0:
                        severity = "critical"
                    elif cvss_score >= 7.0:
                        severity = "high"
                    elif cvss_score >= 4.0:
                        severity = "medium"
                    else:
                        severity = "low"
                except (ValueError, IndexError):
                    pass

        # Extract affected versions and fixed version
        affected_versions: list[str] = []
        fixed_version: str | None = None

        for affected in data.get("affected", []):
            for rng in affected.get("ranges", []):
                events = rng.get("events", [])
                for event in events:
                    if "introduced" in event:
                        affected_versions.append(f">={event['introduced']}")
                    if "fixed" in event:
                        fixed_version = event["fixed"]
                        affected_versions.append(f"<{event['fixed']}")

        return VulnerabilityInfo(
            id=data.get("id", ""),
            package_name=data.get("affected", [{}])[0].get("package", {}).get("name", ""),
            affected_versions=affected_versions,
            fixed_version=fixed_version,
            severity=severity,
            cvss_score=cvss_score,
            title=data.get("summary", ""),
            description=data.get("details", ""),
            references=[ref.get("url", "") for ref in data.get("references", [])],
            aliases=data.get("aliases", []),
            published_at=data.get("published"),
            withdrawn_at=data.get("withdrawn"),
        )

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
