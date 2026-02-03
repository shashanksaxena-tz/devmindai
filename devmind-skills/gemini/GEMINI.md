# GEMINI.md

Project context for Gemini CLI.

## Quick Reference

| Command | Description |
|---------|-------------|
| `/review` | Deep code review |
| `/scan` | Security scan |
| `/test` | Generate tests |
| `/docs` | Generate documentation |
| `/pr` | PR review |
| `/folder-docs` | Per-folder docs |

## Code Conventions

### General (All Languages)
- Use type hints/annotations where available
- Document public APIs (docstrings, Javadoc, JSDoc, XML comments)
- Handle errors explicitly
- Never hardcode secrets
- Validate all user input

### Language-Specific Best Practices
**Java/C#**
- Use explicit generics: `List<User>` not `List`
- Follow SOLID principles
- Use dependency injection

**Python**
- Use `is None` not `== None`
- No mutable default arguments
- Use context managers (`with`)

**TypeScript/JavaScript**
- Avoid `any` type
- Use `===` not `==`
- Include React hook dependencies

**Go**
- Always check error returns
- Use defer for cleanup
- Export only what's needed

## Security Guidelines

- Never log sensitive data
- Use parameterized queries
- Validate all user input
- Check authorization on all endpoints
- Use secure defaults

## Project Structure

Understand the project by examining:
- `README.md` - Overview
- `pyproject.toml` / `package.json` - Dependencies
- `src/` - Main source code
- `tests/` - Test suite

## MCP Integration

Use Context7 MCP for:
- Latest CVE database
- Current framework documentation
- Best practices updates

## Continuation Protocol

For large projects:

```markdown
## ⚠️ Context Limit

Processed: {X}/{Y} items
Checkpoint saved.

Continue: `/command --continue`
```
