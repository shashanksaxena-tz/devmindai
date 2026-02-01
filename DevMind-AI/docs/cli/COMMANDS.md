# CLI Commands

Complete reference for all DevMind CLI commands.

## devmind document

Generate AI assistant documentation for any project.

```bash
devmind document <path> [options]
```

### Options

| Option | Description |
|--------|-------------|
| `-w, --write` | Write to `devmind-output/` |
| `-p, --to-project` | Write directly to project |
| `-f, --format <fmt>` | Specific format (can repeat) |
| `--all` | All formats including human docs |
| `--analyze` | Analyze only, no generation |
| `--human` | Include human-readable docs |
| `--speckit` | Include GitHub Spec Kit |

### Formats

| Format | Output Files |
|--------|--------------|
| `claude` | `CLAUDE.md` |
| `copilot` | `.github/copilot-instructions.md` |
| `cursor` | `.cursor/rules/*.mdc` |
| `gemini` | `.gemini/GEMINI.md` |
| `windsurf` | `.windsurf/rules/*.md` |
| `aider` | `CONVENTIONS.md`, `.aider.conf.yml` |
| `cline` | `.clinerules/*.md` |
| `opencode` | `AGENTS.md`, `.opencode.json` |
| `speckit` | `.specify/memory/constitution.md` |
| `human` | `docs/README.md`, `ARCHITECTURE.md` |

### Examples

```bash
# Analyze project structure
devmind document /path/to/project --analyze

# Generate all formats to devmind-output/
devmind document . -w --all

# Generate specific formats directly to project
devmind document . -p -f claude -f copilot -f gemini

# Generate only Claude and Copilot
devmind document . -w -f claude -f copilot
```

---

## devmind scan

Security vulnerability scanning.

```bash
devmind scan <path> [options]
```

### Options

| Option | Description |
|--------|-------------|
| `--fail-on <level>` | Exit non-zero on severity: `critical`, `high`, `medium`, `low` |
| `--format <fmt>` | Output format: `text`, `json` |

### Examples

```bash
# Basic scan
devmind scan .

# Fail CI on high severity
devmind scan . --fail-on high

# JSON output for processing
devmind scan . --format json > security-report.json

# Scan specific directory
devmind scan src/
```

### Output

```
🔍 Scanning for vulnerabilities...

Found 3 vulnerabilities:
  🔴 CRITICAL (1): CVE-2023-12345 in lodash@4.17.15
  🟠 HIGH (2): CVE-2023-67890 in axios@0.21.0

Recommendation: Update lodash to 4.17.21
```

---

## devmind review

AI-powered code review.

```bash
devmind review <path> [options]
```

### Options

| Option | Description |
|--------|-------------|
| `--focus <area>` | Focus: `security`, `performance`, `style`, `correctness`, `testing`, `documentation` |
| `--fail-on <level>` | Exit non-zero on: `blocker`, `warning`, `suggestion` |
| `--format <fmt>` | Output format: `table`, `json` |

### Examples

```bash
# Review single file
devmind review src/auth.py

# Review directory
devmind review src/

# Security-focused review
devmind review src/ --focus security

# Fail CI on blockers
devmind review src/ --fail-on blocker

# JSON output
devmind review src/main.py --format json
```

### Output

```
📝 Code Review: src/auth.py

┌──────────┬──────────┬───────────────────────────────┐
│ Severity │ Line     │ Issue                         │
├──────────┼──────────┼───────────────────────────────┤
│ BLOCKER  │ 45       │ SQL Injection vulnerability   │
│ WARNING  │ 12       │ Unused variable 'temp'        │
│ SUGGEST  │ 78       │ Consider using f-strings      │
└──────────┴──────────┴───────────────────────────────┘

Summary: 1 blocker, 1 warning, 1 suggestion
```

---

## devmind test

Generate unit tests for code.

```bash
devmind test <file> [options]
```

### Options

| Option | Description |
|--------|-------------|
| `--framework <name>` | Test framework: `pytest`, `unittest`, `jest` |
| `--output <path>` | Output file path |

