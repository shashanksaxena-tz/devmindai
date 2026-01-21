"""Tests for DocGeneratorAgent."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.agents.doc_generator.agent import DocGeneratorAgent
from src.agents.base import AgentContext
from src.core.llm import TaskComplexity

class TestDocGeneratorAgent:

    @pytest.fixture
    def mock_llm(self):
        llm = MagicMock()
        llm.generate = AsyncMock()
        return llm

    @pytest.fixture
    def agent(self, mock_llm):
        return DocGeneratorAgent(mock_llm)

    @pytest.mark.asyncio
    async def test_execute_docstring(self, agent, mock_llm):
        code = """
def test_func():
    pass
"""
        mock_llm.generate.return_value = '"""Docstring."""'

        result = await agent.execute(
            AgentContext(repository_id="test"),
            code=code,
            doc_type="docstring"
        )

        assert "docstrings" in result
        assert "test_func" in result["docstrings"]
        assert result["docstrings"]["test_func"] == '"""Docstring."""'

    @pytest.mark.asyncio
    async def test_execute_api(self, agent):
        code = """
from fastapi import FastAPI
app = FastAPI()

@app.get("/users")
def get_users():
    pass
"""
        result = await agent.execute(
            AgentContext(repository_id="test"),
            code=code,
            doc_type="api"
        )

        assert "api_docs" in result
        assert "openapi_spec" in result
        assert "/users" in result["openapi_spec"]["paths"]

    @pytest.mark.asyncio
    async def test_execute_readme(self, agent, mock_llm):
        code = "def main(): pass"
        mock_llm.generate.return_value = "# Readme"

        result = await agent.execute(
            AgentContext(repository_id="test"),
            code=code,
            doc_type="readme",
            file_path="project/main.py"
        )

        assert "readme" in result
        assert result["readme"] == "# Readme"
