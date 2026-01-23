import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.agents.adr_recorder.capture import DecisionCaptureAgent, DecisionSource, DecisionPoint

@pytest.fixture
def mock_llm_client():
    return AsyncMock()

@pytest.mark.asyncio
async def test_analyze_conversation_no_patterns(mock_llm_client):
    agent = DecisionCaptureAgent(mock_llm_client)
    messages = [{"author": "User", "content": "Hello world"}]

    decisions = await agent.analyze_conversation(messages, DecisionSource.MANUAL)

    assert len(decisions) == 0
    mock_llm_client.generate_structured.assert_not_called()

@pytest.mark.asyncio
async def test_analyze_conversation_with_decisions(mock_llm_client):
    agent = DecisionCaptureAgent(mock_llm_client)
    messages = [
        {"author": "User", "content": "We should use Postgres for the database."},
        {"author": "Other", "content": "I agree, let's decided to go with Postgres."}
    ]

    mock_response = {
        "decisions": [
            {
                "context": "Database selection",
                "options": [{"name": "Postgres", "pros": [], "cons": []}],
                "decision": "Use Postgres",
                "rationale": "Reliability"
            }
        ]
    }
    mock_llm_client.generate_structured.return_value = mock_response

    decisions = await agent.analyze_conversation(messages, DecisionSource.SLACK)

    assert len(decisions) == 1
    d = decisions[0]
    assert d.context == "Database selection"
    assert d.decision_made == "Use Postgres"
    assert d.source == DecisionSource.SLACK
    assert "User" in d.participants
    assert "Other" in d.participants
