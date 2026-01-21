# tests/agents/adr_recorder/test_agent.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.agents.adr_recorder.agent import ADRRecorderAgent
from src.agents.base import AgentContext

@pytest.fixture
def mock_clients():
    llm = AsyncMock()
    # Mock structured generation
    # When mocking AsyncMock, we need to ensure nested attributes are also handled correctly if they are methods.
    # However, for side_effect to work with different return values for different calls, we can set it on the main mock if we use the same method.
    # Here capture uses generate_structured and writer uses generate_structured.

    llm.generate_structured = AsyncMock()
    llm.generate_structured.side_effect = [
        # First call: Capture
        {"decisions": [{"context": "Ctx", "decision": "Dec", "options": []}]},
        # Second call: Writer
        {"title": "Title", "context": "Ctx", "decision": "Dec", "consequences": "Cons", "options": []}
    ]

    qdrant = AsyncMock()
    embedder = AsyncMock()
    embedder.embed.return_value = [0.1]

    return llm, qdrant, embedder

@pytest.fixture
def agent(mock_clients):
    llm, qdrant, embedder = mock_clients
    return ADRRecorderAgent(llm, qdrant, embedder)

@pytest.mark.asyncio
async def test_execute_capture(agent, mock_clients):
    llm, qdrant, embedder = mock_clients
    context = MagicMock(spec=AgentContext)

    result = await agent.execute(
        context,
        action="capture",
        messages=[{"author": "A", "content": "Let's use X"}],
        source="slack"
    )

    assert result["decisions_found"] == 1
    assert result["adrs_generated"] == 1
    assert len(result["adrs"]) == 1

    # Verify sub-components called
    # Both capture and writer use generate_structured
    assert llm.generate_structured.call_count == 2
    qdrant.upsert.assert_called_once() # Indexer

@pytest.mark.asyncio
async def test_execute_search(agent, mock_clients):
    llm, qdrant, embedder = mock_clients
    context = MagicMock(spec=AgentContext)

    # Mock search result
    search_result = MagicMock()
    search_result.payload = {"number": 1, "title": "T", "context": "C"}
    search_result.score = 0.9
    qdrant.search.return_value = [search_result]

    result = await agent.execute(
        context,
        action="search",
        query="test"
    )

    assert len(result["results"]) == 1
    qdrant.search.assert_called_once()
