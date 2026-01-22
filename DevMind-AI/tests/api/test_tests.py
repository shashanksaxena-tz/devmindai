"""Tests for test generation API."""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from src.api.main import app
from src.core.auth import get_current_user

# Mock auth
async def mock_get_current_user():
    return {"id": "test-user-id", "email": "test@example.com"}

app.dependency_overrides[get_current_user] = mock_get_current_user

client = TestClient(app)

@pytest.fixture
def mock_agent():
    with patch("src.api.routes.tests.TestGeneratorAgent") as mock:
        agent_instance = AsyncMock()
        mock.return_value = agent_instance
        yield agent_instance

def test_generate_tests_endpoint(mock_agent):
    """Test generating tests endpoint."""
    mock_agent.execute.return_value = {
        "tests": [{"name": "test_func", "code": "pass"}],
        "test_file_content": "def test_func(): pass",
        "test_file_path": "tests/test_file.py",
        "functions_analyzed": 1,
        "tests_generated": 1,
    }

    response = client.post(
        "/api/v1/tests/generate",
        json={
            "code": "def func(): pass",
            "file_path": "src/file.py",
            "framework": "pytest",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["tests"]) == 1
    assert data["test_file_path"] == "tests/test_file.py"

def test_generate_function_tests(mock_agent):
    """Test generating function tests endpoint."""
    mock_agent.generate_for_function.return_value = {
        "tests": [{"name": "test_func", "code": "pass"}],
        "function_name": "func",
    }

    response = client.post(
        "/api/v1/tests/generate-function",
        json={
            "function_code": "def func(): pass",
            "function_name": "func",
        },
    )

    assert response.status_code == 200
    assert len(response.json()["tests"]) == 1
