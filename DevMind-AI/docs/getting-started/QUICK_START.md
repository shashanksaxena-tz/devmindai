# Quick Start

Get DevMind running in 2 minutes.

## Prerequisites

- Python 3.9+
- A Google API key (free at [aistudio.google.com](https://aistudio.google.com))

## Setup

```bash
# 1. Clone and install
git clone <repository-url>
cd DevMind-AI
pip install -e ".[cli]"

# 2. Set your API key
export GOOGLE_API_KEY=your-key-here

# 3. Verify
devmind --help
```

## Your First Commands

```bash
# Analyze any project
devmind document /path/to/project --analyze

# Generate AI documentation
devmind document /path/to/project -w --all

# Security scan
devmind scan /path/to/project

# Code review
devmind review /path/to/file.py
```

## What You Get

With just Gemini (free):
- All CLI commands work
- All 10 AI documentation formats
- Security scanning
- Code review
- Test generation

## Next Steps

- [CLI Setup](CLI_SETUP.md) - Full installation with virtual environment
- [CLI Commands](../cli/COMMANDS.md) - All available commands
- [Feature Matrix](../features/FEATURE_MATRIX.md) - What each component enables
- [AI Assistants](../cli/AI_ASSISTANTS.md) - Using with Claude Code, Aider, etc.

## Troubleshooting

**"Command not found: devmind"**
```bash
pip install -e ".[cli]"
# Or use: python -m devmind --help
```

**"API key not found"**
```bash
export GOOGLE_API_KEY=your-key
# Or create .env file:
echo "GOOGLE_API_KEY=your-key" >> .env
```
