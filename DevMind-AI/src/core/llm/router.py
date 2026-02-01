"""LLM router for selecting appropriate model based on task complexity."""

from enum import Enum
from functools import lru_cache
import logging

from src.core.config import settings
from src.core.llm.base import BaseLLMClient

logger = logging.getLogger(__name__)


class TaskComplexity(str, Enum):
    """Task complexity levels for routing decisions."""

    SIMPLE = "simple"  # Fast, straightforward tasks
    MODERATE = "moderate"  # Medium complexity
    COMPLEX = "complex"  # Complex reasoning, code review, migrations


class LLMRouter:
    """Routes requests to appropriate LLM based on task requirements."""

    def __init__(self):
        """Initialize router with client instances."""
        self._claude: "BaseLLMClient | None" = None
        self._gemini: "BaseLLMClient | None" = None
        self._openai: "BaseLLMClient | None" = None

        # Check which providers are available
        self._has_claude = bool(settings.ANTHROPIC_API_KEY)
        self._has_gemini = bool(settings.GOOGLE_API_KEY)
        self._has_openai = bool(settings.OPENAI_API_KEY)

        if not any([self._has_claude, self._has_gemini, self._has_openai]):
            logger.warning(
                "No LLM API keys configured. Set GOOGLE_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY."
            )

    @property
    def claude(self) -> "BaseLLMClient | None":
        """Lazy-loaded Claude client."""
        if self._claude is None and self._has_claude:
            from src.core.llm.claude import ClaudeClient
            self._claude = ClaudeClient()
        return self._claude

    @property
    def gemini(self) -> "BaseLLMClient | None":
        """Lazy-loaded Gemini client."""
        if self._gemini is None and self._has_gemini:
            from src.core.llm.gemini import GeminiClient
            self._gemini = GeminiClient()
        return self._gemini

    @property
    def openai(self) -> "BaseLLMClient | None":
        """Lazy-loaded OpenAI client."""
        if self._openai is None and self._has_openai:
            from src.core.llm.openai import OpenAIClient
            self._openai = OpenAIClient()
        return self._openai

    def _get_fallback_client(self) -> BaseLLMClient:
        """Get any available client as fallback."""
        # Try in order: OpenAI, Gemini, Claude
        if self.openai:
            return self.openai
        if self.gemini:
            return self.gemini
        if self.claude:
            return self.claude
        raise RuntimeError(
            "No LLM providers configured. "
            "Set at least one of: GOOGLE_API_KEY, ANTHROPIC_API_KEY, OPENAI_API_KEY"
        )

    def get_client(self, complexity: TaskComplexity) -> BaseLLMClient:
        """Get appropriate LLM client for task complexity.

        Args:
            complexity: Task complexity level

        Returns:
            LLM client appropriate for the task
        """
        if complexity == TaskComplexity.COMPLEX:
            # Prefer Claude for complex tasks
            if self.claude:
                return self.claude
            # Fall back to OpenAI GPT-4
            if self.openai:
                logger.debug("Claude not available, using OpenAI for complex task")
                return self.openai
            # Fall back to Gemini
            if self.gemini:
                logger.debug("Claude/OpenAI not available, using Gemini for complex task")
                return self.gemini

        elif complexity == TaskComplexity.MODERATE:
            # Prefer Gemini for moderate tasks
            if self.gemini:
                return self.gemini
            # Fall back to OpenAI
            if self.openai:
                return self.openai
            # Fall back to Claude
            if self.claude:
                return self.claude

        else:  # SIMPLE
            # Prefer Gemini for simple/fast tasks
            if self.gemini:
                return self.gemini
            # Fall back to OpenAI
            if self.openai:
                return self.openai
            # Fall back to Claude
            if self.claude:
                return self.claude

        # No preferred client available, get any fallback
        return self._get_fallback_client()

    def get_client_for_agent(self, agent_type: str) -> BaseLLMClient:
        """Get appropriate LLM client for a specific agent type.

        Args:
            agent_type: Type of agent (e.g., 'vuln_scanner', 'code_reviewer')

        Returns:
            LLM client appropriate for the agent
        """
        # Map agent types to complexity
        agent_complexity = {
            # Complex tasks - prefer Claude
            "code_reviewer": TaskComplexity.COMPLEX,
            "code_migrator": TaskComplexity.COMPLEX,
            "incident_responder": TaskComplexity.COMPLEX,
            "query_optimizer": TaskComplexity.COMPLEX,
            "adr_recorder": TaskComplexity.COMPLEX,
            # Simple/fast tasks - prefer Gemini
            "vuln_scanner": TaskComplexity.SIMPLE,
            "test_generator": TaskComplexity.MODERATE,
            "debt_analyzer": TaskComplexity.SIMPLE,
            "doc_generator": TaskComplexity.SIMPLE,
            "pipeline_generator": TaskComplexity.MODERATE,
        }

        complexity = agent_complexity.get(agent_type, TaskComplexity.MODERATE)
        return self.get_client(complexity)

    def has_any_provider(self) -> bool:
        """Check if any LLM provider is configured."""
        return any([self._has_claude, self._has_gemini, self._has_openai])

    def get_available_providers(self) -> list[str]:
        """Get list of available provider names."""
        providers = []
        if self._has_gemini:
            providers.append("gemini")
        if self._has_claude:
            providers.append("claude")
        if self._has_openai:
            providers.append("openai")
        return providers


@lru_cache
def get_llm_router() -> LLMRouter:
    """Get cached LLM router instance."""
    return LLMRouter()
