---
description: Guidelines for developing DevMind agents
author: DevMind Team
version: 1.0.0
globs:
  - "src/agents/**/*.py"
---

# Agent Development Guidelines

## Creating New Agents

**MUST** follow this pattern:

```python
from src.agents.base import BaseAgent, AgentContext
from src.core.llm.router import TaskComplexity

class MyNewAgent(BaseAgent):
    """Description of what this agent does."""

    def __init__(self):
        super().__init__(name="my-agent", complexity=TaskComplexity.MODERATE)

    async def execute(self, context: AgentContext, **kwargs) -> dict:
        """Execute the agent's task.

        Args:
            context: Agent execution context
            **kwargs: Agent-specific parameters

        Returns:
            dict with 'success' key and results
        """
        # Implementation
        return {"success": True, "result": data}
```

## Task Complexity Routing

Use appropriate complexity for LLM selection:

| Complexity | LLM Used | Use Case |
|------------|----------|----------|
| `SIMPLE` | Gemini Flash | Quick tasks, formatting |
| `MODERATE` | Gemini Pro | Analysis, generation |
| `COMPLEX` | Claude | Deep reasoning, architecture |

## Agent Registration

1. Create agent in `src/agents/<name>/`
2. Add CLI command in `src/cli/commands/<name>.py`
3. Add API route in `src/api/routes/<name>.py`
4. Register in `src/cli/main.py` and `src/api/routes/__init__.py`
5. Add tests in `tests/agents/<name>/`

## Return Format

**ALWAYS** return structured dict:

```python
return {
    "success": True,  # Required
    "result": data,   # Main output
    "metadata": {},   # Optional metadata
    "errors": []      # Any errors encountered
}
```
