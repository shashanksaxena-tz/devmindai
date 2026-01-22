"""Tests for QueryOptimizerAgent."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.agents.query_optimizer.agent import QueryOptimizerAgent
from src.agents.base import AgentContext
from src.core.llm import TaskComplexity

@pytest.mark.asyncio
async def test_execute_with_explain():
    mock_llm = MagicMock()
    mock_llm.generate = AsyncMock(return_value="CREATE INDEX idx_users_active ON users(active);")

    mock_router = MagicMock()
    mock_router.get_client.return_value = mock_llm

    agent = QueryOptimizerAgent(mock_router)

    context = AgentContext(
        repository_id=str(uuid4()),
        metadata={"task": "optimize_query"}
    )

    sql = "SELECT * FROM users WHERE active = true"
    explain = {
        "Plan": {
            "Node Type": "Seq Scan",
            "Relation Name": "users",
            "Plan Rows": 5000,
            "Total Cost": 100.0,
            "Actual Rows": 5000,
            "Actual Total Time": 50.0
        }
    }

    result = await agent.execute(context, sql=sql, explain=explain)

    assert result["query_type"] == "select"
    assert "users" in result["tables"]
    assert len(result["issues"]) > 0
    assert len(result["suggestions"]) == 1
    assert result["suggestions"][0]["category"] == "index"

@pytest.mark.asyncio
async def test_execute_without_explain():
    mock_llm = MagicMock()
    mock_llm.generate = AsyncMock(return_value="SELECT * FROM users JOIN orders ...")

    mock_router = MagicMock()
    mock_router.get_client.return_value = mock_llm

    agent = QueryOptimizerAgent(mock_router)

    context = AgentContext(
        repository_id=str(uuid4()),
        metadata={"task": "optimize_query"}
    )

    sql = "SELECT * FROM users WHERE id IN (SELECT user_id FROM orders)"

    result = await agent.execute(context, sql=sql)

    assert result["query_type"] == "select"
    assert len(result["suggestions"]) > 0
    assert result["suggestions"][0]["category"] == "rewrite"

@pytest.mark.asyncio
async def test_execute_missing_sql():
    mock_router = MagicMock()

    agent = QueryOptimizerAgent(mock_router)
    context = AgentContext(
        repository_id=str(uuid4()),
        metadata={"task": "optimize_query"}
    )

    result = await agent.execute(context)
    assert "error" in result
