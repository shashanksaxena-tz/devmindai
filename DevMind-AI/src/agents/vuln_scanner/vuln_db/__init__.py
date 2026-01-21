"""Vulnerability database clients."""

from src.agents.vuln_scanner.vuln_db.base import VulnerabilityDB, VulnerabilityInfo
from src.agents.vuln_scanner.vuln_db.github_advisory import GitHubAdvisoryClient
from src.agents.vuln_scanner.vuln_db.osv import OSVClient

__all__ = [
    "GitHubAdvisoryClient",
    "OSVClient",
    "VulnerabilityDB",
    "VulnerabilityInfo",
]
