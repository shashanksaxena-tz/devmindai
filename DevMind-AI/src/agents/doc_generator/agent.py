"""DocGenerator agent."""
from __future__ import annotations

from typing import Any

from src.agents.base import BaseAgent, AgentContext
from src.core.llm import TaskComplexity

from .parser import CodeParser
from .writer import DocWriter
from .openapi import OpenAPIGenerator


class DocGeneratorAgent(BaseAgent):
    """Agent that generates documentation from code."""

    name = "doc_generator"
    description = "Generates documentation, docstrings, and API specs"
    complexity = TaskComplexity.SIMPLE

    def __init__(self, llm_client: Any):
        super().__init__(llm_client)
        self.parser = CodeParser()
        self.writer = DocWriter(llm_client)
        self.openapi_gen = OpenAPIGenerator()

    async def execute(
        self,
        context: AgentContext,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate documentation for code."""
        code = kwargs.get("code", "")
        file_path = kwargs.get("file_path", "")
        doc_type = kwargs.get("doc_type", "docstring")  # docstring, readme, api

        if doc_type == "docstring":
            elements = self.parser.parse_module(code, file_path)
            docstrings = {}
            for element in elements:
                # Generate if docstring is missing or if we force regeneration (not implemented yet)
                if not element.existing_docstring:
                    docstring = await self.writer.generate_docstring(element)
                    docstrings[element.name] = docstring
            return {"docstrings": docstrings, "elements_found": len(elements)}

        elif doc_type == "api":
            endpoints = self.parser.parse_api_routes(code)
            api_docs = await self.writer.generate_api_docs(endpoints)
            openapi_spec = self.openapi_gen.generate_spec(endpoints, {})
            return {"api_docs": api_docs, "openapi_spec": openapi_spec}

        elif doc_type == "readme":
            elements = self.parser.parse_module(code, file_path)
            readme = await self.writer.generate_readme(
                {"name": file_path.split("/")[-1] if file_path else "Project"},
                elements,
            )
            return {"readme": readme}

        return {"error": f"Unknown doc_type: {doc_type}"}
