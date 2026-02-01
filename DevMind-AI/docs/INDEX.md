# DevMind AI Documentation

Complete documentation for DevMind AI - your AI-powered developer toolkit.

## Quick Navigation

| I want to... | Go to... |
|--------------|----------|
| Get started quickly | [Quick Start](getting-started/QUICK_START.md) |
| Set up the CLI | [CLI Setup](getting-started/CLI_SETUP.md) |
| Deploy full stack | [Full Stack Setup](getting-started/FULL_STACK_SETUP.md) |
| See all commands | [CLI Commands](cli/COMMANDS.md) |
| Understand architecture | [Architecture](architecture/ARCHITECTURE.md) |
| Use with Claude Code | [AI Assistants](cli/AI_ASSISTANTS.md) |

---

## Getting Started

Progressive setup guides from minimal to full deployment.

| Guide | Description | Time |
|-------|-------------|------|
| [Quick Start](getting-started/QUICK_START.md) | Minimal 3-command setup | 2 min |
| [CLI Setup](getting-started/CLI_SETUP.md) | Full CLI installation | 5 min |
| [Full Stack Setup](getting-started/FULL_STACK_SETUP.md) | Docker + all services | 10 min |

### Setup Scripts

| Script | What it does |
|--------|--------------|
| [`setup-cli-gemini.sh`](../scripts/setup-cli-gemini.sh) | CLI + Gemini (free tier) |
| [`setup-cli-claude.sh`](../scripts/setup-cli-claude.sh) | CLI + Claude (complex tasks) |
| [`setup-cli-full.sh`](../scripts/setup-cli-full.sh) | CLI + all AI providers |
| [`setup-docker.sh`](../scripts/setup-docker.sh) | Docker full stack |
| [`setup-api.sh`](../scripts/setup-api.sh) | API development setup |

---

## AI Integrations

Guides for configuring AI providers and GitHub integration.

| Guide | Description |
|-------|-------------|
| [Overview](integrations/README.md) | Integration options summary |
| [Gemini](integrations/GEMINI.md) | Primary provider, free tier available |
| [Claude](integrations/CLAUDE.md) | Complex reasoning tasks |
| [OpenAI](integrations/OPENAI.md) | Optional fallback |
| [GitHub](integrations/GITHUB.md) | PR automation, webhooks |

---

## Infrastructure

Optional infrastructure components for advanced features.

| Guide | What it enables |
|-------|-----------------|
| [Overview](infrastructure/README.md) | Infrastructure summary |
| [Docker](infrastructure/DOCKER.md) | Container deployment |
| [PostgreSQL](infrastructure/POSTGRESQL.md) | Persistence, history, analytics |
| [Redis](infrastructure/REDIS.md) | Caching, background jobs |
| [Qdrant](infrastructure/QDRANT.md) | Semantic search, ADR indexing |

See [Feature Matrix](features/FEATURE_MATRIX.md) for what each component unlocks.

---

## CLI Documentation

Command-line interface usage and configuration.

| Guide | Description |
|-------|-------------|
| [Overview](cli/README.md) | CLI introduction |
| [Commands](cli/COMMANDS.md) | All commands with examples |
| [Configuration](cli/CONFIGURATION.md) | `.devmind.yaml` and env vars |
| [AI Assistants](cli/AI_ASSISTANTS.md) | Using with Claude Code, Gemini CLI, etc. |

---

## API Documentation

REST API for programmatic access.

| Guide | Description |
|-------|-------------|
| [Overview](api/README.md) | API introduction |
| [Reference](api/REFERENCE.md) | Endpoint documentation |
| [Examples](api/EXAMPLES.md) | Usage examples |

---

## Features

| Guide | Description |
|-------|-------------|
| [Feature Matrix](features/FEATURE_MATRIX.md) | What you get with each component |

---

## Architecture

Technical architecture and design documentation.

| Guide | Description |
|-------|-------------|
| [Architecture](architecture/ARCHITECTURE.md) | System overview and components |
| [Agents](architecture/AGENTS.md) | Agent development patterns |
| [LLM Routing](architecture/LLM_ROUTING.md) | How models are selected |

---

## Project State

| Document | Description |
|----------|-------------|
| [Project State](state/PROJECT_STATE.md) | Current implementation status |

---

## Archive

| Document | Description |
|----------|-------------|
| [README v1](archive/README-v1.md) | Original comprehensive README |
