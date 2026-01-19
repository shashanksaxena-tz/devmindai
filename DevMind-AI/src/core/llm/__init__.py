"""LLM client abstraction layer."""

from src.core.llm.base import BaseLLMClient
from src.core.llm.claude import ClaudeClient
from src.core.llm.gemini import GeminiClient
from src.core.llm.router import LLMRouter, TaskComplexity, get_llm_router


def get_claude_client():
    return ClaudeClient()


def get_gemini_client():
    return GeminiClient()


__all__ = [
    "BaseLLMClient",
    "ClaudeClient",
    "GeminiClient",
    "LLMRouter",
    "TaskComplexity",
    "get_llm_router",
    "get_claude_client",
    "get_gemini_client",
]
