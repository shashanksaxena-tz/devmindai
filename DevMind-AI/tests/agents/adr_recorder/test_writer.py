# tests/agents/adr_recorder/test_writer.py
import pytest
from unittest.mock import AsyncMock
from datetime import datetime
from src.agents.adr_recorder.capture import DecisionPoint, DecisionSource
from src.agents.adr_recorder.writer import ADRWriter, ADR

@pytest.fixture
def mock_llm():
    llm = AsyncMock()
    llm.generate_structured = AsyncMock()
    llm.generate_structured.return_value = {
        "title": "Use PostgreSQL",
        "context": "We need a database.",
        "decision": "We chose PostgreSQL.",
        "consequences": "Good performance, but maintenance cost.",
        "options": [
            {"name": "PostgreSQL", "description": "Relational DB", "pros": ["Reliable"], "cons": ["Complex"], "chosen": True}
        ]
    }
    return llm

@pytest.fixture
def writer(mock_llm):
    return ADRWriter(mock_llm)

@pytest.fixture
def sample_decision():
    return DecisionPoint(
        id="test-1",
        source=DecisionSource.SLACK,
        timestamp=datetime.now(),
        participants=["Alice"],
        context="Database selection",
        options_discussed=[{"name": "PG"}],
        decision_made="PG",
        rationale="Reliability",
        raw_content="Use PG"
    )

@pytest.mark.asyncio
async def test_generate_adr(writer, mock_llm, sample_decision):
    adr = await writer.generate_adr(sample_decision, adr_number=1)

    assert adr.number == 1
    assert adr.title == "Use PostgreSQL"
    mock_llm.generate_structured.assert_called_once()
