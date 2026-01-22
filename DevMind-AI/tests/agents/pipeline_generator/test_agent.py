import pytest
from unittest.mock import MagicMock
from src.agents.pipeline_generator.agent import PipelineGeneratorAgent
from src.agents.base import AgentContext

@pytest.mark.asyncio
async def test_pipeline_generator_agent_execute():
    mock_llm_client = MagicMock()
    agent = PipelineGeneratorAgent(llm_client=mock_llm_client)

    context = AgentContext(
        repository_id="test-repo",
        user_id="user-1"
    )

    files = {
        "pyproject.toml": "dependencies = ['fastapi']",
    }

    result = await agent.execute(context, files=files, platform="github_actions")

    assert "analysis" in result
    assert result["analysis"]["project_type"] == "python"
    assert "pipeline" in result
    assert result["pipeline"]["platform"] == "github_actions"
    assert "optimization" in result
