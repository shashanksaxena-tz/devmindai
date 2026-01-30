"""LLM client abstraction layer."""

from src.core.llm.base import BaseLLMClient
from src.core.llm.router import LLMRouter, TaskComplexity, get_llm_router


def get_claude_client():
    from src.core.llm.claude import ClaudeClient
    return ClaudeClient()


def get_gemini_client():
    from src.core.llm.gemini import GeminiClient
    return GeminiClient()


def get_openai_client():
    from src.core.llm.openai import OpenAIClient
    return OpenAIClient()


__all__ = [
    "BaseLLMClient",
    "LLMRouter",
    "TaskComplexity",
    "get_llm_router",
    "get_claude_client",
    "get_gemini_client",
    "get_openai_client",
]
