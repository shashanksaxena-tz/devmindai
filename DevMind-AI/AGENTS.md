# DevMind AI - OpenCode Agent Instructions

This file provides workflow instructions for OpenCode AI assistant.

## Project Context

You are working with **DevMind AI**, an AI-powered developer platform with 10+ intelligent agents for code review, testing, security analysis, and documentation.

## Workflow Rules

### Before Making Changes
1. Read relevant files to understand existing code
2. Check for existing patterns in similar files
3. Verify the change aligns with project architecture

### Code Changes
1. Use type hints for all Python functions
2. Follow existing naming conventions
3. Inherit from `BaseAgent` for new agents
4. Update tests when modifying agent logic

### After Changes
1. Run linting: `poetry run black --check .`
2. Run tests: `poetry run pytest tests/ -x`
3. Verify CLI works: `poetry run devmind --help`

## Available DevMind Agents

Run these via CLI or trigger through code:

### Code Review
```bash
poetry run devmind review <file> --format table
```

### Security Scan
```bash
poetry run devmind scan <path> --fail-on high
```

### Test Generation
```bash
poetry run devmind test <file> --framework pytest
```

### Project Documentation
```bash
poetry run devmind document <path> -w --all
```

## Key Files to Know

| File | Purpose |
|------|---------|
| `src/agents/base.py` | BaseAgent class - all agents inherit from this |
| `src/core/llm/router.py` | LLM routing logic (Gemini vs Claude) |
| `src/cli/main.py` | CLI entry point and command registration |
| `src/api/main.py` | FastAPI application entry point |

## Agent Development Pattern

```python
from src.agents.base import BaseAgent, AgentContext
from src.core.llm.router import TaskComplexity

class NewAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="new-agent", complexity=TaskComplexity.MODERATE)

    async def execute(self, context: AgentContext, **kwargs) -> dict:
        # Your implementation
        return {"success": True, "result": data}
```

## Output Directory

Generated files go to `devmind-output/` organized by agent:
```
devmind-output/
├── project-documenter/
│   └── {project}-{timestamp}/
├── code-reviewer/
└── security-scanner/
```

## Commit Guidelines

- Use descriptive commit messages
- Reference issue numbers if applicable
- Run tests before committing
- Never commit API keys or credentials
