# DevMind AI CLI

The DevMind AI Command Line Interface (`devmind`) provides a unified developer experience for accessing the AI agents directly from your terminal.

## Installation

```bash
pip install -e ".[cli]"
```

## Configuration

Initialize the configuration file:

```bash
devmind config init
```

This creates a `.devmind.yaml` file where you can configure LLM keys and preferences.

## Commands

### Code Review
Review a file or directory for security, performance, and style issues.

```bash
devmind review src/my_file.py
devmind review src/ --severity blocker
```

### Vulnerability Scan
Scan project dependencies for known vulnerabilities.

```bash
devmind scan .
devmind scan --full --format json
```

### Test Generation
Generate unit tests for a source file.

```bash
devmind test src/utils/math.py
devmind test src/api/routes.py --framework pytest --output tests/api/
```

### PR Review
Review a GitHub Pull Request (requires `GITHUB_TOKEN`).

```bash
devmind pr-review owner/repo 42
devmind pr-review my-org/backend 101 --reviewers security,performance
```

## Environment Variables

You can set API keys via environment variables or in `.devmind.yaml`:
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`
- `OPENAI_API_KEY`
- `GITHUB_TOKEN`
