"""LLM router for selecting appropriate model based on task complexity."""

from enum import Enum
from functools import lru_cache

from src.core.llm.base import BaseLLMClient
from src.core.llm.claude import ClaudeClient
from src.core.llm.gemini import GeminiClient


class TaskComplexity(str, Enum):
    """Task complexity levels for routing decisions."""

    SIMPLE = "simple"  # Fast, straightforward tasks
    MODERATE = "moderate"  # Medium complexity
    COMPLEX = "complex"  # Complex reasoning, code review, migrations


class LLMRouter:
    """Routes requests to appropriate LLM based on task requirements."""

    def __init__(self):
        """Initialize router with client instances."""
        self._claude: ClaudeClient | None = None
        self._gemini: GeminiClient | None = None

    @property
    def claude(self) -> ClaudeClient:
        """Lazy-loaded Claude client."""
        if self._claude is None:
            self._claude = ClaudeClient()
        return self._claude

    @property
    def gemini(self) -> GeminiClient:
        """Lazy-loaded Gemini client."""
        if self._gemini is None:
            self._gemini = GeminiClient()
        return self._gemini

    def get_client(self, complexity: TaskComplexity) -> BaseLLMClient:
        """Get appropriate LLM client for task complexity.

        Args:
            complexity: Task complexity level

        Returns:
            LLM client appropriate for the task
        """
        if complexity == TaskComplexity.COMPLEX:
            return self.claude
        elif complexity == TaskComplexity.MODERATE:
            # Use Claude for moderate tasks too (better quality)
            return self.claude
        else:
            # Use Gemini for simple/fast tasks
            return self.gemini

    def get_client_for_agent(self, agent_type: str) -> BaseLLMClient:
        """Get appropriate LLM client for a specific agent type.

        Args:
            agent_type: Type of agent (e.g., 'vuln_scanner', 'code_reviewer')

        Returns:
            LLM client appropriate for the agent
        """
        # Map agent types to complexity
        agent_complexity = {
            # Complex tasks - use Claude
            "code_reviewer": TaskComplexity.COMPLEX,
            "code_migrator": TaskComplexity.COMPLEX,
            "incident_responder": TaskComplexity.COMPLEX,
            "query_optimizer": TaskComplexity.COMPLEX,
            "adr_recorder": TaskComplexity.COMPLEX,
            # Simple/fast tasks - use Gemini
            "vuln_scanner": TaskComplexity.SIMPLE,
            "test_generator": TaskComplexity.MODERATE,
            "debt_analyzer": TaskComplexity.SIMPLE,
            "doc_generator": TaskComplexity.SIMPLE,
            "pipeline_generator": TaskComplexity.MODERATE,
        }

        complexity = agent_complexity.get(agent_type, TaskComplexity.MODERATE)
        return self.get_client(complexity)


@lru_cache
def get_llm_router() -> LLMRouter:
    """Get cached LLM router instance."""
    return LLMRouter()
