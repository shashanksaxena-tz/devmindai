"""Tests for OpenAPIGenerator."""
import pytest
from src.agents.doc_generator.openapi import OpenAPIGenerator
from src.agents.doc_generator.parser import APIEndpoint

class TestOpenAPIGenerator:

    @pytest.fixture
    def generator(self):
        return OpenAPIGenerator()

    def test_generate_spec_basic(self, generator):
        endpoints = [
            APIEndpoint(
                method="GET",
                path="/users",
                function_name="get_users",
                description="Get users"
            )
        ]

        info = {"title": "Test API", "version": "1.0.0"}
        spec = generator.generate_spec(endpoints, info)

        assert spec["openapi"] == "3.0.0"
        assert spec["info"]["title"] == "Test API"
        assert "/users" in spec["paths"]
        assert "get" in spec["paths"]["/users"]
        assert spec["paths"]["/users"]["get"]["summary"] == "Get users"

    def test_generate_spec_with_params(self, generator):
        endpoints = [
            APIEndpoint(
                method="POST",
                path="/users",
                function_name="create_user",
                parameters=[{"name": "name", "type": "str", "required": True}]
            )
        ]

        spec = generator.generate_spec(endpoints, {})

        op = spec["paths"]["/users"]["post"]
        assert len(op["parameters"]) == 1
        assert op["parameters"][0]["name"] == "name"
        assert op["parameters"][0]["required"] is True
