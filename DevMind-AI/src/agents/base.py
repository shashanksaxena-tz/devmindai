"""Base agent framework for DevMind AI."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from src.core.llm import BaseLLMClient, LLMRouter, TaskComplexity, get_llm_router

T = TypeVar("T")


@dataclass
class AgentContext:
    """Context passed to agents during execution."""

    organization_id: str | None = None
    repository_id: str | None = None
    user_id: str | None = None
    commit_sha: str | None = None
    pr_number: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Add timestamp to context."""
        self.timestamp = datetime.now(timezone.utc)


@dataclass
class AgentResult(Generic[T]):
    """Result returned by agent execution."""

    success: bool
    data: T | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def ok(cls, data: T, **metadata: Any) -> "AgentResult[T]":
        """Create a successful result."""
        return cls(success=True, data=data, metadata=metadata)

    @classmethod
    def fail(cls, error: str, **metadata: Any) -> "AgentResult[T]":
        """Create a failed result."""
        return cls(success=False, error=error, metadata=metadata)


class BaseAgent(ABC):
    """Abstract base class for all DevMind agents."""

    # Override in subclasses
    name: str = "base_agent"
    description: str = "Base agent"
    complexity: TaskComplexity = TaskComplexity.MODERATE

    def __init__(self, router: LLMRouter | None = None):
        """Initialize agent with LLM router.

        Args:
            router: LLM router instance (uses global if not provided)
        """
        self._router = router or get_llm_router()

    @property
    def llm_client(self) -> BaseLLMClient:
        """Get the appropriate LLM client for this agent."""
        return self._router.get_client(self.complexity)

    @abstractmethod
    async def execute(self, context: AgentContext, **kwargs: Any) -> dict[str, Any]:
        """Execute the agent's main logic.

        Args:
            context: Execution context
            **kwargs: Additional arguments

        Returns:
            Result dictionary
        """
        pass

    async def run(self, context: AgentContext, **kwargs: Any) -> dict[str, Any]:
        """Run the agent with error handling and logging.

        Args:
            context: Execution context
            **kwargs: Additional arguments

        Returns:
            Execution result
        """
        try:
            result = await self.execute(context, **kwargs)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent": self.name,
            }

    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate a response using the agent's LLM client.

        Args:
            prompt: The prompt to send
            system_prompt: Optional system prompt
            **kwargs: Additional arguments

        Returns:
            Generated text
        """
        return await self.llm_client.generate(
            prompt,
            system_prompt=system_prompt,
            **kwargs,
        )

    async def generate_structured(
        self,
        prompt: str,
        schema: dict[str, Any],
        *,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a structured response using the agent's LLM client.

        Args:
            prompt: The prompt to send
            schema: JSON schema for the response
            system_prompt: Optional system prompt
            **kwargs: Additional arguments

        Returns:
            Structured response
        """
        return await self.llm_client.generate_structured(
            prompt,
            schema,
            system_prompt=system_prompt,
            **kwargs,
        )
