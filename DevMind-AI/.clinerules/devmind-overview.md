---
description: DevMind AI project overview and architecture guide
author: DevMind Team
version: 1.0.0
globs:
  - "**/*.py"
  - "**/*.md"
---

# DevMind AI - Project Overview

You are working with **DevMind AI**, an AI-powered developer platform.

## CRITICAL RULES

- **ALWAYS** use type hints in Python code
- **ALWAYS** inherit from `BaseAgent` when creating agents
- **NEVER** commit API keys or secrets
- **NEVER** modify files in `.env` or credentials

## Project Structure

```
DevMind-AI/
├── src/
│   ├── agents/          # Agent implementations (BaseAgent pattern)
│   ├── api/             # FastAPI routes
│   ├── cli/             # Typer CLI commands
│   ├── core/            # Configuration, LLM routing
│   └── dashboard/       # Streamlit UI
├── tests/               # pytest test suite
└── devmind-output/      # Generated output
```

## Available CLI Commands

| Command | Description |
|---------|-------------|
| `devmind review <file>` | AI code review |
| `devmind scan <path>` | Security scanning |
| `devmind test <file>` | Generate unit tests |
| `devmind document <path>` | Generate AI docs |

## Technology Stack

- Python 3.11+ with type hints
- FastAPI for REST API
- Typer + Rich for CLI
- Streamlit for Dashboard
- Poetry for dependencies
