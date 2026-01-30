# AI Integrations

DevMind uses multiple AI providers for different tasks, routing work to the most appropriate model.

## Overview

| Provider | Use Case | Cost |
|----------|----------|------|
| [Gemini](GEMINI.md) | Primary (simple/moderate tasks) | Free tier available |
| [Claude](CLAUDE.md) | Complex reasoning | Pay per token |
| [OpenAI](OPENAI.md) | Optional fallback | Pay per token |
| [GitHub](GITHUB.md) | PR automation | Free (with limits) |

## Quick Setup

Minimum: Set one LLM provider

```bash
# Option 1: Gemini only (free)
export GOOGLE_API_KEY=your-key

# Option 2: Claude only (paid)
export ANTHROPIC_API_KEY=your-key

# Option 3: Both (recommended)
export GOOGLE_API_KEY=your-gemini-key
export ANTHROPIC_API_KEY=your-claude-key
```

## How Routing Works

DevMind automatically routes tasks based on complexity:

| Complexity | Default Provider | Examples |
|------------|------------------|----------|
| SIMPLE | Gemini | Style review, documentation check |
| MODERATE | Gemini/Claude | Test generation, synthesis |
| COMPLEX | Claude | Security analysis, correctness |

If Claude is unavailable, complex tasks fall back to Gemini or OpenAI.

## Recommendation

**For most users:** Start with Gemini (free), add Claude when you need complex analysis.

```bash
# Minimum viable setup
export GOOGLE_API_KEY=your-key

# Better for complex security/correctness review
export GOOGLE_API_KEY=your-gemini-key
export ANTHROPIC_API_KEY=your-claude-key
```

## Provider-Specific Guides

- [Gemini Setup](GEMINI.md) - Free tier, API setup, rate limits
- [Claude Setup](CLAUDE.md) - Complex tasks, cost optimization
- [OpenAI Setup](OPENAI.md) - Fallback configuration
- [GitHub Integration](GITHUB.md) - PR automation, webhooks, bot commands
