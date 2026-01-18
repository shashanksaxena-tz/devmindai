"""Claude (Anthropic) LLM client."""

import json
from typing import Any

import anthropic

from src.core.config import settings
from src.core.llm.base import BaseLLMClient


class ClaudeClient(BaseLLMClient):
    """Client for Anthropic Claude API."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        """Initialize Claude client.

        Args:
            model: Claude model to use
        """
        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = model

    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """Generate a response using Claude."""
        messages = [{"role": "user", "content": prompt}]

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "You are a helpful AI assistant.",
            messages=messages,
            **kwargs,
        )

        return response.content[0].text

    async def generate_structured(
        self,
        prompt: str,
        schema: dict[str, Any],
        *,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a structured response using Claude."""
        schema_str = json.dumps(schema, indent=2)
        structured_prompt = f"""{prompt}

Respond with valid JSON matching this schema:
{schema_str}

JSON response:"""

        system = system_prompt or "You are a helpful AI assistant that responds only with valid JSON."

        response = await self.generate(
            structured_prompt,
            system_prompt=system,
            **kwargs,
        )

        # Parse JSON from response
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(response[start:end])
            raise
