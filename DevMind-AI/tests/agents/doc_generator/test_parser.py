"""Tests for CodeParser."""
import pytest
from src.agents.doc_generator.parser import CodeParser, DocumentableElement, APIEndpoint

class TestCodeParser:

    @pytest.fixture
    def parser(self):
        return CodeParser()

    def test_parse_simple_function(self, parser):
        code = """
def add(a: int, b: int) -> int:
    "Adds two numbers."
    return a + b
"""
        elements = parser.parse_module(code)
        assert len(elements) == 1
        func = elements[0]
        assert func.name == "add"
        assert func.element_type == "function"
        assert func.existing_docstring == "Adds two numbers."
        assert len(func.parameters) == 2
        assert func.parameters[0]["name"] == "a"
        assert func.parameters[0]["type"] == "int"
        assert func.return_type == "int"

    def test_parse_class(self, parser):
        code = """
class Calculator:
    "A simple calculator."
    pass
"""
        elements = parser.parse_module(code)
        assert len(elements) == 1
        cls = elements[0]
        assert cls.name == "Calculator"
        assert cls.element_type == "class"
        assert cls.existing_docstring == "A simple calculator."

    def test_parse_api_routes(self, parser):
        code = """
from fastapi import FastAPI
app = FastAPI()

@app.get("/users")
def get_users():
    "Get all users."
    pass

@app.post("/users")
def create_user(name: str):
    pass
"""
        endpoints = parser.parse_api_routes(code)
        assert len(endpoints) == 2

        get_user = next(e for e in endpoints if e.method == "GET")
        assert get_user.path == "/users"
        assert get_user.function_name == "get_users"
        assert get_user.description == "Get all users."

        create_user = next(e for e in endpoints if e.method == "POST")
        assert create_user.path == "/users"
        assert create_user.function_name == "create_user"
        assert len(create_user.parameters) == 1
        assert create_user.parameters[0]["name"] == "name"

    def test_parse_invalid_code(self, parser):
        code = "def invalid_syntax("
        elements = parser.parse_module(code)
        assert elements == []

        endpoints = parser.parse_api_routes(code)
        assert endpoints == []
