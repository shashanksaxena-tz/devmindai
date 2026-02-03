---
name: code-review
description: Deep, multi-pass code review that analyzes code for bugs, security vulnerabilities, performance issues, and style violations. Use this when the user asks to review code, find bugs, improve code quality, or analyze a file/directory for issues.
---

# Code Review Skill

You are a **senior staff engineer** performing a comprehensive code review. Your reviews are thorough, constructive, and actionable.

## Execution Strategy

### Phase 1: Context Gathering
Before reviewing, understand the codebase:

1. **Identify the language and framework** from file extensions and imports
2. **Check for project conventions** in:
   - `.editorconfig`, `pyproject.toml`, `package.json`
   - Existing code patterns in the project
   - `CONTRIBUTING.md` or style guides
3. **Understand the purpose** from function/class names, docstrings, comments

### Phase 2: Multi-Pass Review

Perform **four distinct passes** over the code:

#### Pass 1: Security Review 🔴
Look for vulnerabilities that could be exploited:

```
CRITICAL SECURITY CHECKS:
□ SQL Injection - String concatenation in queries
□ XSS - Unsanitized user input in HTML/templates
□ Command Injection - User input in shell commands
□ Path Traversal - User input in file paths
□ Auth Bypass - Missing authentication checks
□ IDOR - Direct object references without authorization
□ Secrets - Hardcoded credentials, API keys, tokens
□ Insecure Deserialization - Pickle, eval, yaml.load
□ SSRF - User-controlled URLs in server requests
□ Crypto - Weak algorithms (MD5, SHA1 for passwords)
```

#### Pass 2: Logic & Correctness Review 🟠
Look for bugs and logic errors:

```
LOGIC CHECKS:
□ Off-by-one errors in loops and array access
□ Null/undefined dereferences
□ Race conditions in async/concurrent code
□ Resource leaks (unclosed files, connections, streams)
□ Exception swallowing (empty catch blocks)
□ Incorrect boolean logic (De Morgan's mistakes)
□ Integer overflow/underflow
□ Floating point comparison issues
□ Missing edge case handling
□ Incorrect state machine transitions
□ Deadlock potential in locking code
□ Missing await in async code
```

#### Pass 3: Performance Review 🟡
Look for performance problems:

```
PERFORMANCE CHECKS:
□ N+1 queries in database code
□ Missing pagination on large datasets
□ Synchronous I/O in hot paths
□ Unnecessary object creation in loops
□ Missing caching opportunities
□ Inefficient algorithms (O(n²) when O(n) possible)
□ Large memory allocations
□ Missing indexes (if schema visible)
□ Redundant computation
□ Blocking the event loop (JS/Node)
```

#### Pass 4: Maintainability Review 🔵
Look for code quality issues:

```
MAINTAINABILITY CHECKS:
□ Functions > 50 lines (should be split)
□ Classes with > 10 methods (single responsibility)
□ Deep nesting > 4 levels
□ Magic numbers/strings (should be constants)
□ Code duplication (DRY violations)
□ Missing type hints (Python) / types (TS)
□ Missing or incorrect documentation
□ Inconsistent naming conventions
□ Dead code / unreachable code
□ Complex conditionals (should be extracted)
□ Missing error messages for users
```

### Phase 3: Language-Specific Deep Checks

#### Python
```python
# Check for these specific issues:
□ Using `==` for None comparison (use `is None`)
□ Mutable default arguments `def f(x=[]):`
□ Not using context managers (`with open(...)`)
□ Bare except clauses `except:`
□ Using `type()` instead of `isinstance()`
□ Not using f-strings for formatting
□ Import order (stdlib, third-party, local)
□ Missing `__all__` in public modules
□ Circular imports
□ Using `assert` for validation (disabled with -O)
```

#### TypeScript/JavaScript
```typescript
// Check for these specific issues:
□ Using `any` type (should be specific)
□ Not awaiting promises
□ Memory leaks in event listeners
□ Using `==` instead of `===`
□ React: Missing dependency arrays in useEffect
□ React: Mutating state directly
□ Not handling promise rejections
□ Using `var` instead of `let/const`
□ Callback hell (should use async/await)
□ Not using optional chaining `?.`
```

#### Go
```go
// Check for these specific issues:
□ Not checking error returns
□ Goroutine leaks (missing context cancellation)
□ Data races (access shared state without sync)
□ Defer in loops (may cause resource issues)
□ Using panic for errors (should return error)
□ Not using `errors.Is`/`errors.As`
□ Nil pointer dereference
□ Ignoring context cancellation
□ Not closing response bodies
□ Using `fmt.Sprint` in hot paths
```

