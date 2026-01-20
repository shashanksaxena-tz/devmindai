# Phase 13: CLI Wrapper & Developer Experience
**Created:** 2026-01-20
**Status:** Planned

## Overview

This phase adds a command-line interface (CLI) to DevMind-AI, enabling developers to use the agents directly from their terminal without needing to interact with the REST API manually. The CLI will wrap the existing API functionality and provide a streamlined developer experience.

---

## Objectives

1. **Zero-friction usage** - Run agents with simple commands
2. **Works offline-first** - Direct local analysis without requiring server
3. **Pipeline-ready** - Exit codes and JSON output for CI/CD integration
4. **Progressive disclosure** - Simple commands for common tasks, advanced options available

---

## Target User Experience

### Quick Examples

```bash
# Review a file
devmind review src/auth.py

# Scan for vulnerabilities
devmind scan ./my-project

# Generate tests
devmind test src/utils/math.py --output tests/

# Full PR review (requires GitHub token)
devmind pr-review owner/repo 42
```

---

## Deliverables

### 1. CLI Package Structure

```
src/cli/
├── __init__.py
├── main.py              # Entry point, argument parsing
├── commands/
│   ├── __init__.py
│   ├── review.py        # Code review commands
│   ├── scan.py          # Vulnerability scanning
│   ├── test.py          # Test generation
│   └── config.py        # Configuration management
├── output/
│   ├── __init__.py
│   ├── formatters.py    # JSON, table, markdown output
│   └── colors.py        # Terminal coloring
└── utils/
    ├── __init__.py
    ├── config_loader.py # Load .devmind.yaml / env
    └── git_utils.py     # Git repo detection
```

### 2. Command Specifications

#### `devmind review <file|directory>`

Review code for issues.

**Arguments:**
| Argument | Type | Description |
|----------|------|-------------|
| `path` | positional | File or directory to review |
| `--reviewers` | list | Specific reviewers: security, performance, style, etc. |
| `--severity` | choice | Minimum severity to report: blocker, warning, suggestion, nit |
| `--format` | choice | Output format: text (default), json, markdown, sarif |
| `--fail-on` | choice | Exit 1 if issues of this severity found: blocker, warning |

**Examples:**
```bash
# Review single file
devmind review src/auth.py

# Review directory, only security issues, JSON output
devmind review ./src --reviewers security --format json

# CI mode: fail if any blockers
devmind review ./src --fail-on blocker
```

---

#### `devmind scan [path]`

Scan for dependency vulnerabilities.

**Arguments:**
| Argument | Type | Description |
|----------|------|-------------|
| `path` | positional | Project root (default: current directory) |
| `--full` | flag | Include exploitability analysis |
| `--severity` | choice | Minimum severity: critical, high, medium, low |
| `--format` | choice | Output: text, json, sarif |
| `--ignore` | list | CVE IDs to ignore |
| `--fail-on` | choice | Exit 1 for this severity or above |

**Examples:**
```bash
# Quick scan
devmind scan

# Full scan with exploitability, JSON output
devmind scan --full --format json

# CI mode: fail on high or critical
devmind scan --fail-on high
```

---

#### `devmind test <file>`

Generate tests for source file.

**Arguments:**
| Argument | Type | Description |
|----------|------|-------------|
| `file` | positional | Source file to generate tests for |
| `--output` | path | Output directory (default: tests/) |
| `--framework` | choice | Test framework: pytest, unittest, jest |
| `--coverage` | path | Existing coverage file to find gaps |
| `--dry-run` | flag | Print tests without writing files |

**Examples:**
```bash
# Generate pytest tests
devmind test src/services/payment.py

# Jest tests for TypeScript
devmind test src/auth.ts --framework jest

# Preview without writing
devmind test src/utils.py --dry-run
```

---

#### `devmind pr-review <repo> <pr_number>`

Review a GitHub PR.

**Arguments:**
| Argument | Type | Description |
|----------|------|-------------|
| `repo` | positional | Repository (owner/name) |
| `pr_number` | positional | PR number |
| `--post-comments` | flag | Post review comments to GitHub |
| `--reviewers` | list | Specific reviewers to run |

**Examples:**
```bash
# Review PR locally
devmind pr-review myorg/myrepo 42

# Review and post comments
devmind pr-review myorg/myrepo 42 --post-comments
```

---

#### `devmind config`

Manage configuration.

**Subcommands:**
```bash
devmind config init          # Create .devmind.yaml
devmind config show          # Show current config
devmind config set KEY VALUE # Set config value
```

