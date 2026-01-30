# GitHub Copilot Instructions for DevMind AI

## Project Overview

DevMind AI is an AI-powered developer platform with 10+ intelligent agents for code review, testing, security analysis, and documentation generation.

## Technology Stack

- **Language**: Python 3.11+
- **CLI Framework**: Typer with Rich formatting
- **API Framework**: FastAPI with Pydantic
- **Dashboard**: Streamlit
- **LLM Integration**: Anthropic Claude, Google Gemini
- **Package Manager**: Poetry

## Code Style Guidelines

### Python Conventions
- Use type hints for ALL function parameters and return values
- Follow PEP 8 naming conventions (snake_case for functions/variables, PascalCase for classes)
- Use Black formatter with line length 88
- Use isort for import ordering

### Agent Development Pattern
All agents MUST inherit from `BaseAgent` and implement the `execute` method:

```python
from src.agents.base import BaseAgent, AgentContext
from src.core.llm.router import TaskComplexity

class MyAgent(BaseAgent):
    name = "my_agent"
    description = "What this agent does"
    complexity = TaskComplexity.MODERATE

    async def execute(self, context: AgentContext, **kwargs) -> dict:
        # Implementation here
        return {"success": True, "result": data}
```

### CLI Command Pattern
CLI commands use Typer with Rich output:

```python
import typer
from src.cli.output.formatters import OutputFormatter

def my_command(
    path: Path = typer.Argument(..., help="Path to process"),
    format: str = typer.Option("table", help="Output format"),
):
    """Command description shown in help."""
    # Implementation
    OutputFormatter.print_success("Done!")
```

### API Route Pattern
API routes use FastAPI with Pydantic models:

```python
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class RequestModel(BaseModel):
    field: str

@router.post("/endpoint")
async def endpoint(request: RequestModel):
    return {"status": "success"}
```

## Available CLI Commands

```bash
devmind review <file>      # AI code review
devmind scan <path>        # Security scanning
devmind test <file>        # Test generation
devmind document <path>    # Generate AI docs
devmind pr-review <url>    # Review GitHub PR
devmind generate-pr <repo> # Generate docs and create PR
devmind run-with <tool>    # Run via AI assistant
devmind tools              # List AI tools
```

## Task Complexity Levels

- `SIMPLE` - Routes to Gemini Flash (quick, simple tasks)
- `MODERATE` - Routes to Gemini Pro (analysis, generation)
- `COMPLEX` - Routes to Claude (deep reasoning, architecture)

## Key Project Files

| File | Purpose |
|------|---------|
| `src/agents/base.py` | BaseAgent class |
| `src/core/llm/router.py` | LLM routing logic |
| `src/cli/main.py` | CLI entry point |
| `src/api/main.py` | API entry point |
| `src/api/routes/__init__.py` | Route registration |

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific agent tests
pytest tests/agents/project_documenter/ -v

# Run with coverage
pytest --cov=src tests/
```

## Important Rules

1. ALWAYS use type hints
2. ALWAYS inherit from BaseAgent for new agents
3. NEVER commit API keys or secrets
4. ALWAYS run tests before committing
5. Use async/await for all agent methods
6. Return structured dicts with "success" key from agents
