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
            # Ensure path starts with /
            path_str = endpoint.path if endpoint.path.startswith("/") else f"/{endpoint.path}"

            path = spec["paths"].setdefault(path_str, {})
            method = endpoint.method.lower()

            operation = {
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

            if endpoint.response_model:
                # Add response schema reference if available (simplified)
                operation["responses"]["200"]["content"] = {
                    "application/json": {
                        "schema": {"type": "object", "title": endpoint.response_model}
                    }
                }

            if endpoint.request_body:
                operation["requestBody"] = {
                    "content": {
                        "application/json": {
                            "schema": endpoint.request_body,
                        }
                    }
                }

            path[method] = operation

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
