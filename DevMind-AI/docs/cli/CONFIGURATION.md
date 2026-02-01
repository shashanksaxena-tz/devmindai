# CLI Configuration

Configure DevMind behavior through environment variables and configuration files.

## Configuration Priority

DevMind reads configuration in this order (later overrides earlier):

1. Default values
2. `.devmind.yaml` in current directory
3. `.devmind.yaml` in home directory
4. Environment variables
5. Command-line flags

## Environment Variables

### Required (at least one LLM)

```bash
# Gemini (recommended - free tier)
GOOGLE_API_KEY=your-gemini-api-key

# Claude (for complex tasks)
ANTHROPIC_API_KEY=sk-ant-your-key

# OpenAI (fallback)
OPENAI_API_KEY=sk-your-key
```

### Optional

```bash
# GitHub integration
GITHUB_TOKEN=ghp_your-token

# Application settings
APP_ENV=development
DEBUG=true
SECRET_KEY=your-secret-key

# Infrastructure (for API server)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/devmind
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333
```

## .env File

Create `.env` in the DevMind-AI directory:

```bash
# .env
GOOGLE_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
DEBUG=false
```

DevMind automatically loads this file.

## .devmind.yaml

Create `.devmind.yaml` for persistent configuration.

### Location

- **Project-level**: `.devmind.yaml` in current directory
- **User-level**: `~/.devmind.yaml` in home directory

### Full Example

```yaml
# .devmind.yaml

# LLM configuration
llm:
  default_provider: gemini
  gemini:
    model: gemini-3-flash-preview
    temperature: 0.1
    max_tokens: 4096
  claude:
    model: claude-sonnet-4-20250514
    temperature: 0.1
    max_tokens: 4096
  openai:
    model: gpt-4o-mini
    temperature: 0.1
    max_tokens: 4096

# Documentation generation
document:
  formats:
    - claude
    - copilot
    - gemini
  output_dir: devmind-output
  include_human: false
  include_speckit: false

# Security scanning
scan:
  fail_on: high  # critical, high, medium, low
  include_dev_deps: false
  ignore_paths:
    - node_modules
    - venv
    - .git

# Code review
review:
  focus:
    - security
    - performance
  fail_on: blocker  # blocker, warning, suggestion
  max_issues: 100

# Test generation
test:
  framework: pytest  # pytest, unittest, jest
  output_dir: tests

# Caching
cache:
  enabled: true
  llm_ttl: 3600  # seconds

# Output
output:
  format: table  # table, json, text
  color: true
  verbose: false
```

### Minimal Example

```yaml
# .devmind.yaml
llm:
  default_provider: gemini

document:
  formats:
    - claude
    - copilot

scan:
  fail_on: high
```

## Section Reference

### llm

Configure LLM providers.

```yaml
llm:
  default_provider: gemini  # gemini, claude, openai
  gemini:
    model: gemini-3-flash-preview
    temperature: 0.1
    max_tokens: 4096
```

| Key | Description | Default |
|-----|-------------|---------|
| `default_provider` | Primary LLM | gemini |
| `temperature` | Response randomness (0-1) | 0.1 |
| `max_tokens` | Max response length | 4096 |

### document

Configure documentation generation.

```yaml
document:
  formats:
    - claude
    - copilot
    - gemini
  output_dir: devmind-output
  include_human: false
```

| Key | Description | Default |
|-----|-------------|---------|
| `formats` | Default formats to generate | [claude] |
| `output_dir` | Output directory | devmind-output |
| `include_human` | Include human-readable docs | false |
| `include_speckit` | Include GitHub Spec Kit | false |

### scan

Configure security scanning.

```yaml
scan:
  fail_on: high
  include_dev_deps: false
  ignore_paths:
    - node_modules
```

| Key | Description | Default |
|-----|-------------|---------|
| `fail_on` | Exit non-zero threshold | none |
| `include_dev_deps` | Scan dev dependencies | false |
| `ignore_paths` | Paths to skip | [] |

### review

Configure code review.

```yaml
review:
  focus:
    - security
    - performance
  fail_on: blocker
```

| Key | Description | Default |
|-----|-------------|---------|
| `focus` | Review areas | all |
| `fail_on` | Exit non-zero threshold | none |
| `max_issues` | Max issues to report | 100 |

### test

Configure test generation.

```yaml
test:
  framework: pytest
  output_dir: tests
```

| Key | Description | Default |
|-----|-------------|---------|
| `framework` | Test framework | pytest |
| `output_dir` | Output directory | tests |

### cache

Configure caching.

```yaml
cache:
  enabled: true
  llm_ttl: 3600
```

| Key | Description | Default |
|-----|-------------|---------|
| `enabled` | Enable caching | true |
| `llm_ttl` | Cache TTL in seconds | 3600 |

### output

Configure output formatting.

```yaml
output:
  format: table
  color: true
  verbose: false
```

| Key | Description | Default |
|-----|-------------|---------|
| `format` | Default output format | table |
| `color` | Use colored output | true |
| `verbose` | Verbose logging | false |

## Command-Line Overrides

Flags override config file settings:

```bash
# Override fail_on from config
devmind scan . --fail-on critical

# Override output format
devmind review src/ --format json

# Override verbosity
devmind document . -v
```

## Per-Project Configuration

Put `.devmind.yaml` in your project root for project-specific settings:

```
my-project/
├── .devmind.yaml    # Project config
├── src/
└── tests/
```

This is useful for:
- Project-specific review focus areas
- Custom output directories
- CI/CD threshold configuration

## CI/CD Configuration

For CI/CD, use environment variables:

```yaml
# GitHub Actions
env:
  GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}

steps:
  - run: devmind scan . --fail-on high
  - run: devmind review src/ --fail-on blocker
```

Or create a CI-specific config:

```yaml
# .devmind.ci.yaml
scan:
  fail_on: high

review:
  fail_on: blocker
  focus:
    - security
```

```bash
# Use CI config
DEVMIND_CONFIG=.devmind.ci.yaml devmind scan .
```
