"""Base LLM client interface."""

from abc import ABC, abstractmethod
from typing import Any


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """Generate a response from the LLM.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            **kwargs: Additional provider-specific arguments

        Returns:
            Generated text response
        """
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: dict[str, Any],
        *,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a structured response matching a schema.

        Args:
            prompt: The user prompt
            schema: JSON schema for the response
            system_prompt: Optional system prompt
            **kwargs: Additional provider-specific arguments

        Returns:
            Structured response matching the schema
        """
        pass
