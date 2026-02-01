# Agent Architecture

DevMind uses a modular agent architecture where each agent handles a specific domain.

## Overview

All agents inherit from `BaseAgent` and share common capabilities:
- LLM access via the router
- Structured output generation
- Error handling
- Async execution

## BaseAgent

```python
# src/agents/base.py

from src.core.llm.router import TaskComplexity

class BaseAgent:
    def __init__(self, name: str, complexity: TaskComplexity):
        self.name = name
        self.complexity = complexity
        self.llm = get_llm_for_complexity(complexity)

    async def execute(self, context: AgentContext, **kwargs) -> dict:
        """Override in subclasses"""
        raise NotImplementedError

    async def generate(self, prompt: str) -> str:
        """Generate free-form text response"""
        return await self.llm.generate(prompt)

    async def generate_structured(self, prompt: str, schema: Type[T]) -> T:
        """Generate structured output matching schema"""
        return await self.llm.generate_structured(prompt, schema)

    async def run(self, context: AgentContext, **kwargs) -> dict:
        """Execute with error handling"""
        try:
            return await self.execute(context, **kwargs)
        except Exception as e:
            return {"error": str(e), "success": False}
```

## Creating a New Agent

### 1. Define the Agent Class

```python
# src/agents/my_agent/agent.py

from src.agents.base import BaseAgent, AgentContext
from src.core.llm.router import TaskComplexity

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="my-agent",
            complexity=TaskComplexity.MODERATE
        )

    async def execute(self, context: AgentContext, **kwargs) -> dict:
        # Your agent logic here
        result = await self.analyze(context.content)
        return {
            "success": True,
            "result": result
        }

    async def analyze(self, content: str) -> dict:
        prompt = f"Analyze this content: {content}"
        return await self.generate_structured(prompt, AnalysisResult)
```

### 2. Register with CLI (Optional)

```python
# src/cli/commands/my_command.py

import typer
from src.agents.my_agent import MyAgent

app = typer.Typer()

@app.command()
def my_command(path: str):
    agent = MyAgent()
    result = asyncio.run(agent.run(context))
    print(result)
```

### 3. Register with API (Optional)

```python
# src/api/routes/my_agent.py

from fastapi import APIRouter
from src.agents.my_agent import MyAgent

router = APIRouter()

@router.post("/analyze")
async def analyze(request: AnalyzeRequest):
    agent = MyAgent()
    return await agent.run(request.to_context())
```

## Task Complexity

Agents declare their task complexity, which determines LLM routing:

| Complexity | LLM | Use Case |
|------------|-----|----------|
| `SIMPLE` | Gemini Flash | Style checks, formatting |
| `MODERATE` | Gemini Pro | Test generation, documentation |
| `COMPLEX` | Claude | Security analysis, complex reasoning |

```python
class MySimpleAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="simple", complexity=TaskComplexity.SIMPLE)

class MyComplexAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="complex", complexity=TaskComplexity.COMPLEX)
```

## Agent Modules

Complex agents use multiple modules for separation of concerns:

```
my_agent/
├── __init__.py
├── agent.py        # Main agent class
├── analyzer.py     # Content analysis
├── generator.py    # Output generation
├── validator.py    # Result validation
└── schemas.py      # Pydantic models
```

### Example: Multi-Module Agent

```python
# agent.py
class ComplexAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="complex", complexity=TaskComplexity.COMPLEX)
        self.analyzer = Analyzer()
        self.generator = Generator()
        self.validator = Validator()

    async def execute(self, context: AgentContext, **kwargs) -> dict:
        # 1. Analyze input
        analysis = await self.analyzer.analyze(context)

        # 2. Generate output
        output = await self.generator.generate(analysis)

        # 3. Validate result
        validation = await self.validator.validate(output)

        return {
            "success": validation.is_valid,
            "result": output,
            "validation": validation
        }
```

## Existing Agents

### Code Reviewer

Multi-reviewer architecture with parallel execution:

```
code_reviewer/
├── orchestrator.py   # Coordinates reviewers
├── synthesizer.py    # Combines results
├── context_gatherer.py
├── diff_parser.py
└── reviewers/
    ├── security.py      # COMPLEX
    ├── performance.py   # COMPLEX
    ├── correctness.py   # COMPLEX
    ├── style.py         # SIMPLE
    ├── testing.py       # MODERATE
    └── documentation.py # SIMPLE
```

### Security Scanner (VulnScanner)

Vulnerability detection with exploitability analysis:

```
vuln_scanner/
├── agent.py
├── parsers/         # Dependency file parsers
├── vuln_db/         # OSV database client
└── analyzer/        # Exploitability analysis
```

### Test Generator

Multi-stage test creation:

```
test_generator/
├── agent.py
├── analyzer.py     # Understand code structure
├── strategist.py   # Plan test approach
├── generator.py    # Generate test code
├── validator.py    # Validate syntax
└── coverage.py     # Find coverage gaps
```

### Project Documenter

AI assistant documentation generation:

```
project_documenter/
├── agent.py
├── analyzer.py     # Project analysis
├── formats/        # Format-specific generators
│   ├── claude.py
│   ├── copilot.py
│   ├── cursor.py
│   └── ...
└── templates/      # Output templates
```

## Agent Context

All agents receive context through `AgentContext`:

```python
class AgentContext:
    content: str           # Primary content to process
    file_path: Optional[str]
    language: Optional[str]
    metadata: dict         # Additional context
```

## Error Handling

Agents should use the `run()` method which wraps `execute()` with error handling:

```python
# Good - errors are caught
result = await agent.run(context)
if not result.get("success"):
    handle_error(result.get("error"))

# Direct execute - you handle errors
try:
    result = await agent.execute(context)
except Exception as e:
    handle_error(e)
```

## Testing Agents

```python
# tests/agents/test_my_agent.py

import pytest
from src.agents.my_agent import MyAgent, AgentContext

@pytest.mark.asyncio
async def test_my_agent_basic():
    agent = MyAgent()
    context = AgentContext(content="test content")

    result = await agent.run(context)

    assert result["success"]
    assert "result" in result

@pytest.mark.asyncio
async def test_my_agent_error_handling():
    agent = MyAgent()
    context = AgentContext(content="")  # Invalid input

    result = await agent.run(context)

    assert not result["success"]
    assert "error" in result
```
