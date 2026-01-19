"""VulnScanner Agent - Security vulnerability detection.

This agent scans project dependencies for known vulnerabilities,
analyzes exploitability, and provides remediation recommendations.
"""

from dataclasses import dataclass
from typing import Any

from src.agents.base import AgentContext, BaseAgent
from src.agents.vuln_scanner.analyzer import ExploitabilityAnalyzer
from src.agents.vuln_scanner.parsers import Dependency, NpmParser, PipParser
from src.agents.vuln_scanner.vuln_db import OSVClient, VulnerabilityInfo
from src.core.llm import TaskComplexity


@dataclass
class ScanResult:
    """Result of a vulnerability scan."""

    package_name: str
    package_version: str
    vulnerability: VulnerabilityInfo
    is_exploitable: bool | None = None
    exploit_confidence: float = 0.0
    remediation: str | None = None


class VulnScannerAgent(BaseAgent):
    """Agent for scanning dependencies for security vulnerabilities."""

    name = "vuln_scanner"
    description = "Scans project dependencies for security vulnerabilities and assesses exploitability"
    complexity = TaskComplexity.SIMPLE  # Uses Gemini for fast scanning

    def __init__(self, **kwargs):
        """Initialize VulnScanner agent."""
        super().__init__(**kwargs)

        # Initialize parsers
        self._npm_parser = NpmParser()
        self._pip_parser = PipParser()

        # Initialize vulnerability database client
        self._vuln_db = OSVClient()

        # Initialize exploitability analyzer
        self._exploitability = ExploitabilityAnalyzer()

    async def execute(self, context: AgentContext, **kwargs: Any) -> dict[str, Any]:
        """Execute vulnerability scan for a repository.

        Args:
            context: Agent execution context
            **kwargs: Additional arguments
                - repo_path: Path to repository (required)
                - full_scan: Whether to do full exploitability analysis

        Returns:
            Scan results with vulnerabilities and recommendations
        """
        repo_path = kwargs.get("repo_path") or context.metadata.get("repo_path")
        if not repo_path:
            return {"error": "repo_path is required"}

        full_scan = kwargs.get("full_scan", False)

        # Scan the repository
        return await self.scan_repository(repo_path, full_scan=full_scan)

    async def scan_repository(
        self,
        repo_path: str,
        full_scan: bool = False,
    ) -> dict[str, Any]:
        """Scan a repository for vulnerabilities.

        Args:
            repo_path: Path to the repository
            full_scan: Whether to perform exploitability analysis

        Returns:
            Comprehensive scan results
        """
        from pathlib import Path

        results: dict[str, Any] = {
            "total_dependencies": 0,
            "vulnerabilities": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
            },
            "exploitable": 0,
            "details": [],
        }

        # Find and parse dependency files
        dependencies: list[Dependency] = []

        # NPM
        package_lock = Path(repo_path) / "package-lock.json"
        if package_lock.exists():
            deps = self._npm_parser.parse_file(str(package_lock))
            dependencies.extend(deps)

        # Python
        requirements = Path(repo_path) / "requirements.txt"
        if requirements.exists():
            deps = self._pip_parser.parse_file(str(requirements))
            dependencies.extend(deps)

        poetry_lock = Path(repo_path) / "poetry.lock"
        if poetry_lock.exists():
            deps = self._pip_parser.parse_file(str(poetry_lock))
            dependencies.extend(deps)

        results["total_dependencies"] = len(dependencies)

        if not dependencies:
            return results

        # Scan dependencies for vulnerabilities
        vuln_map = await self.scan_dependencies(dependencies)

        # Process results
        for dep in dependencies:
            vulns = vuln_map.get(dep.name, [])
            for vuln in vulns:
                # Count by severity
                severity = vuln.severity.lower()
                if severity in results["vulnerabilities"]:
                    results["vulnerabilities"][severity] += 1

                scan_result = ScanResult(
                    package_name=dep.name,
                    package_version=dep.version,
                    vulnerability=vuln,
                )

                # Perform exploitability analysis if requested
                if full_scan and vuln.severity in ["critical", "high"]:
                    exploitability = await self._analyze_exploitability(
                        repo_path, dep, vuln
                    )
                    scan_result.is_exploitable = exploitability.is_exploitable
                    scan_result.exploit_confidence = exploitability.confidence

                    if exploitability.is_exploitable:
                        results["exploitable"] += 1

                # Generate remediation advice
                scan_result.remediation = self._generate_remediation(dep, vuln)

                results["details"].append({
                    "package": scan_result.package_name,
                    "version": scan_result.package_version,
                    "vulnerability_id": vuln.id,
                    "severity": vuln.severity,
                    "cvss_score": vuln.cvss_score,
                    "title": vuln.title,
                    "fix_version": vuln.fixed_version,
                    "is_exploitable": scan_result.is_exploitable,
                    "exploit_confidence": scan_result.exploit_confidence,
                    "remediation": scan_result.remediation,
                })

        return results

    async def scan_dependencies(
        self,
        dependencies: list[Dependency],
    ) -> dict[str, list[VulnerabilityInfo]]:
        """Scan a list of dependencies for vulnerabilities.

        Args:
            dependencies: List of dependencies to scan

        Returns:
            Dict mapping package names to their vulnerabilities
        """
        # Prepare batch query
        packages = [
            (dep.name, dep.version, dep.ecosystem)
            for dep in dependencies
        ]

        # Query vulnerability database
        return await self._vuln_db.query_batch(packages)

    async def _analyze_exploitability(
        self,
        repo_path: str,
        dependency: Dependency,
        vulnerability: VulnerabilityInfo,
    ) -> Any:
        """Analyze if a vulnerability is exploitable in the codebase.

        Args:
            repo_path: Path to repository
            dependency: The vulnerable dependency
            vulnerability: The vulnerability info

        Returns:
            ExploitabilityResult
        """
        # Get vulnerable functions based on vulnerability type
        vulnerable_functions = self._get_vulnerable_functions(
            dependency.name,
            vulnerability.id,
        )

        if not vulnerable_functions:
            # Can't analyze without knowing vulnerable functions
            from src.agents.vuln_scanner.analyzer import ExploitabilityResult
            return ExploitabilityResult(
                is_imported=True,
                is_used=True,
                user_input_reachable=True,  # Assume worst case
                confidence=0.5,
                analysis_notes="Unable to determine specific vulnerable functions.",
            )

        # Run exploitability analysis
        return await self._exploitability.analyze_repository(
            repo_path,
            dependency.name,
            vulnerable_functions,
        )

    def _get_vulnerable_functions(
        self,
        package_name: str,
        vulnerability_id: str,
    ) -> list[str]:
        """Get list of vulnerable functions for a known vulnerability.

        This is a simplified mapping. A full implementation would
        query a database of known vulnerable patterns.
        """
        # Known vulnerable functions by package
        known_vulns = {
            "lodash": {
                "prototype_pollution": ["merge", "mergeWith", "set", "setWith"],
            },
            "axios": {
                "ssrf": ["get", "post", "request"],
            },
            "express": {
                "path_traversal": ["sendFile", "static"],
            },
            "requests": {
                "ssrf": ["get", "post", "request"],
            },
            "pyyaml": {
                "arbitrary_code": ["load", "unsafe_load"],
            },
        }

        pkg_vulns = known_vulns.get(package_name.lower(), {})

        # Try to match vulnerability type
        vuln_id_lower = vulnerability_id.lower()
        for vuln_type, functions in pkg_vulns.items():
            if vuln_type in vuln_id_lower:
                return functions

        # Return all known vulnerable functions for the package
        all_functions: list[str] = []
        for functions in pkg_vulns.values():
            all_functions.extend(functions)
        return all_functions

    def _generate_remediation(
        self,
        dependency: Dependency,
        vulnerability: VulnerabilityInfo,
    ) -> str:
        """Generate remediation advice for a vulnerability.

        Args:
            dependency: The vulnerable dependency
            vulnerability: The vulnerability info

        Returns:
            Remediation advice string
        """
        if vulnerability.fixed_version:
            return (
                f"Upgrade {dependency.name} from {dependency.version} "
                f"to {vulnerability.fixed_version} or later."
            )

        return (
            f"No fix available for {vulnerability.id}. "
            f"Consider finding an alternative to {dependency.name} "
            f"or implementing additional security controls."
        )

    async def close(self):
        """Clean up resources."""
        await self._vuln_db.close()
