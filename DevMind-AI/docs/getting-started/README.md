# Getting Started with DevMind AI

Choose your setup path based on your needs.

## Setup Options

| Option | Time | Best For |
|--------|------|----------|
| [Quick Start](QUICK_START.md) | 2 min | Try it out, basic usage |
| [CLI Setup](CLI_SETUP.md) | 5 min | Full CLI with all features |
| [Full Stack Setup](FULL_STACK_SETUP.md) | 10 min | API server, persistence, automation |

## Prerequisites

**Minimum:**
- Python 3.9+
- Git

**For Full Stack:**
- Docker & Docker Compose
- GitHub CLI (`gh`) for PR features

## Quick Decision Guide

**"I just want to try DevMind"**
→ [Quick Start](QUICK_START.md) (2 minutes)

**"I want to use CLI regularly"**
→ [CLI Setup](CLI_SETUP.md) with Gemini (free) or Claude

**"I need API access / persistence / automation"**
→ [Full Stack Setup](FULL_STACK_SETUP.md) with Docker

## Setup Scripts

Run any script to get started:

```bash
# Show instructions (safe, no changes)
./scripts/setup-cli-gemini.sh

# Interactive mode (prompts for API keys)
./scripts/setup-cli-gemini.sh --interactive
```

| Script | What You Get |
|--------|--------------|
| `setup-cli-gemini.sh` | CLI + Gemini (free tier) |
| `setup-cli-claude.sh` | CLI + Gemini + Claude |
| `setup-cli-full.sh` | CLI + all AI providers + GitHub |
| `setup-docker.sh` | Full Docker stack |
| `setup-api.sh` | API development setup |

## What's Next?

After setup:
1. Run `devmind --help` to see available commands
2. Try `devmind document . --analyze` on any project
3. See [CLI Commands](../cli/COMMANDS.md) for all options
4. Check [Feature Matrix](../features/FEATURE_MATRIX.md) for what each component enables
