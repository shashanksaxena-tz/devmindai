"""Tests for LLM client abstraction."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestLLMRouter:
    """Test suite for LLM router."""

    def test_router_selects_claude_for_complex_tasks(self):
        """Router should select Claude for complex reasoning tasks."""
        from src.core.llm.router import LLMRouter, TaskComplexity

        router = LLMRouter()

        client = router.get_client(TaskComplexity.COMPLEX)
        assert client.__class__.__name__ == "ClaudeClient"

    def test_router_selects_gemini_for_simple_tasks(self):
        """Router should select Gemini for simple/fast tasks."""
        from src.core.llm.router import LLMRouter, TaskComplexity

        router = LLMRouter()

        client = router.get_client(TaskComplexity.SIMPLE)
        assert client.__class__.__name__ == "GeminiClient"


class TestClaudeClient:
    """Test suite for Claude client."""

    @pytest.mark.asyncio
    async def test_claude_client_generates_response(self):
        """Claude client should generate responses."""
        from src.core.llm.claude import ClaudeClient

        with patch("src.core.llm.claude.anthropic.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client

            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="Test response")]
            mock_client.messages.create = AsyncMock(return_value=mock_response)

            client = ClaudeClient()
            response = await client.generate("Test prompt")

            assert response == "Test response"
            mock_client.messages.create.assert_called_once()


class TestGeminiClient:
    """Test suite for Gemini client."""

    @pytest.mark.asyncio
    async def test_gemini_client_generates_response(self):
        """Gemini client should generate responses."""
        from src.core.llm.gemini import GeminiClient

        with patch("src.core.llm.gemini.genai") as mock_genai:
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model

            mock_response = MagicMock()
            mock_response.text = "Test response"
            mock_model.generate_content_async = AsyncMock(return_value=mock_response)

            client = GeminiClient()
            response = await client.generate("Test prompt")

            assert response == "Test response"
