# DevMind AI - Complete User Guide

A comprehensive AI-powered developer toolkit with 11 intelligent agents for code review, security scanning, testing, documentation, and more.

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Available Agents](#available-agents)
- [Usage Methods](#usage-methods)
  - [CLI (Command Line)](#cli-command-line)
  - [API (REST)](#api-rest)
  - [Dashboard (Web UI)](#dashboard-web-ui)
  - [Programmatic (Python)](#programmatic-python)
- [Agent Guides](#agent-guides)
- [Working with Repositories](#working-with-repositories)
- [Examples & Workflows](#examples--workflows)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

```bash
# 1. Clone and setup
git clone <repository-url>
cd devmindai/DevMind-AI

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install
pip install -e ".[cli,dev]"

# 4. Set up API keys (create .env file)
cat > .env << 'EOF'
ANTHROPIC_API_KEY=your-anthropic-api-key
GOOGLE_API_KEY=your-google-api-key
SECRET_KEY=your-secret-key
APP_ENV=development
EOF

# 5. Run your first command - review a file
devmind review path/to/your/code.py

# 6. Or scan a whole project for vulnerabilities
devmind scan /path/to/your/project

# 7. Generate AI documentation for your project
devmind document /path/to/your/project -w
```

---

## Installation

### Prerequisites

- Python 3.9 or higher
- pip
- Git
- API keys for AI providers (Anthropic Claude and/or Google Gemini)

### Step-by-Step Setup

```bash
# Clone the repository
git clone <repository-url>
cd devmindai/DevMind-AI

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -e ".[cli,dev]"

# Verify installation
devmind --version
```

### Environment Configuration

Create a `.env` file in the `DevMind-AI` directory:

```bash
# Required - AI Provider API Keys
ANTHROPIC_API_KEY=sk-ant-your-key-here      # For Claude (complex tasks)
GOOGLE_API_KEY=your-google-key-here          # For Gemini (simple/fast tasks)

# Required - Application Settings
SECRET_KEY=generate-a-secure-random-key
APP_NAME="DevMind AI"
APP_ENV=development
DEBUG=True

# Optional - Database (for persistent storage)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/devmind

# Optional - Redis (for caching)
REDIS_URL=redis://localhost:6379/0

# Optional - Qdrant (for vector search in ADR agent)
QDRANT_URL=http://localhost:6333

# Optional - GitHub (for PR reviews)
GITHUB_TOKEN=ghp_your-github-token
```

---

## Available Agents

| Agent | What It Does | CLI Command |
|-------|--------------|-------------|
| **Code Reviewer** | Reviews code for quality, security, performance, style | `devmind review` |
| **Vulnerability Scanner** | Scans for security vulnerabilities (OWASP Top 10) | `devmind scan` |
| **Test Generator** | Generates unit tests for your code | `devmind test` |
| **Project Documenter** | Creates AI-ready docs (Claude, Copilot, Cursor, etc.) | `devmind document` |
| **Doc Generator** | Generates docstrings and API documentation | API only |
| **Debt Analyzer** | Analyzes technical debt and suggests improvements | API only |
| **Incident Responder** | Helps triage and respond to production incidents | API only |
| **Code Migrator** | Assists with code migration between frameworks/versions | API only |
| **Query Optimizer** | Optimizes SQL queries for performance | API only |
| **Pipeline Generator** | Generates CI/CD pipeline configurations | API only |
| **ADR Recorder** | Records Architecture Decision Records | API only |

---

## Usage Methods

### CLI (Command Line)

The easiest way to use DevMind AI. All commands follow the pattern:

```bash
devmind <command> [arguments] [options]
```

#### Available CLI Commands

```bash
# Show all available commands
devmind --help

# Initialize configuration
devmind config init

# Show current configuration
devmind config show
```

---

### API (REST)

Start the API server for programmatic access:

```bash
# Start the server
cd DevMind-AI
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs (Swagger UI)
# Alternative docs at http://localhost:8000/redoc
```

#### API Endpoints Overview

| Endpoint | Agent | Methods |
|----------|-------|---------|
| `/api/reviews` | Code Reviewer | POST |
| `/api/security` | Vulnerability Scanner | POST |
| `/api/tests` | Test Generator | POST |
| `/api/project-docs` | Project Documenter | GET, POST |
| `/api/docs` | Doc Generator | POST |
| `/api/debt` | Debt Analyzer | POST |
| `/api/incidents` | Incident Responder | POST |
| `/api/migrations` | Code Migrator | POST |
| `/api/queries` | Query Optimizer | POST |
| `/api/pipelines` | Pipeline Generator | POST |
| `/api/adrs` | ADR Recorder | GET, POST |

---

### Dashboard (Web UI)

A Streamlit-based web dashboard for visual interaction:

```bash
# Start the dashboard
cd DevMind-AI/dashboard
streamlit run app.py

# Opens at http://localhost:8501
```

The dashboard provides pages for:
- **Security** - Visual vulnerability scanning
- **Reviews** - Code review interface
- **Tests** - Test generation UI
- **Debt** - Technical debt analysis

---

### Programmatic (Python)

Use agents directly in your Python code:

```python
import asyncio
from src.agents.base import AgentContext

# Import the agent you need
from src.agents.code_reviewer import CodeReviewerAgent
from src.agents.vuln_scanner import VulnScannerAgent
from src.agents.test_generator import TestGeneratorAgent
from src.agents.project_documenter import ProjectDocumenterAgent

async def main():
    context = AgentContext()

    # Example: Code review
    reviewer = CodeReviewerAgent()
    result = await reviewer.execute(
        context,
        code="def foo(): pass",
        file_path="example.py"
    )
    print(result)

asyncio.run(main())
```

---

## Agent Guides

### 1. Code Reviewer Agent

**What it does:** Analyzes code for quality issues, security vulnerabilities, performance problems, style violations, and missing tests.

**CLI Usage:**
```bash
# Review a single file
devmind review src/main.py

# Review a directory
devmind review src/

# Review with specific focus
devmind review src/api/ --focus security

# Set failure threshold
devmind review src/ --fail-on blocker

# Output as JSON
devmind review src/main.py --format json
```

**API Usage:**
```bash
curl -X POST http://localhost:8000/api/reviews/code \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def hello():\n    print(\"world\")",
    "file_path": "hello.py",
    "language": "python"
  }'
```

**What you get:**
- Security issues (injection, XSS, etc.)
- Performance problems
- Code correctness issues
- Style violations
- Testing gaps
- Suggestions for improvement

---

### 2. Vulnerability Scanner Agent

**What it does:** Scans code for security vulnerabilities including OWASP Top 10, hardcoded secrets, insecure dependencies.

**CLI Usage:**
```bash
# Scan current directory
devmind scan .

# Scan a specific project
devmind scan /path/to/project

# Scan with severity threshold
devmind scan . --fail-on high

# Output as JSON
devmind scan . --format json
```

**API Usage:**
```bash
curl -X POST http://localhost:8000/api/security/scan \
  -H "Content-Type: application/json" \
  -d '{
    "code": "password = \"secret123\"",
    "file_path": "config.py"
  }'
```

**What you get:**
- Vulnerability type and severity (critical/high/medium/low)
- Affected line numbers
- Description of the issue
- Remediation recommendations

---

### 3. Test Generator Agent

**What it does:** Automatically generates unit tests for your code with proper mocking and edge case coverage.

**CLI Usage:**
```bash
# Generate tests for a file
devmind test src/utils.py

# Generate tests for a specific function
devmind test src/utils.py --function calculate_total

# Specify test framework
devmind test src/utils.py --framework pytest

# Output to file
devmind test src/utils.py --output tests/test_utils.py
```

**API Usage:**
```bash
curl -X POST http://localhost:8000/api/tests/generate \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def add(a, b): return a + b",
    "file_path": "math_utils.py",
    "framework": "pytest"
  }'
```

**What you get:**
- Complete test file with imports
- Test cases for happy paths
- Edge case tests
- Error handling tests
- Mocked dependencies

---

### 4. Project Documenter Agent (NEW)

**What it does:** Analyzes your entire codebase and generates documentation optimized for AI coding assistants (Claude, Copilot, Cursor, Gemini, Windsurf) and humans.

**CLI Usage:**
```bash
# Analyze a project (no files written)
devmind document /path/to/project

# Generate and write AI documentation
devmind document /path/to/project -w

# Generate all formats (AI + human + governance)
devmind document /path/to/project --all -w

# Generate specific formats only
devmind document . -f claude -f copilot -w

# Only analyze (see what the agent detects)
devmind document . --analyze

# Include GitHub Spec Kit constitution
devmind document . --speckit -w

# Include human-readable docs
devmind document . --human -w

# JSON output for scripting
devmind document . --output-format json
```

**API Usage:**
```bash
# Analyze a project
curl -X POST http://localhost:8000/api/project-docs/analyze \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/project"}'

# Generate documentation
curl -X POST http://localhost:8000/api/project-docs/generate \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/path/to/project",
    "formats": ["claude", "copilot", "cursor"],
    "write_files": true
  }'

# List available formats
curl http://localhost:8000/api/project-docs/formats
```

**Available Formats:**

| Format | Output Files | For |
|--------|--------------|-----|
| `claude` | `CLAUDE.md` | Claude Code |
| `copilot` | `.github/copilot-instructions.md` | GitHub Copilot |
| `cursor` | `.cursor/rules/*.mdc` | Cursor AI |
| `gemini` | `GEMINI.md` | Google Gemini |
| `windsurf` | `.windsurf/rules/*.md` | Windsurf/Codeium |
| `speckit` | `.specify/memory/constitution.md` | GitHub Spec Kit |
| `human` | `docs/README.md`, `docs/ARCHITECTURE.md`, `docs/CONTRIBUTING.md` | Humans |

**What you get:**
- Project context and structure
- Tech stack and frameworks
- Build/test/lint commands
- Coding conventions
- Architecture patterns
- Governance rules (for Spec Kit)

---

### 5. PR Review (GitHub Integration)

**What it does:** Reviews GitHub Pull Requests and posts comments directly.

**CLI Usage:**
```bash
# Review a PR (requires GITHUB_TOKEN in .env)
devmind pr-review owner/repo 123

# Example
devmind pr-review facebook/react 12345
```

**What you get:**
- Inline comments on specific lines
- Summary of issues found
- Approval/changes requested

---

## Working with Repositories

### Scanning Your Own Project

```bash
# Navigate to your project
cd /path/to/your/project

# Run security scan
devmind scan .

# Run code review on specific files
devmind review src/

# Generate tests for your utilities
devmind test src/utils/

# Generate AI documentation
devmind document . -w
```

### Scanning a GitHub Repository

```bash
# Clone the repo first
git clone https://github.com/owner/repo.git
cd repo

# Now run any agent
devmind scan .
devmind review src/
devmind document . -w
```

### Scanning Specific Files

```bash
# Single file
devmind review src/api/auth.py
devmind test src/models/user.py

# Multiple files (run multiple commands)
devmind review src/api/auth.py
devmind review src/api/users.py

# Or review a directory
devmind review src/api/
```

---

## Examples & Workflows

### Workflow 1: New Project Security Audit

```bash
# 1. Clone the project
git clone https://github.com/example/webapp.git
cd webapp

# 2. Run vulnerability scan
devmind scan . --fail-on high

# 3. Review critical files
devmind review src/auth/ --focus security
devmind review src/api/ --focus security

# 4. Generate report (JSON)
devmind scan . --format json > security-report.json
```

### Workflow 2: Pre-Commit Code Review

```bash
# Review staged changes before committing
git diff --cached --name-only | while read file; do
  if [[ "$file" == *.py ]]; then
    devmind review "$file"
  fi
done
```

### Workflow 3: Generate Tests for New Feature

```bash
# 1. Write your feature code
# src/features/payment.py

# 2. Generate tests
devmind test src/features/payment.py --output tests/test_payment.py

# 3. Run the generated tests
pytest tests/test_payment.py -v
```

### Workflow 4: Onboard AI Assistant to Your Project

```bash
# 1. Navigate to your project
cd /path/to/your/project

# 2. Generate AI documentation for all assistants
devmind document . --all -w

# 3. Check what was created
ls -la CLAUDE.md GEMINI.md
ls -la .github/copilot-instructions.md
ls -la .cursor/rules/
ls -la .windsurf/rules/
ls -la .specify/memory/

# 4. Commit the documentation
git add CLAUDE.md GEMINI.md .github/ .cursor/ .windsurf/ .specify/
git commit -m "Add AI assistant documentation"

# Now Claude Code, Copilot, Cursor, Gemini, and Windsurf
# will have context about your project!
```

### Workflow 5: Full Project Analysis

```bash
# 1. Security scan
echo "=== Security Scan ==="
devmind scan .

# 2. Code review
echo "=== Code Review ==="
devmind review src/

# 3. Generate missing tests
echo "=== Test Generation ==="
devmind test src/core/

# 4. Generate documentation
echo "=== Documentation ==="
devmind document . --all -w
```

### Workflow 6: Using the API Server

```bash
# Terminal 1: Start the API server
cd DevMind-AI
uvicorn src.api.main:app --reload

# Terminal 2: Make API calls
# Scan for vulnerabilities
curl -X POST http://localhost:8000/api/security/scan \
  -H "Content-Type: application/json" \
  -d '{"code": "import os; os.system(user_input)", "file_path": "danger.py"}'

# Generate tests
curl -X POST http://localhost:8000/api/tests/generate \
  -H "Content-Type: application/json" \
  -d '{"code": "def greet(name): return f\"Hello {name}\"", "file_path": "greet.py"}'
```

### Workflow 7: Using the Dashboard

```bash
# Start the dashboard
cd DevMind-AI/dashboard
streamlit run app.py

# Open http://localhost:8501 in your browser
# Use the sidebar to navigate between:
# - Security (vulnerability scanning)
# - Reviews (code review)
# - Tests (test generation)
# - Debt (technical debt analysis)
```

---

## Understanding Agent Output

### Code Review Output

```
╭─────────────────────────────────────────╮
│           Code Review Results           │
╰─────────────────────────────────────────╯

File: src/api/auth.py

🔴 BLOCKER (Security)
   Line 45: SQL Injection vulnerability
   Suggestion: Use parameterized queries

⚠️  WARNING (Performance)
   Line 23: N+1 query detected in loop
   Suggestion: Use batch fetching

💡 SUGGESTION (Style)
   Line 12: Function too long (85 lines)
   Suggestion: Break into smaller functions

Summary: 1 blocker, 1 warning, 1 suggestion
```

### Vulnerability Scan Output

```
╭─────────────────────────────────────────╮
│         Security Scan Results           │
╰─────────────────────────────────────────╯

🔴 CRITICAL: Hardcoded credentials
   File: config.py:15
   Code: password = "admin123"
   Fix: Use environment variables

🟠 HIGH: SQL Injection
   File: db/queries.py:42
   Code: query = f"SELECT * FROM users WHERE id={user_id}"
   Fix: Use parameterized queries

🟡 MEDIUM: Missing HTTPS
   File: api/client.py:8
   Code: requests.get("http://api.example.com")
   Fix: Use HTTPS for all external requests

Summary: 1 critical, 1 high, 1 medium
```

### Project Documenter Output

```
╭─────────────────────────────────────────╮
│    Documentation Generated: myproject   │
╰─────────────────────────────────────────╯

Language: Python
Frameworks: FastAPI, SQLAlchemy

Generated Documentation:
┌────────┬──────────────────────────────────────┬─────────────────────┐
│ Format │ File Path                            │ Description         │
├────────┼──────────────────────────────────────┼─────────────────────┤
│ claude │ CLAUDE.md                            │ Claude Code context │
│ copilot│ .github/copilot-instructions.md      │ Copilot instructions│
│ cursor │ .cursor/rules/index.mdc              │ Main Cursor rules   │
│ cursor │ .cursor/rules/python.mdc             │ Python rules        │
│ gemini │ GEMINI.md                            │ Gemini context      │
└────────┴──────────────────────────────────────┴─────────────────────┘

Formats generated: claude, copilot, cursor, gemini, windsurf
Total files: 8

✓ Files written to disk (8 files)
```

---

## Project Structure

```
DevMind-AI/
├── src/
│   ├── agents/           # AI agent implementations
│   │   ├── adr_recorder/
│   │   ├── code_migrator/
│   │   ├── code_reviewer/
│   │   ├── debt_analyzer/
│   │   ├── doc_generator/
│   │   ├── incident_responder/
│   │   ├── pipeline_generator/
│   │   ├── project_documenter/   # NEW - Multi-format doc generator
│   │   ├── query_optimizer/
│   │   ├── test_generator/
│   │   └── vuln_scanner/
│   ├── api/              # FastAPI routes
│   ├── cli/              # CLI commands (devmind)
│   ├── core/             # Core logic, LLM routing
│   ├── db/               # Database models
│   └── integrations/     # External integrations
├── tests/                # Test suite
├── dashboard/            # Streamlit web UI
└── docs/                 # Documentation
```

---

## Troubleshooting

### "Command not found: devmind"

```bash
# Make sure you installed with CLI extras
pip install -e ".[cli,dev]"

# Or add to PATH
export PATH=$PATH:$(python -c "import site; print(site.USER_BASE)")/bin
```

### "ModuleNotFoundError"

```bash
# Set PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Or install in development mode
pip install -e ".[cli,dev]"
```

### "API key not found"

```bash
# Create .env file or export variables
export ANTHROPIC_API_KEY=your-key
export GOOGLE_API_KEY=your-key

# Or create .env file
echo "ANTHROPIC_API_KEY=your-key" >> .env
echo "GOOGLE_API_KEY=your-key" >> .env
```

### "Pydantic validation error"

```bash
# Ensure all required env vars are set
export SECRET_KEY=any-random-string
export APP_ENV=development
```

### Tests failing

```bash
# Set up test environment
export PYTHONPATH=$PYTHONPATH:$(pwd)
export ANTHROPIC_API_KEY=dummy
export GOOGLE_API_KEY=dummy
export SECRET_KEY=dummy

# Clear cache
find . -type d -name __pycache__ -exec rm -rf {} +

# Run tests
pytest tests/ -v
```

### Dashboard not starting

```bash
# Install streamlit
pip install streamlit

# Run from correct directory
cd DevMind-AI/dashboard
streamlit run app.py
```

---

## Getting Help

```bash
# Show all commands
devmind --help

# Show help for specific command
devmind review --help
devmind scan --help
devmind document --help

# Show version
devmind --version
```

---

## Summary: What to Run and When

| Task | Command |
|------|---------|
| Review code quality | `devmind review <file-or-dir>` |
| Find security issues | `devmind scan <dir>` |
| Generate tests | `devmind test <file>` |
| Review GitHub PR | `devmind pr-review owner/repo 123` |
| Generate AI docs | `devmind document <dir> -w` |
| Start API server | `uvicorn src.api.main:app --reload` |
| Start web dashboard | `streamlit run dashboard/app.py` |

---

## License

MIT
