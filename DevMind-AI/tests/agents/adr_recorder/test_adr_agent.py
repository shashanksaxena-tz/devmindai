import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.agents.adr_recorder.agent import ADRRecorderAgent
from src.agents.base import AgentContext
from src.agents.adr_recorder.capture import DecisionPoint, DecisionSource

@pytest.fixture
def mock_llm_client():
    client = AsyncMock()
    # Mock responses for different calls
    client.generate_structured.side_effect = [
        # First call: analyze_conversation
        {"decisions": [{"context": "Ctx", "decision": "Dec", "options": []}]},
        # Second call: generate_adr
        {"title": "Title", "context": "Ctx", "decision": "Dec", "consequences": "Cons", "options": []}
    ]
    return client

@pytest.fixture
def mock_router(mock_llm_client):
    router = MagicMock()
    router.get_client.return_value = mock_llm_client
    return router

@pytest.mark.asyncio
async def test_execute_capture(mock_router):
    agent = ADRRecorderAgent(router=mock_router)
    context = AgentContext()

    messages = [{"author": "User", "content": "Let's use Redis."}]

    result = await agent.execute(
        context,
        action="capture",
        messages=messages,
        source="slack"
    )

    assert result["decisions_found"] == 1
    assert result["adrs_generated"] == 1
    assert len(result["adrs"]) == 1
    assert result["adrs"][0]["title"] == "Title"

@pytest.mark.asyncio
async def test_execute_search_no_indexer(mock_router):
    agent = ADRRecorderAgent(router=mock_router)
    context = AgentContext()

    result = await agent.execute(context, action="search", query="something")

    assert "error" in result
    assert result["error"] == "Indexer not configured"
