"""Tests for DocWriter."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.agents.doc_generator.writer import DocWriter
from src.agents.doc_generator.parser import DocumentableElement, APIEndpoint

class TestDocWriter:

    @pytest.fixture
    def mock_llm(self):
        llm = MagicMock()
        llm.generate = AsyncMock()
        return llm

    @pytest.fixture
    def writer(self, mock_llm):
        return DocWriter(mock_llm)

    @pytest.mark.asyncio
    async def test_generate_docstring(self, writer, mock_llm):
        mock_llm.generate.return_value = '"""Generated docstring."""'

        element = DocumentableElement(
            name="test_func",
            element_type="function",
            signature="def test_func(a: int):",
            parameters=[{"name": "a", "type": "int"}]
        )

        docstring = await writer.generate_docstring(element)
        assert docstring == '"""Generated docstring."""'
        mock_llm.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_readme(self, writer, mock_llm):
        mock_llm.generate.return_value = "# Project Title"

        elements = [
            DocumentableElement(name="main", element_type="function", signature="def main():")
        ]

        readme = await writer.generate_readme(
            {"name": "MyProject", "description": "Test"},
            elements
        )
        assert readme == "# Project Title"
        mock_llm.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_api_docs(self, writer):
        # API docs generation doesn't use LLM in current implementation
        endpoints = [
            APIEndpoint(
                method="GET",
                path="/users",
                function_name="get_users",
                description="Get users",
                parameters=[{"name": "limit", "type": "int"}]
            )
        ]

        docs = await writer.generate_api_docs(endpoints)
        assert "## GET /users" in docs
        assert "Get users" in docs
        assert "- `limit` (int): " in docs