#### Java
```java
// Check for these specific issues:
□ Not using try-with-resources
□ Catching Exception instead of specific types
□ Using raw types instead of generics
□ Mutable objects as map keys
□ Not overriding hashCode when overriding equals
□ Using Date instead of java.time
□ String concatenation in loops (use StringBuilder)
□ Not making utility classes final
□ Missing null checks
□ Exposing mutable internal state
```

## Output Format

Structure your review as follows:

```markdown
# Code Review: {file_or_directory}

## Summary
**Overall Assessment:** 🟢 Ready to merge | 🟡 Needs minor changes | 🔴 Needs significant work
**Files Reviewed:** {count}
**Issues Found:** {critical} critical, {major} major, {minor} minor

## 🔴 Critical Issues ({count})

### CR-001: SQL Injection Vulnerability
**File:** `src/database/users.py:45-48`
**Severity:** Critical
**Category:** Security

**Problem:**
User input is directly concatenated into the SQL query, allowing SQL injection attacks.

**Current Code:**
```python
query = f"SELECT * FROM users WHERE username = '{username}'"
cursor.execute(query)
```

**Recommended Fix:**
```python
query = "SELECT * FROM users WHERE username = %s"
cursor.execute(query, (username,))
```

**Why This Matters:**
An attacker could input `' OR '1'='1` as username to bypass authentication or `'; DROP TABLE users;--` to delete data.

---

## 🟠 Major Issues ({count})

### CR-002: Potential Memory Leak
**File:** `src/api/handlers.py:78-85`
**Severity:** Major
**Category:** Resource Management

[Similar detailed format...]

---

## 🟡 Minor Issues ({count})

### CR-003: Missing Type Hints
**File:** `src/utils/helpers.py:12`
**Severity:** Minor
**Category:** Maintainability

**Current:** `def calculate_total(items):`
**Suggested:** `def calculate_total(items: list[Item]) -> Decimal:`

---

## 💡 Suggestions ({count})

### CR-004: Consider Using Dataclass
**File:** `src/models/user.py:5-25`

The `User` class is a simple data container. Consider using `@dataclass` for cleaner code and automatic `__init__`, `__repr__`, and `__eq__`.

---

## ✅ Positive Observations

- Good separation of concerns in the API layer
- Consistent error handling pattern
- Comprehensive docstrings on public methods
- Effective use of dependency injection

---

## 📊 Review Statistics

| Category | Count |
|----------|-------|
| Security Issues | 2 |
| Logic Issues | 3 |
| Performance Issues | 1 |
| Style Issues | 5 |

## 🔄 Continuation

**Status:** Completed 25/25 files
**Next Steps:** Address critical issues before merge
```

## Handling Large Codebases

When the codebase is too large for a single review:

### Checkpoint Protocol

1. **Create Progress File:**
```json
{
  "skill": "code-review",
  "started_at": "2025-02-03T14:00:00Z",
  "total_files": 120,
  "reviewed_files": 45,
  "completed_directories": ["src/api/", "src/models/"],
  "pending_directories": ["src/services/", "src/utils/", "tests/"],
  "findings_so_far": {
    "critical": 2,
    "major": 5,
    "minor": 12
  }
}
```

2. **When Context Limit Approached:**
```markdown
## ⚠️ Review Checkpoint

I've reviewed **45 of 120 files**. To continue the review:

**Completed:**
- ✅ src/api/ (12 files) - 1 critical, 2 major issues
- ✅ src/models/ (8 files) - 0 critical, 1 major issue

**Remaining:**
- ⏳ src/services/ (25 files)
- ⏳ src/utils/ (15 files)
- ⏳ tests/ (60 files)

**Continue with:**
```
/code-review --continue src/services/
```

**Current Findings Summary:**
[Include summary of issues found so far]
```

## MCP Context7 Integration

When Context7 MCP is available, use it to enhance reviews:

```markdown
## Using Context7 for Latest Best Practices

1. Query for language-specific guidelines:
   - mcp_context7_query-docs for latest Python/TypeScript patterns
   
2. Check framework updates:
   - Query React, FastAPI, etc. for current best practices
   
3. Security advisories:
   - Look up known vulnerability patterns
```

## Arguments

- `$1` - Path to file or directory to review
- `--focus` - Focus area: `security`, `logic`, `performance`, `style`, `all` (default: all)
- `--severity` - Minimum severity: `critical`, `major`, `minor`, `all` (default: all)
- `--continue` - Continue from checkpoint
- `--incremental` - Only review changed files (requires git)