### Examples

```bash
# Generate pytest tests
devmind test src/utils.py --framework pytest

# Specify output location
devmind test src/auth.py --output tests/test_auth.py

# Generate Jest tests for JS
devmind test src/utils.js --framework jest
```

### Output

```python
# tests/test_utils.py
import pytest
from src.utils import calculate_total

def test_calculate_total_positive_numbers():
    assert calculate_total([1, 2, 3]) == 6

def test_calculate_total_empty_list():
    assert calculate_total([]) == 0

def test_calculate_total_negative_numbers():
    assert calculate_total([-1, -2, 3]) == 0
```

---

## devmind generate-pr

Clone a repository, generate documentation, and create a pull request.

```bash
devmind generate-pr <repo> [options]
```

### Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Write access to repository (or fork first)

### Options

| Option | Description |
|--------|-------------|
| `-f, --format <fmt>` | Documentation formats (can repeat) |
| `-b, --branch <name>` | Branch name |
| `-t, --title <title>` | PR title |
| `--all` | All documentation formats |
| `--dry-run` | Preview only, don't create PR |

### Examples

```bash
# Basic usage
devmind generate-pr owner/repo

# All formats
devmind generate-pr owner/repo --all

# Custom branch and title
devmind generate-pr owner/repo \
  --branch docs/ai-assistant \
  --title "Add AI coding assistant documentation"

# Specific formats
devmind generate-pr owner/repo -f claude -f copilot -f gemini

# Preview without creating
devmind generate-pr owner/repo --dry-run
```

### Workflow

1. Clones repository to temp directory
2. Analyzes project structure
3. Generates documentation
4. Creates new branch
5. Commits generated files
6. Pushes and creates PR

---

## devmind pr-review

Review an existing GitHub pull request.

```bash
devmind pr-review <repo>#<pr_number> [options]
```

### Options

| Option | Description |
|--------|-------------|
| `--focus <area>` | Focus area (same as review) |
| `--format <fmt>` | Output format: `text`, `json` |

### Examples

```bash
# Review a PR
devmind pr-review owner/repo#123

# Security-focused review
devmind pr-review owner/repo#123 --focus security

# JSON output
devmind pr-review owner/repo#123 --format json
```

---

## devmind run-with

Execute DevMind agents through other AI coding assistants.

```bash
devmind run-with <tool> <agent> <target> [options]
```

### Supported Tools

- `gemini` - Gemini CLI
- `claude` - Claude Code
- `aider` - Aider
- `opencode` - OpenCode
- `copilot` - GitHub Copilot

### Agents

- `review` - Code review
- `scan` - Security scan
- `test` - Test generation
- `document` - Documentation

### Examples

```bash
# Code review via Gemini CLI
devmind run-with gemini review src/main.py

# Security scan via Aider
devmind run-with aider scan .

# Documentation via Claude
devmind run-with claude document /path/to/project

# Preview command without running
devmind run-with opencode document . --dry-run
```

---

## devmind tools

List available AI coding assistants and their status.

```bash
devmind tools
```

### Output

```
Available AI Coding Assistants:

┌────────────┬──────────┬─────────────────────────────┐
│ Tool       │ Status   │ Path/Command                │
├────────────┼──────────┼─────────────────────────────┤
│ gemini     │ ✓ Found  │ /usr/local/bin/gemini       │
│ claude     │ ✓ Found  │ /usr/local/bin/claude       │
│ aider      │ ✓ Found  │ /usr/local/bin/aider        │
│ opencode   │ ✗ Missing│                             │
│ copilot    │ ✓ Found  │ gh copilot                  │
└────────────┴──────────┴─────────────────────────────┘
```

---

## Global Options

These work with all commands:

| Option | Description |
|--------|-------------|
| `--help` | Show help for command |
| `--version` | Show version |
| `-v, --verbose` | Verbose output |
| `-q, --quiet` | Minimal output |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Configuration error |
| 3 | Scan/review threshold exceeded (with `--fail-on`) |
