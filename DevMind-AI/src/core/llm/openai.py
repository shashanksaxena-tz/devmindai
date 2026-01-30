"""OpenAI LLM client."""

import json
from typing import Any

import openai

from src.core.config import settings
from src.core.llm.base import BaseLLMClient


class OpenAIClient(BaseLLMClient):
    """Client for OpenAI API."""

    def __init__(self, model: str = "gpt-4o-mini"):
        """Initialize OpenAI client.

        Args:
            model: OpenAI model to use
        """
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
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
        """Generate a response using OpenAI."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({"role": "system", "content": "You are a helpful AI assistant."})

        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=messages,
            **kwargs,
        )

        return response.choices[0].message.content

    async def generate_structured(
        self,
        prompt: str,
        schema: dict[str, Any],
        *,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a structured response using OpenAI."""
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
