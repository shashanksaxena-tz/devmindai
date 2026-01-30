# DevMind AI

AI-powered developer toolkit with 11+ intelligent agents for code review, security scanning, testing, and documentation generation.

## Quick Start

```bash
# Clone and install
git clone <repository-url>
cd DevMind-AI
pip install -e ".[cli]"

# Set up API key (Gemini is free)
export GOOGLE_API_KEY=your-key

# Run on any project
devmind document /path/to/project -w --all
```

## Setup Options

| Setup | Time | Use Case | Script |
|-------|------|----------|--------|
| **CLI + Gemini** | 2 min | Basic CLI commands | [`setup-cli-gemini.sh`](scripts/setup-cli-gemini.sh) |
| **CLI + Claude** | 2 min | Complex reasoning | [`setup-cli-claude.sh`](scripts/setup-cli-claude.sh) |
| **CLI Full** | 3 min | All AI providers | [`setup-cli-full.sh`](scripts/setup-cli-full.sh) |
| **Docker Stack** | 5 min | API server + infra | [`setup-docker.sh`](scripts/setup-docker.sh) |
| **API Development** | 5 min | Full development | [`setup-api.sh`](scripts/setup-api.sh) |

Run any script to get started:
```bash
./scripts/setup-cli-gemini.sh           # Instructions mode
./scripts/setup-cli-gemini.sh --interactive  # Prompts for keys
```

## Available Agents

| Agent | Command | Description |
|-------|---------|-------------|
| Code Reviewer | `devmind review` | AI code review for quality, security, performance |
| Security Scanner | `devmind scan` | OWASP Top 10, secrets detection, dependency scan |
| Test Generator | `devmind test` | Generate unit tests with edge cases |
| Project Documenter | `devmind document` | Generate AI-ready docs for 10+ formats |
| PR Generator | `devmind generate-pr` | Clone repo, generate docs, create PR |
| PR Reviewer | `devmind pr-review` | Review GitHub pull requests |

## Common Commands

```bash
# Generate AI documentation for any project
devmind document /path/to/project -w --all

# Security scan
devmind scan . --fail-on high

# Code review
devmind review src/

# Generate tests
devmind test src/utils.py --framework pytest

# Create PR with documentation
devmind generate-pr owner/repo
```

## Documentation

- **[Full Documentation Index](docs/INDEX.md)** - Complete navigation hub
- **[Quick Start Guide](docs/getting-started/QUICK_START.md)** - 2-minute setup
- **[CLI Commands](docs/cli/COMMANDS.md)** - All commands with examples
- **[Feature Matrix](docs/features/FEATURE_MATRIX.md)** - What each component enables

### By Topic

| Topic | Documentation |
|-------|--------------|
| Getting Started | [Setup Overview](docs/getting-started/README.md) |
| AI Integrations | [Gemini](docs/integrations/GEMINI.md), [Claude](docs/integrations/CLAUDE.md), [OpenAI](docs/integrations/OPENAI.md) |
| Infrastructure | [Docker](docs/infrastructure/DOCKER.md), [PostgreSQL](docs/infrastructure/POSTGRESQL.md), [Redis](docs/infrastructure/REDIS.md) |
| CLI Usage | [Commands](docs/cli/COMMANDS.md), [Configuration](docs/cli/CONFIGURATION.md) |
| API Server | [Reference](docs/api/REFERENCE.md), [Examples](docs/api/EXAMPLES.md) |
| Architecture | [System Design](docs/architecture/ARCHITECTURE.md), [LLM Routing](docs/architecture/LLM_ROUTING.md) |

## AI Coding Assistant Support

DevMind generates documentation for 10+ AI coding assistants:

- **Claude Code** - `CLAUDE.md`
- **GitHub Copilot** - `.github/copilot-instructions.md`
- **Cursor** - `.cursor/rules/*.mdc`
- **Gemini CLI** - `.gemini/GEMINI.md`
- **Windsurf** - `.windsurf/rules/*.md`
- **Aider** - `CONVENTIONS.md`
- **Cline** - `.clinerules/*.md`
- **OpenCode** - `AGENTS.md`

See [AI Assistants Integration Guide](docs/cli/AI_ASSISTANTS.md) for details.

## License

MIT
