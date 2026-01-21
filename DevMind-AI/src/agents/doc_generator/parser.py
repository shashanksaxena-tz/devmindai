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

    def parse_module(self, code: str, file_path: str = "") -> list[DocumentableElement]:
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
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return endpoints

        # Pattern matching for @app.get("/path"), @router.post("/path"), etc.
        # This is a simplified implementation looking for decorators
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        # Check for app.get, router.post, etc.
                        func = decorator.func
                        is_route = False
                        method = "GET"

                        # Case: @app.get or @router.get
                        if isinstance(func, ast.Attribute):
                            if func.attr in ["get", "post", "put", "delete", "patch"]:
                                is_route = True
                                method = func.attr.upper()

                        if is_route:
                            # Extract path
                            path = "/"
                            if decorator.args:
                                if isinstance(decorator.args[0], ast.Constant):
                                    path = decorator.args[0].value

                            endpoints.append(APIEndpoint(
                                method=method,
                                path=path,
                                function_name=node.name,
                                description=ast.get_docstring(node),
                                parameters=self._extract_params(node)
                            ))

        return endpoints

    def _parse_function(self, node: ast.FunctionDef, source: str) -> DocumentableElement:
        """Parse a function definition."""
        params = self._extract_params(node)

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

    def _extract_params(self, node: ast.FunctionDef) -> list[dict]:
        """Extract parameters from function definition."""
        params = []
        for arg in node.args.args:
            # Skip 'self' or 'cls' usually
            if arg.arg in ["self", "cls"]:
                continue

            param = {"name": arg.arg}
            if arg.annotation:
                param["type"] = ast.unparse(arg.annotation)
            params.append(param)
        return params
