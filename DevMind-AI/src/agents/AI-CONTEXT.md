# Agent Framework - Base Module Context
**Version**: d9bc9d2908b51be8fc4af9dd38c611fb3888d1df  
**Generated**: 2026-02-03T14:40:18Z

## 🧠 Architectural Mental Model

### Core Responsibility
This module defines the **foundational agent framework** for DevMind AI. It provides abstract base classes and data structures that ALL 10+ agents inherit from, enforcing a consistent execution pattern while abstracting LLM provider complexity.

**Think of it as the "Agent DNA"** - every agent (`VulnScannerAgent`, `CodeReviewerAgent`, etc.) inherits:
1. **Automatic LLM routing** (via `BaseAgent.llm_client`)
2. **Standardized execution flow** (`run()` → `execute()` with error handling)
3. **Unified result format** (`AgentResult[T]`)
4. **Context awareness** (`AgentContext` with repo, commit, user tracking)

### Design Patterns

#### Template Method Pattern
```python
class BaseAgent:
    async def run(self):        # Template (handles errors, logging)
        return await self.execute()  # Hook (subclass implements)
```
**Why**: Separates **execution orchestration** (base class) from **business logic** (subclass)

#### Strategy Pattern (via LLM Router)
- Agents declare `complexity` (SIMPLE/MODERATE/COMPLEX)
- `llm_client` property dynamically returns the optimal provider
- **Decouples** agent logic from "which AI model to use"

#### Result Object Pattern
```python
AgentResult.ok(data={"findings": []}, execution_time=5.2)
AgentResult.fail(error="API timeout", retry_count=3)
```
**Benefits**:
- Type-safe results (`AgentResult[T]` is generic)
- Rich metadata (execution time, token usage, etc.)
- Consistent error handling across all agents

### Data Flow

```
┌─────────────┐
│ CLI/API     │
│ Request     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│ 1. Create AgentContext  │ ◄── Metadata (repo, commit, user)
│    - repository_id      │
│    - commit_sha         │
│    - metadata {...}     │
└──────┬──────────────────┘
       │
       ▼
┌───────────────────────────┐
│ 2. Agent.run(context)     │
│   ├─ Error handling       │
│   └─ Calls execute()      │
└──────┬────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ 3. Agent.execute (OVERRIDE)  │ ◄── Subclass implements this
│    ├─ get llm_client         │
│    ├─ Call generate()        │
│    └─ Return dict result     │
└──────┬───────────────────────┘
       │
       ▼
┌─────────────────────┐
│ 4. llm_client       │ ◄── Auto-routed by complexity
│    ├─ Gemini (SIMPLE)    │
│    ├─ Claude (COMPLEX)   │
│    └─ OpenAI (fallback)  │
└──────┬──────────────┘
       │
       ▼
┌────────────────────┐
│ 5. Return Result   │ ◄── Standardized format
│  {"success": true, │
│   "data": {...},   │
│   "metadata": {}}  │
└────────────────────┘
```

## 🧬 Type Definitions / Models

### `AgentContext`
```python
@dataclass
class AgentContext:
    """Execution context with metadata and state tracking."""
    
    organization_id: str | None = None  # For multi-tenant deployments
    repository_id: str | None = None    # GitHub repo ID
    user_id: str | None = None          # User who triggered
    commit_sha: str | None = None       # Git commit being analyzed
    pr_number: int | None = None        # PR number (if triggered by PR)
    metadata: dict[str, Any] = field(default_factory=dict)  # Flexible payload
    timestamp: datetime  # Auto-set in __post_init__
```

**Key Behaviors**:
- **Immutable after creation** (frozen dataclass in practice)
- **Timestamp auto-added** via `__post_init__` for audit trail
- **Flexible metadata** for agent-specific context (e.g., `{"target_file": "auth.py"}`)

### `AgentResult[T]` (Generic)
```python
@dataclass
class AgentResult(Generic[T]):
    """Type-safe result container."""
    
    success: bool  # Did execution complete successfully?
    data: T | None = None  # Typed payload (e.g., VulnReport, CodeReview)
    error: str | None = None  # Error message if failed
    metadata: dict[str, Any] = field(default_factory=dict)  # Metrics
    
    @classmethod
    def ok(cls, data: T, **metadata) -> AgentResult[T]:
        """Factory for success case."""
        return cls(success=True, data=data, metadata=metadata)
    
    @classmethod
    def fail(cls, error: str, **metadata) -> AgentResult[T]:
        """Factory for failure case."""
        return cls(success=False, error=error, metadata=metadata)
```

