# DevMind AI Skills

**Production-ready AI coding skills for Claude Code, Cursor, GitHub Copilot, OpenCode, Gemini CLI, and Antigravity.**

These skills enable your AI coding assistant to perform professional-grade code review, security scanning, test generation, documentation, and more — **using the editor's built-in LLM, no external API keys required**.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Available Skills](#-available-skills)
- [Editor-Specific Installation](#-editor-specific-installation)
- [Handling Large Repositories](#-handling-large-repositories)
- [MCP Context7 Integration](#-mcp-context7-integration)
- [LLM Recommendations](#-llm-recommendations)

---

## 🚀 Quick Start

### Universal Installer

```bash
# Clone this repository
git clone https://github.com/your-org/devmind-skills.git

# Navigate to skills folder
cd devmind-skills

# Install for your editor (run from your project root)
./install.sh /path/to/your/project --editor <editor>

# Or install all editor configs
./install.sh /path/to/your/project --all
```

### Supported Editors

| Editor | Flag | Skills Location |
|--------|------|-----------------|
| Claude Code | `--claude` | `.claude/skills/` |
| Cursor | `--cursor` | `.cursor/rules/` |
| GitHub Copilot | `--copilot` | `.github/` + `AGENTS.md` |
| OpenCode | `--opencode` | `.opencode/commands/` + `AGENTS.md` |
| Gemini CLI | `--gemini` | `GEMINI.md` + `.gemini/commands/` |
| Antigravity | `--antigravity` | `.agent/skills/` + `AGENTS.md` |

---

## 📦 Available Skills

### 1. Code Review (`/code-review`)
**Deep, multi-pass code analysis** that catches bugs, security issues, performance problems, and style violations.

**Features:**
- Multi-pass review (security → logic → performance → style)
- Language-specific checks (Python, TypeScript, Go, Rust, Java)
- Severity-based prioritization (Critical → Major → Minor → Suggestions)
- Actionable fix suggestions with code examples

### 2. Security Scanner (`/security-scan`)
**OWASP Top 10 compliant** vulnerability detection with CVE references and remediation guidance.

**Features:**
- Secret detection (API keys, passwords, tokens)
- Injection vulnerability detection (SQL, XSS, Command)
- Dependency vulnerability checking
- CWE/CVE references for all findings
- OWASP Top 10 2021 checklist

### 3. Test Generator (`/generate-tests`)
**Comprehensive unit test generation** with edge cases, mocks, and assertions tailored to your framework.

**Features:**
- Framework auto-detection (pytest, Jest, Vitest, Go testing)
- Happy path + edge case + error case coverage
- Mock generation for dependencies
- Parameterized tests for multiple scenarios
- Coverage goal targeting

### 4. Documentation Generator (`/document-project`)
**AI-ready project documentation** that creates context files for all major AI assistants.

**Features:**
- Generates CLAUDE.md, AGENTS.md, GEMINI.md
- Creates comprehensive README.md
- Architecture documentation with diagrams
- API endpoint documentation
- Multi-format output (markdown, RST)

### 5. PR Review (`/pr-review`)
**Professional pull request reviews** with structured feedback and actionable suggestions.

**Features:**
- Diff-aware analysis
- Change impact assessment
- Breaking change detection
- Test coverage evaluation
- Constructive feedback format

### 6. Per-Folder Documentation (`/per-folder-docs`)
**Module-level documentation** that creates AI-CONTEXT.md and README.md for each code folder.

**Features:**
- Smart folder detection and prioritization
- Custom section preservation during regeneration
- Incremental update support
- Cross-reference generation

---

## 📁 Editor-Specific Installation

### Claude Code

```bash
# Copy Claude skills to your project
cp -r devmind-skills/claude/.claude /path/to/your/project/

# Usage
/code-review src/api/
/security-scan --focus injection src/
/generate-tests src/utils.py
```

**Structure:**
```
your-project/
└── .claude/
    └── skills/
        ├── code-review/
        │   └── SKILL.md
        ├── security-scan/
        │   └── SKILL.md
        └── ...
```

### Cursor AI

```bash
# Copy Cursor rules to your project
cp -r devmind-skills/cursor/.cursor /path/to/your/project/

# Usage
# Rules are auto-applied based on file patterns
# Or reference directly: @code-review analyze this file
```

**Structure:**
```
your-project/
└── .cursor/
    └── rules/
        ├── code-review.mdc
        ├── security-scan.mdc
        └── ...
```

### GitHub Copilot

```bash
# Copy Copilot config to your project
cp -r devmind-skills/copilot/.github /path/to/your/project/
cp devmind-skills/copilot/AGENTS.md /path/to/your/project/

# Usage
# In Copilot Chat: @workspace Review this code for security issues
# Or: @workspace Generate tests for this function
```

**Structure:**
```
your-project/
├── AGENTS.md
└── .github/
    ├── copilot-instructions.md
    └── instructions/
        ├── code-review.instructions.md
        ├── security-scan.instructions.md
        └── ...
```

### OpenCode

```bash
# Copy OpenCode config to your project
cp devmind-skills/opencode/AGENTS.md /path/to/your/project/
cp -r devmind-skills/opencode/.opencode /path/to/your/project/

# Usage
/review src/
/scan src/
/test src/utils.py
```

**Structure:**
```
your-project/
├── AGENTS.md
└── .opencode/
    └── commands/
        ├── review.md
        ├── scan.md
        └── ...
```

### Gemini CLI

```bash
# Copy Gemini config to your project
cp devmind-skills/gemini/GEMINI.md /path/to/your/project/
cp -r devmind-skills/gemini/.gemini /path/to/your/project/

# Usage
/review src/
/scan src/
/test src/utils.py
```

**Structure:**
```
your-project/
├── GEMINI.md
└── .gemini/
    └── commands/
        ├── review.toml
        ├── scan.toml
        └── ...
```

### Antigravity

```bash
# Copy Antigravity config to your project
cp devmind-skills/antigravity/AGENTS.md /path/to/your/project/
cp -r devmind-skills/antigravity/.agent /path/to/your/project/

# Usage
/code-review src/
/security-scan src/
/generate-tests src/utils.py
```

**Structure:**
```
your-project/
├── AGENTS.md
└── .agent/
    └── skills/
        ├── code-review/
        │   └── SKILL.md
        └── ...
```

---

## 📊 Handling Large Repositories

When working with large codebases that exceed context window limits, these skills support **chunked processing with handoff**:

### Continuation Protocol

Each skill implements a continuation protocol for large projects:

1. **Initial Analysis** - Skill analyzes structure, identifies scope
2. **Chunked Processing** - Works on manageable chunks
3. **Progress Tracking** - Saves state to `.devmind/progress.json`
4. **Handoff Prompt** - Provides continuation command when limit reached

**Example Handoff:**
```markdown
## ⚠️ Context Limit Reached

Processed 45/120 files. To continue:

```
/code-review --continue --from-checkpoint .devmind/progress.json
```

**Completed:** src/api/, src/models/
**Remaining:** src/services/, src/utils/, tests/
```

### Chunking Strategies

| Strategy | Use Case |
|----------|----------|
| **By Directory** | Large monorepos, clear module boundaries |
| **By File Count** | Many small files |
| **By Priority** | Focus on high-risk areas first |
| **Incremental** | Only changed files since last run |

---

## 🔌 MCP Context7 Integration

These skills can integrate with **MCP Context7** to fetch the latest documentation, vulnerability databases, and best practices.

### Enabling Context7

When available, skills will automatically use Context7 for:

- **Security Scan**: Latest CVE database, OWASP updates
- **Code Review**: Current language/framework best practices
- **Test Generation**: Framework-specific testing patterns
- **Documentation**: Library documentation lookups

### Usage with Context7

```markdown
# In your skill invocation
/security-scan src/ --use-context7

# The skill will:
# 1. Query Context7 for latest vulnerability patterns
# 2. Check dependencies against CVE database
# 3. Fetch current OWASP guidelines
```

---

## 🎯 LLM Recommendations

| Skill | Best Models | Reasoning |
|-------|-------------|-----------|
| **Code Review** | Claude Sonnet 4, GPT-4o, Gemini Pro | Deep semantic understanding needed |
| **Security Scan** | Claude Sonnet 4, GPT-4o | Security expertise and CVE knowledge |
| **Test Generation** | Claude Sonnet 4, GPT-4o | Complex test scenario generation |
| **Documentation** | Gemini Flash, Claude Haiku | Speed, good at summarization |
| **PR Review** | Claude Sonnet 4 | Context understanding critical |
| **Per-Folder Docs** | Gemini Flash, Claude Haiku | Fast iteration, clear output |

---

## 📄 License

MIT License - Use these skills in any project!

---

## 🤝 Contributing

1. Fork this repository
2. Add/improve skills in the universal `skills/` folder
3. Run `./build.sh` to generate editor-specific formats
4. Submit a pull request
