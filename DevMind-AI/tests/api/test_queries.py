"""Tests for Query Optimizer API routes."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from src.api.main import app
from src.core.auth import get_current_user

# Mock authentication
async def mock_get_current_user():
    user = MagicMock()
    user.id = "user123"
    return user

app.dependency_overrides[get_current_user] = mock_get_current_user

client = TestClient(app)

@pytest.fixture
def mock_agent_run():
    with patch("src.api.routes.queries.QueryOptimizerAgent") as MockAgent:
        instance = MockAgent.return_value
        instance.run = AsyncMock()
        yield instance.run

def test_analyze_query_success(mock_agent_run):
    mock_agent_run.return_value = {
        "original_query": "SELECT * FROM users",
        "query_type": "select",
        "tables": ["users"],
        "issues": [],
        "suggestions": []
    }

    response = client.post(
        "/api/v1/queries/analyze",
        json={
            "sql": "SELECT * FROM users",
            "repository_id": "repo123"
        }
    )

    assert response.status_code == 200
    assert response.json()["query_type"] == "select"
    mock_agent_run.assert_called_once()

def test_analyze_query_missing_sql():
    response = client.post(
        "/api/v1/queries/analyze",
        json={
            "repository_id": "repo123"
        }
    )

    assert response.status_code == 400
    assert "SQL query is required" in response.json()["detail"]

def test_analyze_query_agent_error(mock_agent_run):
    mock_agent_run.return_value = {
        "success": False,
        "error": "Optimization failed"
    }

    response = client.post(
        "/api/v1/queries/analyze",
        json={
            "sql": "SELECT * FROM users"
        }
    )

    assert response.status_code == 500
    assert "Optimization failed" in response.json()["detail"]
