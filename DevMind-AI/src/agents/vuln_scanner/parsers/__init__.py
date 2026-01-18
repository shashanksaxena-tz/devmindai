"""Dependency parsers for different package ecosystems."""

from src.agents.vuln_scanner.parsers.base import Dependency, DependencyParser
from src.agents.vuln_scanner.parsers.npm import NpmParser
from src.agents.vuln_scanner.parsers.pip import PipParser

__all__ = [
    "Dependency",
    "DependencyParser",
    "NpmParser",
    "PipParser",
]
