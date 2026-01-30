# LLM Routing

DevMind uses intelligent routing to select the appropriate LLM for each task.

## Overview

The LLM Router (`src/core/llm/router.py`) automatically selects the best model based on:
- Task complexity declared by agents
- Provider availability (configured API keys)
- Fallback configuration

## Task Complexity Levels

| Level | Description | Default Provider |
|-------|-------------|------------------|
| `SIMPLE` | Quick, straightforward tasks | Gemini Flash |
| `MODERATE` | Analysis requiring some reasoning | Gemini Pro |
| `COMPLEX` | Deep reasoning, nuanced analysis | Claude |

## How It Works

```python
# Agent declares complexity at initialization
class SecurityReviewer(BaseAgent):
    def __init__(self):
        super().__init__(
            name="security-reviewer",
            complexity=TaskComplexity.COMPLEX  # Routes to Claude
        )

class StyleReviewer(BaseAgent):
    def __init__(self):
        super().__init__(
            name="style-reviewer",
            complexity=TaskComplexity.SIMPLE  # Routes to Gemini
        )
```

## Routing Logic

```
┌─────────────────┐
│  Agent Request  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Check Complexity│
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐ ┌───────┐
│SIMPLE │ │COMPLEX│
└───┬───┘ └───┬───┘
    │         │
    ▼         ▼
┌───────┐ ┌───────┐
│Gemini │ │Claude │
│  OK?  │ │  OK?  │
└───┬───┘ └───┬───┘
    │         │
   Yes       Yes
    │         │
    ▼         ▼
┌───────┐ ┌───────┐
│ Use   │ │ Use   │
│Gemini │ │Claude │
└───────┘ └───────┘
    │         │
   No        No
    │         │
    ▼         ▼
┌─────────────────┐
│   Try Fallback  │
│    (OpenAI)     │
└─────────────────┘
```

## Provider Configuration

### Gemini (Default for Simple/Moderate)

```bash
# Required for SIMPLE and MODERATE tasks
export GOOGLE_API_KEY=your-key
```

Model: `gemini-2.0-flash`
- Fast inference
- Good code understanding
- Free tier (60 RPM)

### Claude (Default for Complex)

```bash
# Required for COMPLEX tasks (optional if Gemini available)
export ANTHROPIC_API_KEY=your-key
```

Model: `claude-sonnet-4-20250514`
- Superior reasoning
- Better security analysis
- More expensive

### OpenAI (Fallback)

```bash
# Optional fallback
export OPENAI_API_KEY=your-key
```

Model: `gpt-4o-mini`
- Reliable fallback
- Good for most tasks

## Task-to-Model Mapping

| Task | Complexity | Model | Reason |
|------|------------|-------|--------|
| Style review | SIMPLE | Gemini | Pattern matching |
| Documentation check | SIMPLE | Gemini | Template following |
| Test generation | MODERATE | Gemini | Structured output |
| Documentation generation | MODERATE | Gemini | Template-based |
| Security review | COMPLEX | Claude | Attack vector reasoning |
| Correctness review | COMPLEX | Claude | Logic analysis |
| Exploitability analysis | COMPLEX | Claude | Threat modeling |
| Review synthesis | COMPLEX | Claude | Multi-source reasoning |

## Fallback Behavior

When the primary model is unavailable:

1. **COMPLEX task, no Claude**
   - Try OpenAI GPT-4
   - Fall back to Gemini Pro
   - Warn about reduced quality

2. **SIMPLE task, no Gemini**
   - Use Claude (more expensive)
   - Use OpenAI

3. **No models available**
   - Raise configuration error

## Router Implementation

```python
# src/core/llm/router.py

class LLMRouter:
    def __init__(self):
        self.clients = {
            "gemini": GeminiClient() if GOOGLE_API_KEY else None,
            "claude": ClaudeClient() if ANTHROPIC_API_KEY else None,
            "openai": OpenAIClient() if OPENAI_API_KEY else None,
        }

    def get_client(self, complexity: TaskComplexity) -> BaseLLMClient:
        # Primary selection
        if complexity == TaskComplexity.COMPLEX:
            primary = self.clients.get("claude")
        else:
            primary = self.clients.get("gemini")

        if primary:
            return primary

        # Fallback chain
        for client in ["openai", "gemini", "claude"]:
            if self.clients.get(client):
                return self.clients[client]

        raise ConfigurationError("No LLM providers configured")
```

## Customizing Routing

### Per-Agent Override

```python
class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="my-agent",
            complexity=TaskComplexity.MODERATE
        )
        # Override to always use Claude
        self.llm = ClaudeClient()
```

### Configuration Override

```yaml
# .devmind.yaml
llm:
  routing:
    simple: gemini
    moderate: gemini
    complex: claude
  override:
    security-reviewer: claude  # Always Claude
    style-reviewer: gemini     # Always Gemini
```

## Cost Optimization

### Use Complexity Appropriately

```python
# Good - declares SIMPLE for simple task
class StyleReviewer(BaseAgent):
    def __init__(self):
        super().__init__(complexity=TaskComplexity.SIMPLE)

# Bad - over-declares complexity
class StyleReviewer(BaseAgent):
    def __init__(self):
        super().__init__(complexity=TaskComplexity.COMPLEX)  # Wastes $$$
```

### Configure Both Providers

With both Gemini and Claude:
- Simple tasks use free Gemini tier
- Complex tasks use Claude when needed

With only Claude:
- All tasks use Claude
- Much higher costs

## Monitoring

Track LLM usage with logging:

```python
# Enable in configuration
DEBUG=true
```

Logs show:
- Which model handled each request
- Token usage
- Response time
- Fallback events

## Error Handling

```python
try:
    result = await router.generate(prompt, TaskComplexity.COMPLEX)
except RateLimitError:
    # Automatic retry with backoff
    pass
except ProviderError as e:
    # Fallback to next provider
    pass
except NoProviderError:
    # No providers available
    raise ConfigurationError("Configure at least one LLM provider")
```