---

### 3. Configuration File (.devmind.yaml)

```yaml
# .devmind.yaml - Project-level configuration

# LLM Settings
llm:
  anthropic_api_key: ${ANTHROPIC_API_KEY}  # From environment
  google_api_key: ${GOOGLE_API_KEY}
  
# GitHub Integration  
github:
  token: ${GITHUB_TOKEN}
  
# Default Review Settings
review:
  enabled_reviewers:
    - security
    - performance
    - correctness
    - style
  fail_on: blocker
  
# Vulnerability Scanning
scan:
  full_analysis: false
  ignore_cves: []
  fail_on: high
  
# Test Generation
test:
  framework: pytest
  output_dir: tests/
```

---

### 4. Output Formatters

#### Text (Default - Human Readable)
```
╭──────────────────────────────────────────────────────────╮
│ DevMind Review: src/auth.py                              │
╰──────────────────────────────────────────────────────────╯

🔴 BLOCKER (1)
━━━━━━━━━━━━━━
[security] Line 45: SQL Injection Vulnerability
  User input directly concatenated into query string.
  ↳ Fix: Use parameterized queries with placeholders.

⚠️  WARNING (2)
━━━━━━━━━━━━━━
[performance] Line 23: N+1 Query Pattern
  Database called inside loop. Consider batch fetch.

[style] Line 67: Function too long (85 lines)
  Consider breaking into smaller functions.

Summary: 1 blocker, 2 warnings, 5 suggestions
```

#### JSON (Machine Readable)
```json
{
  "file": "src/auth.py",
  "summary": {
    "blockers": 1,
    "warnings": 2,
    "suggestions": 5
  },
  "comments": [...]
}
```

#### SARIF (Static Analysis Results Interchange Format)
For integration with GitHub Code Scanning, VS Code, etc.

---

### 5. Installation Methods

#### Via pip (Recommended)
```bash
pip install devmind-ai
```

#### Via pipx (Isolated)
```bash
pipx install devmind-ai
```

#### Development
```bash
pip install -e ".[cli]"
```

**pyproject.toml addition:**
```toml
[project.scripts]
devmind = "src.cli.main:cli"

[project.optional-dependencies]
cli = [
    "typer>=0.9.0",
    "rich>=13.0.0",
    "shellingham>=1.5.0",
]
```

---

## Implementation Plan

### Phase 13.1: Core CLI Framework (2-3 days)
- [ ] Set up Typer application structure
- [ ] Implement `devmind review` command
- [ ] Add text and JSON formatters
- [ ] Configuration loading from .devmind.yaml and env

### Phase 13.2: All Commands (3-4 days)
- [ ] Implement `devmind scan` command
- [ ] Implement `devmind test` command
- [ ] Implement `devmind pr-review` command
- [ ] Implement `devmind config` subcommands

### Phase 13.3: CI/CD Integration (2 days)
- [ ] SARIF output format
- [ ] Exit codes based on findings
- [ ] GitHub Actions example workflow
- [ ] GitLab CI example

### Phase 13.4: Polish & Documentation (2 days)
- [ ] Shell completion (bash, zsh, fish)
- [ ] Man pages / help text
- [ ] Tutorial documentation
- [ ] Demo video/GIF for README

---

## Technical Notes

### Standalone vs Server Mode

The CLI should support two modes:

1. **Standalone Mode (Default)**
   - Direct use of agents without running server
   - No database required
   - Uses file-based caching for performance
   
2. **Server Mode**
   - Connects to running DevMind API server
   - Required for PR reviews with full context
   - Enables team-wide configuration

```bash
# Standalone (default)
devmind review file.py

# Connect to server
devmind --server http://localhost:8000 review file.py
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success, no issues matching fail-on threshold |
| 1 | Issues found matching fail-on threshold |
| 2 | CLI usage error |
| 3 | Configuration error |
| 4 | Network/API error |

---

## Dependencies

```toml
cli = [
    "typer[all]>=0.9.0",      # CLI framework
    "rich>=13.0.0",            # Rich terminal output
    "pyyaml>=6.0",             # Config file parsing
    "httpx>=0.26.0",           # API client (server mode)
]
```

---

## Success Criteria

- [ ] User can review a file with single command
- [ ] User can scan project for vulnerabilities with single command
- [ ] User can generate tests with single command
- [ ] CI/CD integration works with exit codes
- [ ] JSON and SARIF output available for tooling
- [ ] Configuration can be project-level or global
- [ ] Documentation and examples complete
