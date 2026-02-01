# CLI Setup

Complete CLI installation with virtual environment and configuration.

## Prerequisites

- Python 3.9+
- Git
- pip or Poetry

## Installation

### Using pip (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd DevMind-AI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install CLI with dependencies
pip install -e ".[cli]"

# Verify installation
devmind --help
```

### Using Poetry

```bash
# Clone repository
git clone <repository-url>
cd DevMind-AI

# Install with Poetry
poetry install --extras cli

# Activate environment
poetry shell

# Verify
devmind --help
```

## Configuration

### Option 1: Environment Variables

```bash
# Required: At least one LLM provider
export GOOGLE_API_KEY=your-gemini-key      # Recommended (free tier)
export ANTHROPIC_API_KEY=your-claude-key   # For complex tasks

# Optional
export OPENAI_API_KEY=your-openai-key      # Fallback
export GITHUB_TOKEN=your-github-token      # For PR features
```

### Option 2: .env File

Create `.env` in the DevMind-AI directory:

```bash
# .env
GOOGLE_API_KEY=your-gemini-key
ANTHROPIC_API_KEY=your-claude-key
```

### Option 3: Project Configuration

Create `.devmind.yaml` in your project:

```yaml
# .devmind.yaml
llm:
  default_provider: gemini

document:
  formats:
    - claude
    - copilot
    - gemini
  output_dir: devmind-output

scan:
  fail_on: high

review:
  focus:
    - security
    - performance
```

See [Configuration Guide](../cli/CONFIGURATION.md) for all options.

## LLM Provider Setup

### Gemini (Recommended - Free)

1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Create API key
3. Set `GOOGLE_API_KEY`

Free tier: 60 requests/minute, sufficient for most CLI usage.

### Claude (Complex Tasks)

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create API key
3. Set `ANTHROPIC_API_KEY`

Claude handles complex analysis (security review, correctness checks).

### OpenAI (Optional Fallback)

1. Go to [platform.openai.com](https://platform.openai.com)
2. Create API key
3. Set `OPENAI_API_KEY`

## Verify Setup

```bash
# Check all commands
devmind --help

# Test with a simple command
devmind document . --analyze

# Run on a real project
devmind document /path/to/project -w
```

## Using on External Projects

DevMind can analyze any project, not just itself:

```bash
# Navigate to your project
cd /path/to/your/project

# Analyze structure
devmind document . --analyze

# Generate AI documentation
devmind document . -w --all

# Or specify path from anywhere
devmind document /path/to/project -w --all
```

## Next Steps

- [CLI Commands](../cli/COMMANDS.md) - All commands with examples
- [AI Assistants](../cli/AI_ASSISTANTS.md) - Using with Claude Code, Gemini CLI
- [Configuration](../cli/CONFIGURATION.md) - Advanced configuration
- [Full Stack Setup](FULL_STACK_SETUP.md) - Add persistence and API server
