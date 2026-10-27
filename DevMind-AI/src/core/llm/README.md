# LLM Router Module
> Intelligent AI provider selection with automatic fallback and cost optimization

## Overview

The **LLM Router** provides a unified interface to multiple AI providers (Claude, Gemini, OpenAI) with intelligent routing based on task complexity. Think of it as a **smart traffic controller** that sends simple tasks to fast, cheap providers (Gemini) and complex reasoning tasks to powerful models (Claude).

**Why You Need This:**
- **Cost Optimization**: Don't waste expensive Claude credits on simple tasks
- **Resilience**: Automatic fallback if your preferred provider is down
- **Simplicity**: One API, multiple providers

## 🚀 Usage

### Basic Example: Get Client by Complexity

```python
from src.core.llm import get_llm_router, TaskComplexity

# Get router instance (singleton)
router = get_llm_router()

# Simple task (uses Gemini - fast & cheap)
client = router.get_client(TaskComplexity.SIMPLE)
response = await client.generate(
    "Fix this code style issue: missing docstring",
    system_prompt="You are a code style checker"
)

# Complex task (uses Claude - deep reasoning)
client = router.get_client(TaskComplexity.COMPLEX)
review = await client.generate(
    "Perform a security audit of this authentication module",
    system_prompt="You are a senior security engineer"
)
```

### Get Client by Agent Type

```python
# Automatic routing based on agent
client = router.get_client_for_agent("code_reviewer")  # Gets Claude
client = router.get_client_for_agent("vuln_scanner")   # Gets Gemini
```

### Structured Output (JSON)

```python
schema = {
    "type": "object",
    "properties": {
        "severity": {"type": "string", "enum": ["low", "medium", "high"]},
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "line": {"type": "integer"},
                    "description": {"type": "string"}
                }
            }
        }
    }
}

result = await client.generate_structured(
    prompt="Analyze this code for vulnerabilities",
    schema=schema
)
# Returns: {"severity": "high", "issues": [{"line": 42, "description": "SQL injection"}]}
```

### Direct Provider Access

```python
from src.core.llm import get_claude_client, get_gemini_client

# Force specific provider (bypass routing)
claude = get_claude_client()
response = await claude.generate("Your prompt here")
```

## 📚 API Summary

| Function / Method | Description |
|-------------------|-------------|
| `get_llm_router()` | Get singleton router instance |
| `router.get_client(complexity)` | Get optimal client for SIMPLE/MODERATE/COMPLEX task |
| `router.get_client_for_agent(agent_type)` | Get client by agent name (e.g., "code_reviewer") |
| `router.has_any_provider()` | Check if at least one provider is configured |
| `router.get_available_providers()` | List available providers (e.g., `["gemini", "claude"]`) |
| `get_claude_client()` | Direct access to Claude client |
| `get_gemini_client()` | Direct access to Gemini client |
| `get_openai_client()` | Direct access to OpenAI client |

## ⚙️ Configuration

### Environment Variables

```bash
# Gemini (Free Tier: 60 req/min)
export GOOGLE_API_KEY=your_google_api_key

# Claude (For complex tasks)
export ANTHROPIC_API_KEY=your_anthropic_api_key

# OpenAI (Optional)
export OPENAI_API_KEY=your_openai_api_key
```

### Routing Strategy

| Task Complexity | Preferred | Fallback 1 | Fallback 2 |
|----------------|-----------|------------|------------|
| **SIMPLE** | Gemini | OpenAI | Claude |
| **MODERATE** | Gemini | OpenAI | Claude |
| **COMPLEX** | Claude | OpenAI | Gemini |

**Rationale:**
- **Gemini**: Fast, cheap, good for straightforward tasks (free 60 RPM)
- **Claude**: Best reasoning for complex code analysis
- **OpenAI**: Middle ground for most tasks

### Agent-to-Complexity Mapping

| Agent | Complexity | Why? |
|-------|------------|------|
| `code_reviewer` | COMPLEX | Deep analysis, multi-step reasoning |
| `vuln_scanner` | SIMPLE | Pattern matching, quick scans |
| `test_generator` | MODERATE | Understands code structure |
| `doc_generator` | SIMPLE | Straightforward summarization |

## 🏗️ Architecture

```
┌─────────────┐
│ Agent/CLI   │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│  LLMRouter       │  ◄── Singleton (cached)
│  - get_client()  │
└────┬────┬────┬───┘
     │    │    │
     ▼    ▼    ▼
┌────────┐ ┌────────┐ ┌────────┐
│ Claude │ │ Gemini │ │ OpenAI │  ◄── Lazy-loaded
│ Client │ │ Client │ │ Client │
└────────┘ └────────┘ └────────┘
     │         │         │
     │         │         │
     ▼         ▼         ▼
  Anthropic  Google   OpenAI
     API       API      API
```

**Key Design Decisions:**
1. **Lazy Loading**: Provider SDKs only imported when needed
2. **Graceful Degradation**: Falls back to available providers
3. **Single Interface**: All providers implement `BaseLLMClient`

## 🔧 Troubleshooting

### Error: "No LLM providers configured"
**Cause**: No API keys set  
**Fix**: 
```bash
export GOOGLE_API_KEY=your_key
```

### Warning: "Claude not available, using Gemini for complex task"
**Cause**: `ANTHROPIC_API_KEY` not set  
**Impact**: Complex tasks will use Gemini (less accurate)  
**Fix**: Add Claude key or accept fallback behavior

### Rate Limit Exceeded
**Cause**: Free tier limits hit (Gemini: 60 req/min)  
**Fix**: 
- Wait 1 minute
- Add paid tier key
- Add additional provider for automatic fallback

## 💡 Best Practices

### Cost Optimization
```python
# ❌ Wrong: Using Claude for simple task
client = get_claude_client()
await client.generate("Format this JSON")

# ✅ Right: Let router choose
client = router.get_client(TaskComplexity.SIMPLE)  # Gets Gemini
await client.generate("Format this JSON")
```

### Error Handling
```python
try:
    client = router.get_client(TaskComplexity.COMPLEX)
    result = await client.generate(prompt)
except RuntimeError:
    print("No LLM providers configured!")
    # Guide user to set API key
```

### Testing
```python
# Mock settings for testing
from unittest.mock import patch

with patch('src.core.config.settings.GOOGLE_API_KEY', 'fake_key'):
    router = LLMRouter()
    assert router.has_any_provider() is True
```

## 📂 Module Structure

```
llm/
├── __init__.py          # Public API exports
├── base.py              # BaseLLMClient interface
├── router.py            # LLMRouter logic ⭐
├── claude.py            # Claude implementation
├── gemini.py            # Gemini implementation
├── openai.py            # OpenAI implementation
├── AI-CONTEXT.md        # This file's companion (AI docs)
└── README.md            # This file (Human docs)
```

## 🔗 Related Docs

- [Configuration Guide](../config.py) - Environment setup
- [Agent Development](../../agents/base.py) - How agents use LLM router
- [../../agents/base.py](../../agents/base.py) - Base agent implementation
