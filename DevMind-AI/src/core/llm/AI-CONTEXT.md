# LLM Client Abstraction Module Context
**Version**: d9bc9d2908b51be8fc4af9dd38c611fb3888d1df  
**Generated**: 2026-02-03T14:40:18Z

## 🧠 Architectural Mental Model

### Core Responsibility
This module implements a **provider-agnostic LLM routing system** that intelligently selects the optimal AI model based on task complexity and provider availability. It abstracts the differences between Claude (Anthropic), Gemini (Google), and OpenAI, providing a unified interface with automatic fallback handling.

The router acts as a **smart dispatcher**, routing:
- **SIMPLE** tasks (style review, basic analysis) → **Gemini** (fast, cost-effective)
- **MODERATE** tasks (documentation, test generation) → **Gemini** or **OpenAI**
- **COMPLEX** tasks (deep code review, migrations, incident response) → **Claude** (superior reasoning)

### Design Patterns
- **Strategy Pattern**: `BaseLLMClient` defines interface; concrete clients (`ClaudeClient`, `GeminiClient`, `OpenAIClient`) implement provider-specific logic
- **Lazy Initialization**: Clients are instantiated only when needed via `@property` decorators, avoiding unnecessary SDK imports/connections
- **Singleton via Caching**: `@lru_cache` on `get_llm_router()` ensures single instance across application
- **Graceful Degradation**: Automatic fallback to available providers when preferred provider is unavailable

### Data Flow
1. **Agent/CLI** requests LLM via `get_llm_router().get_client(TaskComplexity.COMPLEX)`
2. **Router** checks provider availability flags (`_has_claude`, `_has_gemini`, `_has_openai`)
3. **Lazy Loading**: If preferred client not initialized, import and instantiate (e.g., `ClaudeClient()`)
4. **Fallback Logic**: If preferred unavailable, try next best option
5. **Return** concrete `BaseLLMClient` instance
6. **Caller** invokes `generate()` or `generate_structured()` on returned client

## 🧬 Type Definitions / Models

> **Critical Type Definitions**

```python
from enum import Enum
from abc import ABC, abstractmethod
from typing import Any

class TaskComplexity(str, Enum):
    """Maps task types to complexity tiers for routing decisions."""
    SIMPLE = "simple"      # Fast inference, low cost (Gemini preferred)
    MODERATE = "moderate"  # Medium complexity (Gemini/OpenAI)
    COMPLEX = "complex"    # Deep reasoning (Claude preferred)

class BaseLLMClient(ABC):
    """Abstract interface all providers must implement."""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """
        Generate unstructured text response.
        
        Args:
            prompt: User message
            system_prompt: System instructions (e.g., "You are a code reviewer")
            max_tokens: Response length limit
            temperature: 0.0 = deterministic, 1.0 = creative
            **kwargs: Provider-specific options (e.g., top_p, stop_sequences)
        
        Returns:
            Raw text response from LLM
        
        Raises:
            RuntimeError: On API failures (rate limits, invalid keys)
        """
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: dict[str, Any],  # JSON Schema format
        *,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Generate JSON response matching provided schema.
        
        Used for:
        - Vulnerability reports (structured findings)
        - Test generation (structured test cases)
        - Code metrics (numerical data)
        
        Returns:
            Validated dict matching schema
        """
        pass
```

## 🔌 Public Interfaces

### `LLMRouter.get_client(complexity: TaskComplexity) -> BaseLLMClient`
- **Purpose**: Get optimal LLM client for task complexity
- **Routing Logic**:
  - `COMPLEX` → Claude > OpenAI > Gemini
  - `MODERATE` → Gemini > OpenAI > Claude
  - `SIMPLE` → Gemini > OpenAI > Claude
- **Fallback**: Raises `RuntimeError` if NO providers configured
- **Side Effects**: Lazy-instantiates client on first access

