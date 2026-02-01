# Using DevMind with AI Coding Assistants

DevMind generates documentation for 10+ AI coding assistants and can be used through these tools.

## Overview

| Assistant | Generated Files | Use DevMind Through It? |
|-----------|-----------------|-------------------------|
| Claude Code | `CLAUDE.md` | Yes |
| GitHub Copilot | `.github/copilot-instructions.md` | Limited |
| Cursor | `.cursor/rules/*.mdc` | No |
| Gemini CLI | `.gemini/GEMINI.md` | Yes |
| Windsurf | `.windsurf/rules/*.md` | No |
| Aider | `CONVENTIONS.md`, `.aider.conf.yml` | Yes |
| Cline | `.clinerules/*.md` | Limited |
| OpenCode | `AGENTS.md`, `.opencode.json` | Yes |
| GitHub Spec Kit | `.specify/memory/constitution.md` | No |

## Generate Documentation for All Assistants

```bash
# All formats
devmind document /path/to/project -w --all

# Specific formats
devmind document . -w -f claude -f copilot -f gemini

# Write directly to project
devmind document . -p -f claude -f copilot
```

---

## Claude Code

**Files generated:** `CLAUDE.md`

### Setup

```bash
# Generate Claude Code docs for your project
cd /path/to/your/project
devmind document . -w -f claude -p

# Copy CLAUDE.md to project root
cp devmind-output/*/claude/CLAUDE.md ./CLAUDE.md

# Start Claude Code
claude
```

### Using Claude Code to Run DevMind

In Claude Code session:

```
"Run devmind document on this project"
> poetry run devmind document . -w

"Scan this project for security vulnerabilities"
> poetry run devmind scan . --fail-on high

"Generate tests for src/auth.py"
> poetry run devmind test src/auth.py --framework pytest
```

Claude Code reads `CLAUDE.md` and understands:
- Project structure
- Available commands
- Development workflows
- Testing patterns

---

## Gemini CLI

**Files generated:** `.gemini/GEMINI.md`, `.gemini/commands/*.toml`

### Setup

```bash
# Install Gemini CLI
npm install -g @google/gemini-cli

# Generate Gemini docs
cd /path/to/your/project
devmind document . -w -f gemini -p

# Start Gemini CLI
gemini
```

### Using Gemini CLI with DevMind

Custom commands are created in `.gemini/commands/`:

```bash
# In Gemini CLI session
/review src/main.py      # Code review
/scan .                  # Security scan
/test src/utils.py       # Generate tests
/document . -w           # Generate docs
```

Or ask directly:

```
"Run a security scan on this project using DevMind"
"Generate documentation for all AI assistants"
```

---

## GitHub Copilot

**Files generated:** `.github/copilot-instructions.md`

### Setup

```bash
# Generate Copilot instructions
cd /path/to/your/project
devmind document . -w -f copilot -p

# The file is created at .github/copilot-instructions.md
# Copilot reads this automatically in VS Code
```

### Using Copilot CLI

```bash
# Install Copilot CLI
gh extension install github/gh-copilot

# Use Copilot to explain commands
gh copilot explain "devmind document . -w --all"

# Get command suggestions
gh copilot suggest "scan project for security issues"
```

---

## Cursor

**Files generated:** `.cursor/rules/*.mdc`

### Setup

```bash
# Generate Cursor rules
cd /path/to/your/project
devmind document . -w -f cursor -p

# Rules are created in .cursor/rules/
# Cursor reads these automatically
```

Cursor uses the rules for:
- Code style guidance
- Project structure understanding
- Command suggestions

---

## Aider

**Files generated:** `CONVENTIONS.md`, `.aider.conf.yml`

### Setup

```bash
# Install Aider
pip install aider-chat

# Generate Aider config
cd /path/to/your/project
devmind document . -w -f aider -p

# Start Aider with config
aider --config .aider.conf.yml
```

### Using Aider with DevMind

Aider reads `CONVENTIONS.md` automatically:

```bash
# In Aider session
"Run DevMind security scanner"
"Generate tests for auth.py using DevMind"
"Create documentation with devmind document"
```

---

## Cline

**Files generated:** `.clinerules/*.md`

### Setup

```bash
# Generate Cline rules
cd /path/to/your/project
devmind document . -w -f cline -p

# Files created:
# .clinerules/project-overview.md
# .clinerules/development-guidelines.md
# .clinerules/commands-reference.md
```

### Using in VS Code

1. Install Cline extension
2. Open project with `.clinerules/`
3. Cline reads rules automatically
4. Ask: "Run DevMind code review on this file"

---

## OpenCode

**Files generated:** `AGENTS.md`, `.opencode.json`

### Setup

```bash
# Install OpenCode
npm install -g opencode-ai

# Generate OpenCode config
cd /path/to/your/project
devmind document . -w -f opencode -p

# Start OpenCode
opencode
```

### Using OpenCode with DevMind

OpenCode reads `AGENTS.md`:

```bash
# In OpenCode session
"Run devmind scan to check for vulnerabilities"
"Generate documentation using devmind document"
"Create tests with devmind test"
```

---

## Windsurf

**Files generated:** `.windsurf/rules/*.md`

### Setup

```bash
# Generate Windsurf rules
cd /path/to/your/project
devmind document . -w -f windsurf -p

# Rules are in .windsurf/rules/
```

Windsurf uses these for project context and code style guidance.

---

## GitHub Spec Kit

**Files generated:** `.specify/memory/constitution.md`

### Setup

```bash
# Generate Spec Kit constitution
cd /path/to/your/project
devmind document . -w -f speckit -p

# File is at .specify/memory/constitution.md
```

---

## Using run-with Command

Run DevMind agents through other AI tools:

```bash
# List available tools
devmind tools

# Run through specific tool
devmind run-with gemini review src/main.py
devmind run-with aider scan .
devmind run-with claude document /path/to/project

# Preview command
devmind run-with opencode document . --dry-run
```

## Workflow: Onboard AI to New Project

```bash
# 1. Navigate to project
cd /path/to/project

# 2. Generate all AI documentation
devmind document . --all -w -p

# 3. Commit generated files
git add CLAUDE.md CONVENTIONS.md AGENTS.md \
        .github/ .gemini/ .cursor/ .windsurf/ .clinerules/
git commit -m "Add AI coding assistant documentation"

# 4. Now use any AI assistant - they all have project context
claude      # Reads CLAUDE.md
gemini      # Reads .gemini/GEMINI.md
aider       # Reads CONVENTIONS.md
opencode    # Reads AGENTS.md
```

## Best Practices

### Keep docs updated

```bash
# Re-generate after major changes
devmind document . -w --all -p
git add -A && git commit -m "Update AI docs"
```

### Use project-specific config

```yaml
# .devmind.yaml
document:
  formats:
    - claude
    - copilot
    - gemini
```

### CI/CD integration

```yaml
# .github/workflows/docs.yml
on:
  push:
    branches: [main]

jobs:
  update-ai-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install devmind-ai[cli]
      - run: devmind document . -w --all
      - uses: peter-evans/create-pull-request@v5
        with:
          title: "Update AI coding assistant docs"
```
