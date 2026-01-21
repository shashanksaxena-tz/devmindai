# tests/agents/adr_recorder/test_indexer.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from src.agents.adr_recorder.writer import ADR
from src.agents.adr_recorder.indexer import ADRIndexer

@pytest.fixture
def mock_qdrant():
    client = AsyncMock()
    # Mock search result
    search_result = MagicMock()
    search_result.payload = {
        "number": 1,
        "title": "Test ADR",
        "status": "accepted",
        "context": "Context",
        "decision": "Decision",
        "date": "2023-01-01"
    }
    search_result.score = 0.95
    client.search.return_value = [search_result]
    return client

@pytest.fixture
def mock_embedder():
    embedder = AsyncMock()
    embedder.embed.return_value = [0.1, 0.2, 0.3]
    return embedder

@pytest.fixture
def indexer(mock_qdrant, mock_embedder):
    return ADRIndexer(mock_qdrant, mock_embedder)

@pytest.fixture
def sample_adr():
    return ADR(
        number=1,
        title="Test ADR",
        status="accepted",
        date=datetime.now(),
        context="Context",
        decision="Decision",
        consequences="",
        options_considered=[],
        deciders=[],
        source_link=None,
        supersedes=None,
        superseded_by=None
    )

@pytest.mark.asyncio
async def test_index_adr(indexer, mock_qdrant, mock_embedder, sample_adr):
    await indexer.index_adr(sample_adr)

    mock_embedder.embed.assert_called_once()
    mock_qdrant.upsert.assert_called_once()

    # Check payload
    call_kwargs = mock_qdrant.upsert.call_args.kwargs
    point = call_kwargs['points'][0]
    assert point['id'] == 1
    assert point['payload']['title'] == "Test ADR"

@pytest.mark.asyncio
async def test_search(indexer, mock_qdrant, mock_embedder):
    results = await indexer.search("query")

    assert len(results) == 1
    assert results[0].title == "Test ADR"
    assert results[0].score == 0.95

    mock_embedder.embed.assert_called_with("query")
    mock_qdrant.search.assert_called_once()

@pytest.mark.asyncio
async def test_search_with_filter(indexer, mock_qdrant, mock_embedder):
    await indexer.search("query", status_filter="accepted")

    mock_qdrant.search.assert_called_once()
    call_kwargs = mock_qdrant.search.call_args.kwargs
    assert call_kwargs['query_filter'] == {"status": "accepted"}
