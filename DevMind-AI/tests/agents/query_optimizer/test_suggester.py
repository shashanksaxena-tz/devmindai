"""Tests for OptimizationSuggester."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.agents.query_optimizer.suggester import OptimizationSuggester, Optimization
from src.agents.query_optimizer.parser import ParsedQuery, QueryType
from src.agents.query_optimizer.analyzer import QueryPlan, PlanNode

@pytest.mark.asyncio
async def test_suggest_indexes():
    mock_llm = MagicMock()
    mock_llm.generate = AsyncMock(return_value="CREATE INDEX idx_users_active ON users(active);")

    suggester = OptimizationSuggester(mock_llm)

    query = ParsedQuery(
        original="SELECT * FROM users WHERE active = true",
        query_type=QueryType.SELECT,
        tables=["users"],
        columns=["*"],
        where_conditions=["active = true"],
        joins=[],
        order_by=[],
        group_by=[],
        subqueries=[]
    )

    plan = QueryPlan(
        root=PlanNode("Seq Scan", "users", 5000, 5000, 100.0, 50.0),
        total_cost=100.0,
        execution_time_ms=50.0,
        rows_affected=5000,
        issues=["Sequential scan on users: Consider adding an index"]
    )

    optimizations = await suggester.suggest(query, plan)

    assert len(optimizations) == 1
    assert optimizations[0].category == "index"
    assert "CREATE INDEX" in optimizations[0].sql
    assert optimizations[0].priority == 1
    mock_llm.generate.assert_called_once()

@pytest.mark.asyncio
async def test_suggest_rewrites():
    mock_llm = MagicMock()
    mock_llm.generate = AsyncMock(return_value="SELECT u.name FROM users u JOIN orders o ON u.id = o.user_id")

    suggester = OptimizationSuggester(mock_llm)

    query = ParsedQuery(
        original="SELECT name FROM users WHERE id IN (SELECT user_id FROM orders)",
        query_type=QueryType.SELECT,
        tables=["users"],
        columns=["name"],
        where_conditions=["id IN (...)"],
        joins=[],
        order_by=[],
        group_by=[],
        subqueries=["SELECT user_id FROM orders"]
    )

    plan = QueryPlan(
        root=PlanNode("Seq Scan", "users", 5000, 5000, 100.0, 50.0),
        total_cost=100.0,
        execution_time_ms=50.0,
        rows_affected=5000,
        issues=[] # No issues flagged to trigger index suggestion, but subquery exists
    )

    optimizations = await suggester.suggest(query, plan)

    assert len(optimizations) == 1
    assert optimizations[0].category == "rewrite"
    assert "SELECT u.name" in optimizations[0].sql
    assert optimizations[0].priority == 2
