import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.agents.adr_recorder.indexer import ADRIndexer, SearchResult
from src.agents.adr_recorder.writer import ADR

@pytest.fixture
def mock_qdrant():
    return AsyncMock()

@pytest.fixture
def mock_embedder():
    embedder = AsyncMock()
    embedder.embed.return_value = [0.1, 0.2, 0.3]
    return embedder

@pytest.mark.asyncio
async def test_index_adr(mock_qdrant, mock_embedder):
    indexer = ADRIndexer(mock_qdrant, mock_embedder)

    adr = ADR(
        number=1,
        title="Test ADR",
        status="accepted",
        date=datetime.now(),
        context="Context",
        decision="Decision",
        consequences="Consequences",
        options_considered=[],
        deciders=[],
        source_link=None,
        supersedes=None,
        superseded_by=None
    )

    await indexer.index_adr(adr)

    mock_embedder.embed.assert_called_once()
    mock_qdrant.upsert.assert_called_once()

    # Check arguments
    args, kwargs = mock_qdrant.upsert.call_args
    assert kwargs["collection_name"] == "adr_embeddings"
    assert kwargs["points"][0]["id"] == 1
    assert kwargs["points"][0]["payload"]["title"] == "Test ADR"

@pytest.mark.asyncio
async def test_search(mock_qdrant, mock_embedder):
    indexer = ADRIndexer(mock_qdrant, mock_embedder)

    mock_result = MagicMock()
    mock_result.payload = {"number": 1, "title": "Test ADR", "context": "Ctx"}
    mock_result.score = 0.9

    mock_qdrant.search.return_value = [mock_result]

    results = await indexer.search("query")

    assert len(results) == 1
    assert results[0].adr_number == 1
    assert results[0].score == 0.9
    mock_embedder.embed.assert_called_with("query")