**Usage Example**:
```python
# Type-safe result
result: AgentResult[VulnReport] = await agent.run(context)
if result.success:
    report: VulnReport = result.data  # TypeScript-like type narrowing
    print(f"Found {len(report.findings)} vulnerabilities")
else:
    logger.error(result.error)
```

### `BaseAgent` (Abstract)
```python
class BaseAgent(ABC):
    """All agents inherit from this."""
    
    # Subclass MUST override these
    name: str = "base_agent"  
    description: str = "Base agent"
    complexity: TaskComplexity = TaskComplexity.MODERATE
    
    # Automatic routing to correct LLM
    @property
    def llm_client(self) -> BaseLLMClient:
        return self._router.get_client(self.complexity)
    
    # Subclass MUST implement
    @abstractmethod
    async def execute(self, context: AgentContext, **kwargs) -> dict[str, Any]:
        pass
```

## 🔌 Public Interfaces

### `BaseAgent.run(context, **kwargs) -> dict[str, Any]`
- **Purpose**: Public entry point with error handling
- **Flow**:
  1. Calls `execute()` (implemented by subclass)
  2. Catches **all exceptions** and returns structured error
  3. Logs execution metadata (timing, tokens used)
- **Returns**: Always returns a dict (never raises)
- **Example**:
  ```python
  result = await agent.run(AgentContext(commit_sha="abc123"))
  # result = {"success": True, "data": {...}}
  # OR
  # result = {"success": False, "error": "API timeout", "agent": "vuln_scanner"}
  ```

### `BaseAgent.execute(context, **kwargs) -> dict[str, Any]` [ABSTRACT]
- **Purpose**: Agent-specific logic (MUST be overridden)
- **Contract**: Subclass implements the actual work here
- **No Error Handling**: Let exceptions bubble to `run()`
- **Example Override**:
  ```python
  class VulnScannerAgent(BaseAgent):
      async def execute(self, context, file_path):
          code = read_file(file_path)
          findings = await self.generate_structured(
              prompt=f"Find SQL injection in:\n{code}",
              schema=VULN_SCHEMA
          )
          return {"findings": findings}
  ```

### `BaseAgent.llm_client -> BaseLLMClient` (Property)
- **Purpose**: Get the appropriate LLM client for this agent
- **Auto-Routing**: Based on `self.complexity`:
  - `TaskComplexity.SIMPLE` → Gemini (fast)
  - `TaskComplexity.COMPLEX` → Claude (smart)
- **Lazy**: Client instantiated only when first accessed
- **Example**:
  ```python
  class CodeReviewerAgent(BaseAgent):
      complexity = TaskComplexity.COMPLEX  # Prefers Claude
      
      async def execute(self, context):
          # self.llm_client automatically returns Claude
          review = await self.llm_client.generate(...)
  ```

### `BaseAgent.generate(prompt, system_prompt=None, **kwargs) -> str`
- **Purpose**: Convenience wrapper for text generation
- **Delegates** to `self.llm_client.generate()`
- **Use Case**: Unstructured AI responses (e.g., code reviews, explanations)
- **Example**:
  ```python
  explanation = await self.generate(
      "Explain this bug",
      system_prompt="You are a senior developer"
  )
  ```

### `BaseAgent.generate_structured(prompt, schema, **kwargs) -> dict`
- **Purpose**: Get structured JSON responses
- **Schema**: JSON Schema format
- **Use Case**: Vulnerability reports, test cases, metrics
- **Validation**: LLM enforces schema (Anthropic, OpenAI support this)
- **Example**:
  ```python
  schema = {
      "type": "object",
      "properties": {
          "severity": {"type": "string", "enum": ["low", "high"]},
          "cwe_id": {"type": "integer"}
      },
      "required": ["severity"]
  }
  result = await self.generate_structured(prompt, schema)
  # result = {"severity": "high", "cwe_id": 89}
  ```

## 🔗 Dependencies & Linking

