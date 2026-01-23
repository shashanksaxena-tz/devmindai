import pytest
from unittest.mock import AsyncMock
from datetime import datetime

from src.agents.adr_recorder.writer import ADRWriter, ADR
from src.agents.adr_recorder.capture import DecisionPoint, DecisionSource

@pytest.fixture
def mock_llm_client():
    return AsyncMock()

@pytest.mark.asyncio
async def test_generate_adr(mock_llm_client):
    writer = ADRWriter(mock_llm_client)

    decision = DecisionPoint(
        id="test-1",
        source=DecisionSource.MANUAL,
        timestamp=datetime.now(),
        participants=["Alice"],
        context="Choose DB",
        options_discussed=[],
        decision_made="Postgres",
        rationale="Better",
        raw_content="Use Postgres"
    )

    mock_response = {
        "title": "Use PostgreSQL",
        "context": "We need a relational DB.",
        "decision": "We will use PostgreSQL.",
        "consequences": "Good performance.",
        "options": [{"name": "Postgres", "description": "Relational DB", "pros": ["Fast"], "cons": ["Complex"], "chosen": True}]
    }
    mock_llm_client.generate_structured.return_value = mock_response

    adr = await writer.generate_adr(decision, adr_number=1)

    assert adr.number == 1
    assert adr.title == "Use PostgreSQL"
    assert adr.status == "accepted"
    assert "Postgres" in adr.to_markdown()
    assert "We need a relational DB" in adr.to_markdown()

@pytest.mark.asyncio
async def test_enrich_decision_supersedes(mock_llm_client):
    writer = ADRWriter(mock_llm_client)

    old_adr = ADR(
        number=1,
        title="Use MySQL",
        status="accepted",
        date=datetime.now(),
        context="Need DB",
        decision="MySQL",
        consequences="",
        options_considered=[],
        deciders=[],
        source_link=None,
        supersedes=None,
        superseded_by=None
    )

    decision = DecisionPoint(
        id="test-2",
        source=DecisionSource.MANUAL,
        timestamp=datetime.now(),
        participants=["Bob"],
        context="Need DB but better",
        options_discussed=[],
        decision_made="Postgres",
        rationale="MySQL is slow",
        raw_content="Switch to Postgres"
    )

    # The logic is: simple keyword matching. "Need DB" matches "Need DB but better"
    enrichment = await writer._enrich_decision(decision, [old_adr])
    assert enrichment.get("supersedes") == 1
