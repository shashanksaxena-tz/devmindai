from .base import BaseLLMClient
from .router import LLMRouter, TaskComplexity, get_llm_router
from .claude import ClaudeClient
from .gemini import GeminiClient

def get_claude_client():
    return ClaudeClient()

def get_gemini_client():
    return GeminiClient()