### Internal
- **[../core/llm/router.py](../core/llm/router.py)** - `get_llm_router()` for LLM access
- **[../core/llm/base.py](../core/llm/base.py)** - `BaseLLMClient` interface
- **[../core/llm/__init__.py](../core/llm/__init__.py)** - `TaskComplexity` enum

### External
- **Python Standard Library**: `abc`, `dataclasses`, `datetime`, `typing`
- **No third-party dependencies** (keeps base agent lightweight)

### Consumed By (10+ Agents)
All agents in this directory inherit from `BaseAgent`:
- **[vuln_scanner/agent.py](vuln_scanner/agent.py)** - `VulnScannerAgent(BaseAgent)`
- **[code_reviewer/agent.py](code_reviewer/agent.py)** - `CodeReviewerAgent(BaseAgent)`
- **[test_generator/agent.py](test_generator/agent.py)** - `TestGeneratorAgent(BaseAgent)`
- **[doc_generator/agent.py](doc_generator/agent.py)** - `DocGeneratorAgent(BaseAgent)`
- **[debt_analyzer/agent.py](debt_analyzer/agent.py)** - `DebtAnalyzerAgent(BaseAgent)`
- **[code_migrator/agent.py](code_migrator/agent.py)** - `CodeMigratorAgent(BaseAgent)`
- **[query_optimizer/agent.py](query_optimizer/agent.py)** - `QueryOptimizerAgent(BaseAgent)`
- **[incident_responder/agent.py](incident_responder/agent.py)** - `IncidentResponderAgent(BaseAgent)`
- **[pipeline_generator/agent.py](pipeline_generator/agent.py)** - `PipelineGeneratorAgent(BaseAgent)`
- **[adr_recorder/agent.py](adr_recorder/agent.py)** - `ADRRecorderAgent(BaseAgent)`

## 💡 Developer Insights

### Creating a New Agent

**Step-by-Step**:
1. **Create Directory**: `src/agents/my_agent/`
2. **Define Agent Class**:
   ```python
   from src.agents.base import BaseAgent, AgentContext, TaskComplexity
   
   class MyAgent(BaseAgent):
       name = "my_agent"
       description = "Does XYZ"
       complexity = TaskComplexity.MODERATE  # Choose wisely
       
       async def execute(self, context: AgentContext, **kwargs):
           # Your logic here
           result = await self.generate("Your prompt")
           return {"output": result}
   ```
3. **Register in `__init__.py`**:
   ```python
   from src.agents.my_agent.agent import MyAgent
   __all__ = ["MyAgent"]
   ```

### Complexity Selection Guidelines

| Complexity | When to Use | LLM Preference |
|------------|-------------|----------------|
| **SIMPLE** | Pattern matching, formatting, basic checks | Gemini (fast, cheap) |
| **MODERATE** | Code generation, documentation, test cases | Gemini → OpenAI |
| **COMPLEX** | Deep reasoning, security analysis, migrations | Claude → OpenAI |

**Rule of Thumb**: If a human would spend \u003c5 minutes, use SIMPLE. If it needs "thinking", use COMPLEX.

### Error Handling Philosophy

**Do NOT** catch exceptions in `execute()`:
```python
# ❌ BAD
async def execute(self, context):
    try:
        return await self.generate("prompt")
    except Exception as e:
        return {"error": str(e)}  # DON'T DO THIS

# ✅ GOOD
async def execute(self, context):
    return await self.generate("prompt")  # Let run() handle errors
```

**Why**: `run()` already wraps `execute()` with error handling. Double-catching leads to nested error objects.

### Metadata Best Practices

**Use `context.metadata` for agent-specific inputs**:
```python
context = AgentContext(
    commit_sha="abc123",
    metadata={
        "target_file": "src/api/auth.py",  # File to analyze
        "severity_threshold": "medium",    # Agent config
    }
)
```

**Use `result.metadata` for execution metrics**:
```python
return {
    "success": True,
    "data": findings,
    "metadata": {
        "execution_time": 5.2,
        "tokens_used": 1500,
        "llm_provider": "claude",
    }
}
```

### Thread Safety

**⚠️ BaseAgent is NOT thread-safe** for the same instance:
- **Safe**: Create new agent instance per request (stateless)
- **Unsafe**: Reuse same agent across concurrent requests (has mutable `_router`)

**Recommendation**: Use dependency injection in FastAPI/Flask to create new instances.
