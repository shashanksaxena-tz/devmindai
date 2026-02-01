# DevMind AI - Complete User Guide

A comprehensive AI-powered developer toolkit with 11+ intelligent agents for code review, security scanning, testing, and documentation generation. Works with multiple AI coding assistants including Claude Code, Gemini CLI, GitHub Copilot, Aider, Cline, and OpenCode.

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Available Agents](#available-agents)
- [Using DevMind on External Projects](#using-devmind-on-external-projects)
  - [Method 1: Direct CLI](#method-1-direct-cli)
  - [Method 2: Generate PR for GitHub Repo](#method-2-generate-pr-for-github-repo)
  - [Method 3: Via AI Coding Assistants](#method-3-via-ai-coding-assistants)
- [AI Coding Assistant Integrations](#ai-coding-assistant-integrations)
  - [Claude Code](#claude-code)
  - [Gemini CLI](#gemini-cli)
  - [GitHub Copilot](#github-copilot)
  - [Aider](#aider)
  - [Cline](#cline)
  - [OpenCode](#opencode)
- [CLI Reference](#cli-reference)
- [API Reference](#api-reference)
- [Examples & Workflows](#examples--workflows)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

```bash
# 1. Clone and setup DevMind
git clone <repository-url>
cd devmindai/DevMind-AI
python -m venv venv && source venv/bin/activate
pip install -e ".[cli,dev]"

# 2. Set up API keys
export GOOGLE_API_KEY=your-google-api-key  # For Gemini (primary)
export ANTHROPIC_API_KEY=your-key          # Optional for Claude

# 3. Run on ANY external project
devmind document /path/to/any/project -w --all

# 4. Or generate a PR for a GitHub repo
devmind generate-pr owner/repo
```

---

## Installation

### Prerequisites

- Python 3.9+
- Git
- API keys (Google Gemini recommended - free tier available)
- Optional: GitHub CLI (`gh`) for PR generation

### Full Setup

```bash
# Clone DevMind
git clone <repository-url>
cd devmindai/DevMind-AI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install with all extras
pip install -e ".[cli,dev]"

# Configure environment
cat > .env << 'EOF'
GOOGLE_API_KEY=your-google-api-key
ANTHROPIC_API_KEY=your-anthropic-key  # Optional
SECRET_KEY=any-random-string
APP_ENV=development
EOF

# Verify installation
devmind --help
```

---

## Available Agents

| Agent | CLI Command | Description |
|-------|-------------|-------------|
| **Code Reviewer** | `devmind review` | AI code review for quality, security, performance |
| **Security Scanner** | `devmind scan` | OWASP Top 10, secrets detection, dependency scan |
| **Test Generator** | `devmind test` | Generate unit tests with edge cases |
| **Project Documenter** | `devmind document` | Generate AI-ready docs for 10+ formats |
| **PR Generator** | `devmind generate-pr` | Clone repo, generate docs, create PR |
| **PR Reviewer** | `devmind pr-review` | Review GitHub pull requests |
| **Run With** | `devmind run-with` | Execute via AI coding assistants |

---

## Using DevMind on External Projects

### Method 1: Direct CLI

Run DevMind directly on any local project to analyze **all files, folders, and services**:

```bash
# Navigate to ANY project (not DevMind)
cd /path/to/your/external/project

# Option A: Analyze entire project structure
devmind document . --analyze

# Option B: Generate AI docs for the WHOLE project
devmind document . -w --all

# Option C: Generate specific formats
devmind document . -w -f claude -f copilot -f gemini

# Option D: Run security scan on entire codebase
devmind scan . --fail-on high

# Option E: Review all Python files
devmind review src/
```

**What happens:**
1. DevMind analyzes your **entire codebase** (all files, directories, services)
2. Detects languages, frameworks, architecture patterns
3. Extracts build/test/lint commands
4. Generates documentation optimized for each AI assistant
5. Writes files to `devmind-output/` (organized) or directly to project (`-p`)

**Output structure:**
```
devmind-output/
└── project-documenter/
    └── your-project-20240130-123456/
        ├── README.md           # Usage guide
        ├── claude/CLAUDE.md
        ├── copilot/copilot-instructions.md
        ├── cursor/rules/*.mdc
        ├── gemini/GEMINI.md
        ├── windsurf/rules/*.md
        ├── aider/CONVENTIONS.md
        ├── cline/.clinerules/*.md
        └── opencode/AGENTS.md
```

### Method 2: Generate PR for GitHub Repo

Automatically generate documentation for any GitHub repository and create a pull request:

```bash
# Prerequisites: Install and authenticate GitHub CLI
# brew install gh && gh auth login

# Generate docs and create PR for any public repo
devmind generate-pr facebook/react

# With custom options
devmind generate-pr owner/repo \
  --branch feature/ai-docs \
  --title "feat: Add AI coding assistant documentation" \
  --all

# Specific formats only
devmind generate-pr owner/repo -f claude -f copilot -f gemini

# Dry run to preview
devmind generate-pr owner/repo --dry-run
```

**What happens:**
1. Clones the repository to a temp directory
2. Analyzes the entire codebase
3. Generates documentation for all AI formats
4. Creates a new branch, commits changes
5. Pushes and creates a PR via GitHub CLI

### Method 3: Via AI Coding Assistants

Use your preferred AI coding assistant to run DevMind agents:

```bash
# List available AI tools and their status
devmind tools

# Run DevMind agent via specific AI tool
devmind run-with gemini review src/main.py
devmind run-with aider test src/utils.py
devmind run-with claude document /path/to/project
devmind run-with copilot scan .

# Dry run to see command
devmind run-with opencode document . --dry-run
```

---

## AI Coding Assistant Integrations

DevMind generates documentation for **10 different AI coding assistant formats** and can be used **through** these assistants.

### Claude Code

**Generated files:** `CLAUDE.md`

**Setup for your external project:**
```bash
# Generate Claude Code docs for your project
cd /path/to/your/project
devmind document . -w -f claude -p

# Now use Claude Code in your project
claude
```

**Using Claude Code to run DevMind:**
```bash
# In Claude Code session:
# "Run devmind document on this project and write to devmind-output"
poetry run devmind document . -w
```

### Gemini CLI

**Generated files:** `.gemini/GEMINI.md`, `.gemini/commands/*.toml`

**Setup for your external project:**
```bash
# Install Gemini CLI
npm install -g @anthropic-ai/gemini-cli

# Generate Gemini docs for your project
cd /path/to/your/project
devmind document . -w -f gemini -p

# Custom commands are created in .gemini/commands/
# Use them with: /review, /scan, /test, /document
```

**Using Gemini CLI with DevMind:**
```bash
# Start Gemini CLI in your project
gemini

# Use custom commands (if generated with -p flag)
/review src/main.py
/scan .
/document . -w

# Or ask directly
"Run poetry run devmind scan . and summarize the results"
```

### GitHub Copilot

**Generated files:** `.github/copilot-instructions.md`

**Setup for your external project:**
```bash
# Generate Copilot instructions
cd /path/to/your/project
devmind document . -w -f copilot -p

# The file will be at .github/copilot-instructions.md
# Copilot in VS Code/JetBrains will automatically read this
```

**Using GitHub Copilot CLI:**
```bash
# Install Copilot CLI extension
gh extension install github/gh-copilot

# Use Copilot to explain/suggest
gh copilot explain "devmind document . -w --all"
gh copilot suggest "scan this project for security vulnerabilities"
```

### Aider

**Generated files:** `CONVENTIONS.md`, `.aider.conf.yml`

**Setup for your external project:**
```bash
# Install Aider
pip install aider-chat

# Generate Aider config for your project
cd /path/to/your/project
devmind document . -w -f aider -p

# Start Aider with the generated config
aider --config .aider.conf.yml
```

**Using Aider with DevMind:**
```bash
# Aider automatically reads CONVENTIONS.md
aider

# In Aider session:
# "Run the DevMind security scanner on this project"
# "Generate tests for src/utils.py using DevMind"
```

### Cline

**Generated files:** `.clinerules/*.md`

**Setup for your external project:**
```bash
# Generate Cline rules
cd /path/to/your/project
devmind document . -w -f cline -p

# Files created:
# .clinerules/project-overview.md
# .clinerules/development-guidelines.md
# .clinerules/commands-reference.md
```

**Using Cline in VS Code:**
1. Install Cline extension in VS Code
2. Open your project (with generated `.clinerules/`)
3. Cline automatically reads the rules
4. Ask: "Run DevMind code review on this file"

### OpenCode

**Generated files:** `AGENTS.md`, `.opencode.json`

**Setup for your external project:**
```bash
# Install OpenCode
npm install -g opencode-ai

# Generate OpenCode config
cd /path/to/your/project
devmind document . -w -f opencode -p

# Start OpenCode
opencode
```

**Using OpenCode with DevMind:**
```bash
# OpenCode reads AGENTS.md for workflow instructions
opencode

# In session:
# "Run devmind scan to check for vulnerabilities"
# "Generate documentation using devmind document"
```

---

## CLI Reference

### Core Commands

```bash
# Documentation Generation
devmind document <path> [options]
  -w, --write              Write to devmind-output/
  -p, --to-project         Write directly to project
  -f, --format <format>    Specific format (multiple allowed)
  --all                    All formats including human docs
  --analyze                Only analyze, don't generate
  --human                  Include human-readable docs
  --speckit                Include GitHub Spec Kit

# Security Scanning
devmind scan <path> [options]
  --fail-on <level>        Fail on severity: critical/high/medium/low
  --format <format>        Output: text/json

# Code Review
devmind review <path> [options]
  --focus <area>           Focus: security/performance/style
  --fail-on <level>        Fail on: blocker/warning/suggestion
  --format <format>        Output: table/json

# Test Generation
devmind test <file> [options]
  --framework <name>       Framework: pytest/unittest/jest
  --output <path>          Output file path

# GitHub PR Generation
devmind generate-pr <repo> [options]
  -f, --format <format>    Documentation formats
  -b, --branch <name>      Branch name
  -t, --title <title>      PR title
  --all                    All formats
  --dry-run                Preview only

# AI Tool Integration
devmind run-with <tool> <agent> <target>
  Tools: gemini, claude, aider, opencode, copilot
  Agents: review, scan, test, document

devmind tools              List AI tools and status
```

### Format Options

| Format | Output | Description |
|--------|--------|-------------|
| `claude` | `CLAUDE.md` | Claude Code context |
| `copilot` | `.github/copilot-instructions.md` | GitHub Copilot |
| `cursor` | `.cursor/rules/*.mdc` | Cursor AI rules |
| `gemini` | `.gemini/GEMINI.md` + commands | Gemini CLI |
| `windsurf` | `.windsurf/rules/*.md` | Windsurf/Codeium |
| `aider` | `CONVENTIONS.md`, `.aider.conf.yml` | Aider |
| `cline` | `.clinerules/*.md` | Cline VS Code |
| `opencode` | `AGENTS.md`, `.opencode.json` | OpenCode |
| `speckit` | `.specify/memory/constitution.md` | GitHub Spec Kit |
| `human` | `docs/README.md`, `ARCHITECTURE.md` | Human docs |

---

## API Reference

### Starting the API Server

```bash
cd DevMind-AI
uvicorn src.api.main:app --reload --port 8000

# Docs at http://localhost:8000/docs
```

### Key Endpoints

```bash
# Project Documentation
POST /api/v1/project-docs/analyze
POST /api/v1/project-docs/generate
GET  /api/v1/project-docs/formats

# Code Review
POST /api/v1/reviews/code

# Security Scan
POST /api/v1/security/scan

# Test Generation
POST /api/v1/tests/generate
```

### Example API Calls

```bash
# Analyze a project
curl -X POST http://localhost:8000/api/v1/project-docs/analyze \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/project"}'

# Generate documentation
curl -X POST http://localhost:8000/api/v1/project-docs/generate \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/path/to/project",
    "formats": ["claude", "copilot", "gemini"],
    "write_files": true
  }'
```

---

## Examples & Workflows

### Workflow 1: Onboard AI to New Project

```bash
# 1. Navigate to your project
cd /path/to/your/project

# 2. Generate all AI documentation
devmind document . --all -w -p

# 3. Commit the generated files
git add CLAUDE.md GEMINI.md AGENTS.md CONVENTIONS.md \
        .github/ .gemini/ .cursor/ .windsurf/ .clinerules/ \
        .opencode.json .aider.conf.yml
git commit -m "Add AI coding assistant documentation"
git push

# Now all AI assistants have context about your project!
```

### Workflow 2: PR for Open Source Project

```bash
# Fork the repo on GitHub first, then:
devmind generate-pr your-username/forked-repo \
  --branch add-ai-docs \
  --title "docs: Add AI coding assistant documentation" \
  --all

# The PR is created automatically!
```

### Workflow 3: Security Audit via Gemini CLI

```bash
# 1. Start Gemini CLI in your project
cd /path/to/project
gemini

# 2. In Gemini, ask:
"Run a comprehensive security scan using DevMind:
poetry run devmind scan . --fail-on high

Then analyze the results and suggest fixes."
```

### Workflow 4: Generate Tests via Aider

```bash
# 1. Start Aider
cd /path/to/project
aider --config .aider.conf.yml

# 2. In Aider:
"Generate unit tests for src/services/auth.py using DevMind:
poetry run devmind test src/services/auth.py --output tests/test_auth.py"
```

### Workflow 5: Full Project Analysis

```bash
#!/bin/bash
# full-analysis.sh

PROJECT_PATH=${1:-.}

echo "=== DevMind Full Project Analysis ==="

echo "\n1. Security Scan..."
devmind scan "$PROJECT_PATH" --format json > security-report.json

echo "\n2. Code Review..."
devmind review "$PROJECT_PATH" --format json > review-report.json

echo "\n3. Generate AI Documentation..."
devmind document "$PROJECT_PATH" -w --all

echo "\n=== Analysis Complete ==="
echo "Reports: security-report.json, review-report.json"
echo "Documentation: devmind-output/"
```

### Workflow 6: Using with Multiple AI Assistants

```bash
# Generate docs for all AI assistants
devmind document /path/to/project -w --all -p

# Now you can use ANY of these:

# Claude Code
claude  # Reads CLAUDE.md

# Gemini CLI
gemini  # Reads .gemini/GEMINI.md, uses /commands

# Aider
aider --config .aider.conf.yml  # Reads CONVENTIONS.md

# OpenCode
opencode  # Reads AGENTS.md

# Cline in VS Code
# Just open project, Cline reads .clinerules/

# GitHub Copilot
# Reads .github/copilot-instructions.md automatically
```

---

## Troubleshooting

### "Command not found: devmind"

```bash
pip install -e ".[cli,dev]"
# Or add to PATH
export PATH=$PATH:$(python -c "import site; print(site.USER_BASE)")/bin
```

### "API key not found"

```bash
export GOOGLE_API_KEY=your-key
# Or create .env file
echo "GOOGLE_API_KEY=your-key" >> .env
```

### "gh: command not found" (for generate-pr)

```bash
# Install GitHub CLI
# macOS
brew install gh

# Linux
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update && sudo apt install gh

# Authenticate
gh auth login
```

### "Permission denied" when creating PR

```bash
# Make sure you have write access to the repo
# Or fork it first:
gh repo fork owner/repo
devmind generate-pr your-username/repo
```

---

## Summary: Quick Command Reference

| Task | Command |
|------|---------|
| Analyze any project | `devmind document /path -w` |
| Generate all AI docs | `devmind document . --all -w -p` |
| Create PR for GitHub repo | `devmind generate-pr owner/repo` |
| Security scan | `devmind scan . --fail-on high` |
| Code review | `devmind review src/` |
| Generate tests | `devmind test src/file.py` |
| Use via Gemini CLI | `devmind run-with gemini review file.py` |
| Use via Aider | `devmind run-with aider test file.py` |
| List AI tools | `devmind tools` |

---

## License

MIT
