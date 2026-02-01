# DevMind CLI

Command-line interface for AI-powered code analysis, documentation, and security scanning.

## Quick Reference

| Command | Purpose |
|---------|---------|
| `devmind document` | Generate AI assistant documentation |
| `devmind scan` | Security vulnerability scanning |
| `devmind review` | AI code review |
| `devmind test` | Generate unit tests |
| `devmind generate-pr` | Create PR with documentation |
| `devmind pr-review` | Review GitHub PR |
| `devmind tools` | List available AI tools |

## Installation

```bash
pip install -e ".[cli]"
devmind --help
```

## Basic Usage

```bash
# Analyze any project
devmind document /path/to/project --analyze

# Generate all AI documentation
devmind document /path/to/project -w --all

# Security scan
devmind scan /path/to/project --fail-on high

# Code review
devmind review /path/to/file.py
```

## Documentation

| Guide | Description |
|-------|-------------|
| [Commands](COMMANDS.md) | All commands with examples |
| [Configuration](CONFIGURATION.md) | `.devmind.yaml` and environment variables |
| [AI Assistants](AI_ASSISTANTS.md) | Using with Claude Code, Gemini CLI, etc. |

## Output Locations

| Flag | Output |
|------|--------|
| `-w, --write` | `devmind-output/` directory |
| `-p, --to-project` | Directly to project root |
| Neither | Terminal output only |

## Common Workflows

### Generate docs for any project

```bash
cd /path/to/project
devmind document . -w --all
```

### Security audit

```bash
devmind scan . --fail-on high --format json > security-report.json
```

### Code review before commit

```bash
devmind review src/ --focus security
```

### Create documentation PR

```bash
devmind generate-pr owner/repo --all
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `GOOGLE_API_KEY` | Gemini (primary) |
| `ANTHROPIC_API_KEY` | Claude (complex tasks) |
| `OPENAI_API_KEY` | OpenAI (fallback) |
| `GITHUB_TOKEN` | GitHub features |

See [Configuration](CONFIGURATION.md) for all options.
