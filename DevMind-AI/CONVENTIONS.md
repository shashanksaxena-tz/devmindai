# DevMind AI - Coding Conventions for Aider

This file defines coding conventions and project context for Aider AI pair programming.

## Project Overview

DevMind AI is an AI-powered developer platform with 10+ intelligent agents:
- Code Reviewer Agent
- Security Scanner Agent
- Test Generator Agent
- PR Review Agent
- Project Documenter Agent
- Documentation Agent
- Tech Debt Analyzer
- Incident Analyzer
- Migration Agent
- Query Optimizer
- Pipeline Optimizer
- ADR Recorder

## Technology Stack

- **Language**: Python 3.11+
- **CLI Framework**: Typer with Rich
- **API Framework**: FastAPI with Pydantic
- **Dashboard**: Streamlit
- **LLM Integration**: Anthropic Claude, Google Gemini
- **Package Manager**: Poetry

## Code Style Guidelines

### Python Style
- Use type hints for all function parameters and return values
- Follow PEP 8 naming conventions
- Use Black for formatting (line length 88)
- Use isort for import sorting

### Agent Pattern
All agents must:
1. Inherit from `BaseAgent` class in `src/agents/base.py`
2. Implement the `execute(context: AgentContext, **kwargs)` method
3. Use `TaskComplexity` enum for LLM routing
4. Return structured dict results

```python
from src.agents.base import BaseAgent, AgentContext

class MyAgent(BaseAgent):
    async def execute(self, context: AgentContext, **kwargs) -> dict:
        # Implementation
        return {"success": True, "result": data}
```

### CLI Commands
CLI commands use Typer:
```python
import typer
from src.cli.output.formatters import OutputFormatter

def my_command(
    path: Path = typer.Argument(..., help="Path to process"),
    format: str = typer.Option("table", help="Output format"),
):
    """Command description."""
    # Implementation
```

### API Routes
API routes use FastAPI:
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

## Running DevMind Agents

### Via CLI
```bash
# Code review
devmind review src/file.py

# Security scan
devmind scan . --fail-on high

# Generate tests
devmind test src/file.py

# Document project
devmind document /path/to/project -w --all
```

### Via API
```bash
# Start server
uvicorn src.api.main:app --reload

# Make requests
curl -X POST http://localhost:8000/api/v1/reviews/code -d '{"code": "..."}'
```

## Directory Structure

```
src/
├── agents/           # Agent implementations
│   ├── base.py       # BaseAgent class
│   ├── code_review/  # Code Reviewer
│   ├── security/     # Security Scanner
│   └── project_documenter/  # Project Documenter
├── api/              # FastAPI routes
├── cli/              # Typer commands
├── core/             # Config, LLM routing
└── dashboard/        # Streamlit UI
```

## Important Notes

- Never commit API keys or secrets
- Run tests with `pytest tests/`
- Use `poetry run` prefix for commands
- Output goes to `devmind-output/` directory
