"""Tests for VulnScanner agent."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents.base import AgentContext


class TestVulnScannerAgent:
    """Test suite for VulnScannerAgent."""

    @pytest.fixture
    def agent(self):
        """Create VulnScannerAgent instance."""
        from src.agents.vuln_scanner.agent import VulnScannerAgent
        return VulnScannerAgent()

    def test_agent_has_correct_name(self, agent):
        """Agent should have correct name and description."""
        assert agent.name == "vuln_scanner"
        assert "vulnerabilities" in agent.description.lower()

    @pytest.mark.asyncio
    async def test_scan_dependencies_returns_results(self, agent):
        """Should scan dependencies and return vulnerability results."""
        # Mock the vulnerability database
        with patch.object(agent, '_vuln_db') as mock_db:
            mock_db.query_batch = AsyncMock(return_value={
                "lodash": [
                    MagicMock(
                        id="CVE-2024-1234",
                        severity="high",
                        cvss_score=7.5,
                        fixed_version="4.17.21",
                    )
                ],
                "axios": [],
            })

            # Mock dependencies
            dependencies = [
                MagicMock(name="lodash", version="4.17.20", ecosystem="npm"),
                MagicMock(name="axios", version="1.6.0", ecosystem="npm"),
            ]

            results = await agent.scan_dependencies(dependencies)

            assert "lodash" in results
            assert len(results["lodash"]) == 1
            assert results["lodash"][0].id == "CVE-2024-1234"

    @pytest.mark.asyncio
    async def test_execute_with_repo_context(self, agent):
        """Should execute full scan with repository context."""
        context = AgentContext(
            organization_id="org-123",
            repository_id="repo-456",
            metadata={"repo_path": "/tmp/test-repo"},
        )

        with patch.object(agent, 'scan_repository') as mock_scan:
            mock_scan.return_value = {
                "total_dependencies": 50,
                "vulnerabilities": {
                    "critical": 0,
                    "high": 2,
                    "medium": 5,
                    "low": 10,
                },
                "details": [],
            }

            result = await agent.execute(context)

            assert result["total_dependencies"] == 50
            assert result["vulnerabilities"]["high"] == 2


class TestVulnScannerIntegration:
    """Integration tests for VulnScannerAgent."""

    @pytest.mark.asyncio
    async def test_parse_and_scan_npm_project(self):
        """Should parse package-lock.json and scan for vulnerabilities."""
        from src.agents.vuln_scanner.agent import VulnScannerAgent

        agent = VulnScannerAgent()

        # Create a mock package-lock.json
        package_lock = {
            "name": "test-project",
            "lockfileVersion": 3,
            "packages": {
                "": {"name": "test-project", "version": "1.0.0"},
                "node_modules/lodash": {"version": "4.17.20"},
            }
        }

        # Parse dependencies
        deps = agent._npm_parser.parse(package_lock)

        assert len(deps) == 1
        assert deps[0].name == "lodash"
