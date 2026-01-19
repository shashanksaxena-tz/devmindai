"""Tests for base agent framework."""

from unittest.mock import AsyncMock, patch

import pytest


class TestBaseAgent:
    """Test suite for BaseAgent."""

    def test_agent_has_required_attributes(self):
        """Agent should have name, description, and llm_client."""
        from src.agents.base import BaseAgent
        from src.core.llm import TaskComplexity

        class TestAgent(BaseAgent):
            name = "test_agent"
            description = "A test agent"
            complexity = TaskComplexity.SIMPLE

            async def execute(self, **kwargs):
                return {"result": "success"}

        agent = TestAgent()

        assert agent.name == "test_agent"
        assert agent.description == "A test agent"
        assert agent.llm_client is not None

    @pytest.mark.asyncio
    async def test_agent_execute_returns_result(self):
        """Agent execute should return a result."""
        from src.agents.base import BaseAgent
        from src.core.llm import TaskComplexity

        class TestAgent(BaseAgent):
            name = "test_agent"
            description = "A test agent"
            complexity = TaskComplexity.SIMPLE

            async def execute(self, **kwargs):
                return {"status": "completed", "data": kwargs.get("input")}

        agent = TestAgent()
        result = await agent.execute(input="test_data")

        assert result["status"] == "completed"
        assert result["data"] == "test_data"

    @pytest.mark.asyncio
    async def test_agent_run_with_context(self):
        """Agent run should execute with context."""
        from src.agents.base import AgentContext, BaseAgent
        from src.core.llm import TaskComplexity

        class TestAgent(BaseAgent):
            name = "test_agent"
            description = "A test agent"
            complexity = TaskComplexity.SIMPLE

            async def execute(self, context: AgentContext, **kwargs):
                return {
                    "repo": context.repository_id,
                    "org": context.organization_id,
                }

        agent = TestAgent()
        context = AgentContext(
            organization_id="org-123",
            repository_id="repo-456",
        )

        result = await agent.run(context)

        assert result["repo"] == "repo-456"
        assert result["org"] == "org-123"
