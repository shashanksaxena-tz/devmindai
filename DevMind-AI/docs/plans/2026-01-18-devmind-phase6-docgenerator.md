# DevMind AI Phase 6: DocGenerator Agent Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an intelligent documentation generator that automatically creates and maintains API documentation, README files, inline docstrings, and architecture diagrams from code.

**Architecture:** Multi-agent documentation pipeline with Parser (code extraction), Analyzer (purpose understanding), Writer (documentation generation), and Example Generator. Uses Gemini for fast documentation and Claude for complex explanations.

**Tech Stack:** FastAPI, tree-sitter, OpenAPI spec generation, Mermaid diagram generation, Gemini API

**Prerequisites:** Phase 1 (Foundation) completed

---

## Task 1: Code Parser and Extractor

**Files:**
- Create: `src/agents/doc_generator/parser.py`
- Create: `src/agents/doc_generator/extractor.py`
- Test: `tests/agents/doc_generator/test_parser.py`

### Implementation Overview

```python
# src/agents/doc_generator/parser.py
"""Code parsing for documentation extraction."""
from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DocumentableElement:
    """An element that can be documented."""
    name: str
    element_type: str  # function, class, method, module
    signature: str
    existing_docstring: Optional[str] = None
    parameters: list[dict] = field(default_factory=list)
    return_type: Optional[str] = None
    decorators: list[str] = field(default_factory=list)
    line_number: int = 0
    source_code: str = ""


@dataclass
class APIEndpoint:
    """An API endpoint to document."""
    method: str  # GET, POST, etc.
    path: str
    function_name: str
    parameters: list[dict] = field(default_factory=list)
    request_body: Optional[dict] = None
    response_model: Optional[str] = None
    description: Optional[str] = None
    tags: list[str] = field(default_factory=list)


class CodeParser:
    """Parses code to extract documentable elements."""

    def parse_module(self, code: str, file_path: str) -> list[DocumentableElement]:
        """Parse a Python module and extract documentable elements."""
        elements = []
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return elements

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                elements.append(self._parse_function(node, code))
            elif isinstance(node, ast.ClassDef):
                elements.append(self._parse_class(node, code))

        return elements

    def parse_api_routes(self, code: str) -> list[APIEndpoint]:
        """Extract API endpoints from FastAPI/Flask code."""
        endpoints = []
        # Pattern matching for @app.get("/path"), @router.post("/path"), etc.
        # Implementation extracts method, path, and function details
        return endpoints

    def _parse_function(self, node: ast.FunctionDef, source: str) -> DocumentableElement:
        """Parse a function definition."""
        params = []
        for arg in node.args.args:
            param = {"name": arg.arg}
            if arg.annotation:
                param["type"] = ast.unparse(arg.annotation)
            params.append(param)

        return DocumentableElement(
            name=node.name,
            element_type="function",
            signature=self._build_signature(node),
            existing_docstring=ast.get_docstring(node),
            parameters=params,
            return_type=ast.unparse(node.returns) if node.returns else None,
            decorators=[ast.unparse(d) for d in node.decorator_list],
            line_number=node.lineno,
        )

    def _parse_class(self, node: ast.ClassDef, source: str) -> DocumentableElement:
        """Parse a class definition."""
        return DocumentableElement(
            name=node.name,
            element_type="class",
            signature=f"class {node.name}",
            existing_docstring=ast.get_docstring(node),
            line_number=node.lineno,
        )

    def _build_signature(self, node: ast.FunctionDef) -> str:
        """Build function signature string."""
        return f"def {node.name}({ast.unparse(node.args)})"
```

---

## Task 2: Documentation Writer

**Files:**
- Create: `src/agents/doc_generator/writer.py`
- Test: `tests/agents/doc_generator/test_writer.py`

### Implementation Overview

```python
# src/agents/doc_generator/writer.py
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
        prompt = f"""Generate a README.md for this project:

Project: {project_info.get('name', 'Project')}
Description: {project_info.get('description', '')}

Main modules/functions:
{[e.name for e in elements[:10]]}

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
```

---

## Task 3: OpenAPI Spec Generator

**Files:**
- Create: `src/agents/doc_generator/openapi.py`
- Test: `tests/agents/doc_generator/test_openapi.py`

### Implementation Overview

```python
# src/agents/doc_generator/openapi.py
"""OpenAPI specification generator."""
from __future__ import annotations

from typing import Any
from .parser import APIEndpoint


class OpenAPIGenerator:
    """Generates OpenAPI 3.0 specifications."""

    def generate_spec(
        self,
        endpoints: list[APIEndpoint],
        info: dict,
    ) -> dict:
        """Generate OpenAPI 3.0 spec."""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": info.get("title", "API"),
                "version": info.get("version", "1.0.0"),
                "description": info.get("description", ""),
            },
            "paths": {},
        }

        for endpoint in endpoints:
            path = spec["paths"].setdefault(endpoint.path, {})
            path[endpoint.method.lower()] = {
                "summary": endpoint.description or endpoint.function_name,
                "operationId": endpoint.function_name,
                "tags": endpoint.tags,
                "parameters": self._build_parameters(endpoint.parameters),
                "responses": {
                    "200": {
                        "description": "Successful response",
                    }
                },
            }

            if endpoint.request_body:
                path[endpoint.method.lower()]["requestBody"] = {
                    "content": {
                        "application/json": {
                            "schema": endpoint.request_body,
                        }
                    }
                }

        return spec

    def _build_parameters(self, params: list[dict]) -> list[dict]:
        """Build OpenAPI parameter objects."""
        return [
            {
                "name": p["name"],
                "in": p.get("in", "query"),
                "required": p.get("required", False),
                "schema": {"type": p.get("type", "string")},
            }
            for p in params
        ]
```

---

## Task 4: DocGenerator Agent and API

**Files:**
- Create: `src/agents/doc_generator/agent.py`
- Create: `src/api/routes/docs.py`
- Test: `tests/agents/doc_generator/test_agent.py`

### Implementation Overview

```python
# src/agents/doc_generator/agent.py
"""DocGenerator agent."""
from __future__ import annotations

from typing import Any

from src.core.agents import BaseAgent, AgentContext, TaskComplexity

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
                {"name": file_path.split("/")[-1]},
                elements,
            )
            return {"readme": readme}

        return {"error": f"Unknown doc_type: {doc_type}"}
```

---

## Summary

Phase 6 (DocGenerator Agent) consists of 4 tasks:

1. **Code Parser & Extractor** - Extract documentable elements and API endpoints
2. **Documentation Writer** - LLM-powered docstring and README generation
3. **OpenAPI Spec Generator** - Generate OpenAPI 3.0 specifications
4. **DocGenerator Agent & API** - Orchestration and REST endpoints

**Estimated Implementation Time:** ~1 week

**Dependencies:** Phase 1 (Foundation)
