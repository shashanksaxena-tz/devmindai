# DevMind AI - Gemini CLI Context

You are working with **DevMind AI**, an AI-powered developer platform with 10+ intelligent agents for code review, testing, security analysis, and documentation.

## Project Overview

- **Stack**: Python 3.11+, FastAPI, Typer CLI, Streamlit Dashboard
- **Architecture**: Agent-based with LLM routing (Gemini for simple tasks, Claude for complex)
- **Location**: `/home/user/devmindai/DevMind-AI`

## Available Agents

Run agents via CLI: `devmind <command> [options]`

| Agent | Command | Description |
|-------|---------|-------------|
| Code Reviewer | `devmind review <file>` | AI-powered code review |
| Security Scanner | `devmind scan <path>` | Vulnerability detection |
| Test Generator | `devmind test <file>` | Generate unit tests |
| PR Reviewer | `devmind pr-review <pr-url>` | Review pull requests |
| Project Documenter | `devmind document <path>` | Generate AI-ready docs |

## Key Commands for Gemini CLI

### Run Code Review
```bash
devmind review src/path/to/file.py --format json
```

### Security Scan
```bash
devmind scan . --fail-on high
```

### Generate Documentation
```bash
devmind document /path/to/project -w --all
```

## Project Structure

```
DevMind-AI/
├── src/
│   ├── agents/          # Agent implementations
│   ├── api/             # FastAPI routes
│   ├── cli/             # Typer CLI commands
│   ├── core/            # Configuration and utilities
│   └── dashboard/       # Streamlit UI
├── tests/               # Test suite
└── devmind-output/      # Generated documentation output
```

## Code Style

- Use type hints for all functions
- Follow PEP 8 and Black formatting
- Agent classes inherit from `BaseAgent` with `execute()` method
- Use `TaskComplexity` enum for LLM routing

## Running the Project

```bash
# Install dependencies
poetry install

# Run CLI
poetry run devmind --help

# Run API server
poetry run uvicorn src.api.main:app --reload

# Run dashboard
poetry run streamlit run src/dashboard/app.py
```

## Important Files

- `src/agents/base.py` - Base agent class
- `src/core/llm/router.py` - LLM routing logic
- `src/cli/main.py` - CLI entry point
- `src/api/main.py` - API entry point

@../CLAUDE.md
