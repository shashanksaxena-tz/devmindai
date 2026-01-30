---
description: How to run DevMind agents via CLI
author: DevMind Team
version: 1.0.0
globs:
  - "src/cli/**/*.py"
---

# Running DevMind Agents

## Quick Reference

Execute agents using the `devmind` CLI:

```bash
# Code Review
poetry run devmind review src/path/to/file.py --format table

# Security Scan
poetry run devmind scan . --fail-on high

# Generate Tests
poetry run devmind test src/path/to/file.py --framework pytest

# PR Review
poetry run devmind pr-review https://github.com/org/repo/pull/123

# Generate Documentation
poetry run devmind document /path/to/project -w --all
```

## Documentation Generator Options

```bash
# Generate to devmind-output/ (organized by format)
devmind document /path/to/project -w

# Generate directly to project directory
devmind document /path/to/project -w -p

# Generate specific formats
devmind document /path/to/project -w -f claude -f gemini -f copilot

# Generate all formats including human docs
devmind document /path/to/project -w --all --include-human

# Include GitHub Spec Kit
devmind document /path/to/project -w --all --include-speckit
```

## Output Location

When using `-w` flag, output goes to:
```
devmind-output/
└── project-documenter/
    └── {project-name}-{timestamp}/
        ├── README.md       # Execution summary
        ├── claude/         # Claude Code docs
        ├── copilot/        # GitHub Copilot docs
        ├── cursor/         # Cursor AI docs
        ├── gemini/         # Gemini docs
        └── windsurf/       # Windsurf docs
```

## Running via API

```bash
# Start the API server
poetry run uvicorn src.api.main:app --reload --port 8000

# Then make requests
curl -X POST http://localhost:8000/api/v1/project-docs/generate \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/project", "formats": ["claude", "gemini"]}'
```
