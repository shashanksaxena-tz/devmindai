# tests/agents/adr_recorder/test_capture.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from src.agents.adr_recorder.capture import DecisionCaptureAgent, DecisionSource, DecisionPoint

@pytest.fixture
def mock_llm():
    llm = AsyncMock()
    # Mock structured generation
    llm.generate_structured = AsyncMock()
    llm.generate_structured.return_value = {
        "decisions": [
            {
                "context": "Selecting a database",
                "options": [
                    {"name": "PostgreSQL", "pros": ["Reliable"]},
                    {"name": "MongoDB", "pros": ["Flexible"]}
                ],
                "decision": "PostgreSQL",
                "rationale": "We need relational consistency"
            }
        ]
    }
    # Mock fallback generation
    llm.generate.return_value = '{"decisions": []}'
    return llm

@pytest.fixture
def capture_agent(mock_llm):
    return DecisionCaptureAgent(mock_llm)

@pytest.mark.asyncio
async def test_analyze_conversation_with_decisions(capture_agent, mock_llm):
    messages = [
        {"author": "Alice", "content": "What database should we use?"},
        {"author": "Bob", "content": "I think we should go with PostgreSQL."},
        {"author": "Alice", "content": "Agreed, let's decided to use Postgres."}
    ]

    decisions = await capture_agent.analyze_conversation(messages, DecisionSource.SLACK)

    assert len(decisions) == 1
    assert decisions[0].decision_made == "PostgreSQL"
    assert decisions[0].source == DecisionSource.SLACK

    # Verify structured call was used
    mock_llm.generate_structured.assert_called_once()

@pytest.mark.asyncio
async def test_analyze_conversation_fallback(capture_agent, mock_llm):
    # Simulate client without structured generation
    del capture_agent.llm_client.generate_structured
    mock_llm.generate.return_value = '{"decisions": [{"decision": "Fallback"}]}'

    messages = [{"author": "A", "content": "Decision: Fallback"}]
    decisions = await capture_agent.analyze_conversation(messages, DecisionSource.SLACK)

    assert len(decisions) == 1
    assert decisions[0].decision_made == "Fallback"
    mock_llm.generate.assert_called_once()

def test_contains_decision_patterns(capture_agent):
    assert capture_agent._contains_decision_patterns("should we use redis?")
    assert not capture_agent._contains_decision_patterns("Just a regular chat")
