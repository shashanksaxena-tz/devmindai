"""Google Gemini LLM client."""

import json
from typing import Any

import google.generativeai as genai

from src.core.config import settings
from src.core.llm.base import BaseLLMClient


class GeminiClient(BaseLLMClient):
    """Client for Google Gemini API."""

    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize Gemini client.

        Args:
            model: Gemini model to use
        """
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(model)

    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """Generate a response using Gemini."""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )

        response = await self.model.generate_content_async(
            full_prompt,
            generation_config=generation_config,
        )

        return response.text

    async def generate_structured(
        self,
        prompt: str,
        schema: dict[str, Any],
        *,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a structured response using Gemini."""
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
