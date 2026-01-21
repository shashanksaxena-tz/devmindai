from fastapi.testclient import TestClient
import pytest
from unittest.mock import MagicMock
from src.api.routes.debt import router
from fastapi import FastAPI
from src.core.auth import get_current_user

app = FastAPI()
app.include_router(router)

# Mock auth
app.dependency_overrides[get_current_user] = lambda: {"id": "test-user"}

client = TestClient(app)

def test_analyze_endpoint():
    files = {
        "test.py": "def foo(): pass"
    }
    response = client.post("/analyze", json={"files": files})
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert "grade" in data

def test_analyze_endpoint_no_files():
    # If we send empty files, the agent returns error, but pydantic might validate first?
    # DebtRequest requires files field. Empty dict is valid for Dict[str, str].

    response = client.post("/analyze", json={"files": {}})
    assert response.status_code == 400
    # The agent returns "No files provided for analysis"
    assert "No files provided for analysis" in response.json()["detail"]