### `LLMRouter.get_client_for_agent(agent_type: str) -> BaseLLMClient`
- **Purpose**: Get client based on agent name (convenience wrapper)
- **Mappings**:
  - `code_reviewer` → `TaskComplexity.COMPLEX` (Claude preferred)
  - `vuln_scanner` → `TaskComplexity.SIMPLE` (Gemini preferred)
  - `test_generator` → `TaskComplexity.MODERATE`
- **Default**: Unknown agents map to `MODERATE`

### `get_llm_router() -> LLMRouter`
- **Purpose**: Get singleton router instance
- **Caching**: `@lru_cache` ensures single instance
- **Initialization**: Checks environment for API keys:
  - `ANTHROPIC_API_KEY` → Claude available
  - `GOOGLE_API_KEY` → Gemini available
  - `OPENAI_API_KEY` → OpenAI available
- **Warnings**: Logs warning if NO keys configured

### Factory Functions
```python
def get_claude_client() -> ClaudeClient  # Explicit Claude client
def get_gemini_client() -> GeminiClient  # Explicit Gemini client
def get_openai_client() -> OpenAIClient  # Explicit OpenAI client
```
**Use Case**: Direct provider access when routing logic should be bypassed (e.g., testing specific provider)

## 🔗 Dependencies & Linking

### Internal
- [../config.py](../config.py) - `Settings` for API key access
- `base.py` - `BaseLLMClient` abstract interface
- `claude.py` - Anthropic Claude implementation
- `gemini.py` - Google Gemini implementation
- `openai.py` - OpenAI GPT implementation

### External
- **Lazy Imports**: Provider SDKs (`anthropic`, `google.generativeai`, `openai`) imported only when needed
- **Pydantic Settings**: Environment variable loading
- **Python Logging**: Provider availability warnings

### Consumed By
- [../../agents/base.py](../../agents/base.py) - All agents use `get_llm_router()` for LLM access
- [../../cli/main.py](../../cli/main.py) - CLI commands route through this module
- [../../api/routes/](../../api/routes/) - API endpoints for LLM-powered features

## 📊 Implementation Details

### Lazy Loading Strategy
```python
@property
def claude(self) -> "BaseLLMClient | None":
    if self._claude is None and self._has_claude:
        from src.core.llm.claude import ClaudeClient  # Import deferred
        self._claude = ClaudeClient()
    return self._claude
```
**Why**: 
- Avoids import errors if SDK not installed
- Faster startup (only import what's used)
- Supports graceful degradation

### Cost Optimization
The routing strategy intentionally routes simple tasks to **Gemini** because:
- **60 requests/min** free tier (vs Claude's strict limits)
- **Lower latency** for straightforward tasks
- **Cost-effective** at scale

For complex tasks (code review, migrations), **Claude** is preferred because:
- **Superior reasoning** on multi-step logic
- **Better code understanding** (trained on GitHub)
- **More reliable** structured outputs

### Error Handling
- If **no providers** configured: `RuntimeError` with actionable message
- If **preferred unavailable**: Silent fallback to next best provider with debug log
- If **API call fails**: Propagates provider-specific exceptions (caller handles retries)

## 💡 Developer Insights

### Configuration Best Practices
For CLI usage, **only Gemini** is required:
```bash
export GOOGLE_API_KEY=your_key_here
```

For production API, configure **both Gemini + Claude**:
```bash
export GOOGLE_API_KEY=...
export ANTHROPIC_API_KEY=...
```

### Adding a New Provider
1. Create `src/core/llm/your_provider.py` implementing `BaseLLMClient`
2. Add property to `LLMRouter`: `@property def your_provider(self) -> BaseLLMClient | None`
3. Update routing logic in `get_client()` method
4. Add agent mapping in `get_client_for_agent()`
5. Update `get_available_providers()` to include new provider

### Testing Considerations
- Mock `settings.ANTHROPIC_API_KEY` etc. to test routing logic without real API keys
- Use `LLMRouter.get_available_providers()` to verify provider detection
- Test fallback order by selectively disabling providers
