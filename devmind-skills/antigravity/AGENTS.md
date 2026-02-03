# AGENTS.md

Instructions for AI coding agents in Antigravity IDE.

## Available Skills

Skills are located in `.agent/skills/`. Each skill folder contains a `SKILL.md` file.

| Skill | Command | Description |
|-------|---------|-------------|
| code-review | `/code-review` | Deep multi-pass code review |
| security-scan | `/security-scan` | OWASP Top 10 vulnerability scan |
| test-generator | `/generate-tests` | Comprehensive test generation |
| document-project | `/document-project` | AI-ready documentation |
| pr-review | `/pr-review` | Pull request review |
| per-folder-docs | `/per-folder-docs` | Module documentation |

## Usage

```
/code-review src/api/
/security-scan src/ --focus injection
/generate-tests src/models/user.py
/document-project
/pr-review
/per-folder-docs src/services/
```

## Skill Details

See individual `SKILL.md` files in `.agent/skills/` for comprehensive instructions.

## MCP Integration

These skills can use MCP Context7 for:
- Latest CVE lookups
- Current framework documentation
- Best practices updates

## Continuation Protocol

For large projects, skills support chunked processing:

```markdown
## ⚠️ Context Limit Reached

Processed: {X}/{Y} items

To continue:
/skill-name --continue
```

## Code Conventions

- Always use type hints
- Write docstrings for public API
- Handle errors explicitly
- Never hardcode secrets
- Validate all user input
