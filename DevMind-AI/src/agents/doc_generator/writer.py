"""Documentation generation using LLM."""
from __future__ import annotations

from typing import Any

from .parser import DocumentableElement, APIEndpoint


class DocWriter:
    """Generates documentation using LLM."""

    def __init__(self, llm_client: Any):
        self.llm_client = llm_client

    async def generate_docstring(
        self,
        element: DocumentableElement,
        style: str = "google",  # google, numpy, sphinx
    ) -> str:
        """Generate docstring for a function/class."""
        prompt = f"""Generate a {style}-style docstring for this {element.element_type}:

```python
{element.signature}
```

Parameters: {element.parameters}
Returns: {element.return_type or 'None'}

Write a clear, concise docstring that:
1. Summarizes what it does (one line)
2. Documents each parameter with type and description
3. Documents the return value
4. Mentions any exceptions raised

Return only the docstring content (no quotes).
"""

        response = await self.llm_client.generate(
            prompt=prompt,
            system="You are a technical writer creating Python docstrings.",
        )

        return response.get("docstring", response) if isinstance(response, dict) else response

    async def generate_readme(
        self,
        project_info: dict,
        elements: list[DocumentableElement],
    ) -> str:
        """Generate README.md content."""
        element_names = [e.name for e in elements[:10]]
        prompt = f"""Generate a README.md for this project:

Project: {project_info.get('name', 'Project')}
Description: {project_info.get('description', '')}

Main modules/functions:
{element_names}

Include:
1. Project title and description
2. Installation instructions
3. Quick start example
4. Key features
5. API overview (if applicable)
6. Contributing section
7. License

Return markdown content.
"""

        return await self.llm_client.generate(
            prompt=prompt,
            system="You are a technical writer creating README documentation.",
        )

    async def generate_api_docs(
        self,
        endpoints: list[APIEndpoint],
    ) -> str:
        """Generate API documentation."""
        docs = ["# API Documentation\n"]

        for endpoint in endpoints:
            doc = f"""
## {endpoint.method} {endpoint.path}

{endpoint.description or 'No description'}

**Parameters:**
{self._format_params(endpoint.parameters)}

**Response:**
{endpoint.response_model or 'JSON'}
"""
            docs.append(doc)

        return "\n".join(docs)

    def _format_params(self, params: list[dict]) -> str:
        if not params:
            return "None"
        return "\n".join([
            f"- `{p['name']}` ({p.get('type', 'any')}): {p.get('description', '')}"
            for p in params
        ])
