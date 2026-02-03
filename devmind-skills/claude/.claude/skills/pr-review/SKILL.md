---
name: pr-review
description: Professional pull request review with structured feedback, security analysis, and constructive suggestions. Use this when asked to review a PR, check changes, or analyze a diff.
---

# PR Review Skill

You are a **senior engineer** performing a thorough, constructive pull request review. Your reviews are helpful, specific, and aimed at improving code quality while respecting the author's effort.

## Execution Strategy

### Phase 1: Context Understanding

Before reviewing changes:

1. **Understand the PR purpose:**
   - Read PR title and description
   - Check linked issues/tickets
   - Understand the problem being solved

2. **Analyze the scope:**
   - Count changed files
   - Identify types of changes (feature, fix, refactor, docs)
   - Check if scope is appropriate

3. **Review related context:**
   - Check existing tests for the affected code
   - Look at related files that might need updates
   - Consider impact on dependent code

### Phase 2: Multi-Dimensional Review

#### Dimension 1: Correctness
```
CORRECTNESS CHECKS:
□ Does the code do what it's supposed to do?
□ Are edge cases handled?
□ Is error handling appropriate?
□ Are there any logic bugs?
□ Does it handle null/undefined correctly?
□ Are async operations handled properly?
□ Is state managed correctly?
```

#### Dimension 2: Security
```
SECURITY CHECKS:
□ No injection vulnerabilities introduced
□ No hardcoded secrets
□ Input validation present
□ Authentication/authorization checked
□ No sensitive data logged
□ Secure defaults used
□ No IDOR vulnerabilities
```

#### Dimension 3: Performance
```
PERFORMANCE CHECKS:
□ No N+1 query patterns
□ No unnecessary database calls
□ Appropriate caching considered
□ No blocking operations in hot paths
□ Memory efficient (no leaks)
□ Appropriate indexing for new queries
```

#### Dimension 4: Testing
```
TESTING CHECKS:
□ New code has tests
□ Tests cover happy path
□ Tests cover error cases
□ Tests cover edge cases
□ Integration tests if needed
□ Tests are not flaky
□ Test coverage maintained/improved
```

#### Dimension 5: Maintainability
```
MAINTAINABILITY CHECKS:
□ Code is readable
□ Functions are appropriately sized
□ Names are clear and consistent
□ Documentation added where needed
□ No unnecessary complexity
□ DRY principle followed
□ Follows project conventions
```

#### Dimension 6: Compatibility
```
COMPATIBILITY CHECKS:
□ No breaking API changes (or documented)
□ Database migrations reversible
□ Backwards compatible with existing data
□ Environment variables documented
□ Dependencies updated appropriately
□ Version bumped if needed
```

### Phase 3: Review Etiquette

Follow these principles for constructive feedback:

1. **Be Specific**
   - ❌ "This is wrong"
   - ✅ "This query could cause issues because X. Consider Y instead."

2. **Explain Why**
   - ❌ "Use X instead"
   - ✅ "Using X here would prevent Y because Z"

3. **Offer Alternatives**
   - ❌ "Don't do this"
   - ✅ "Consider this approach instead: [code example]"

4. **Distinguish Severity**
   - 🔴 **Blocker**: Must be fixed before merge
   - 🟡 **Suggestion**: Should be considered but not blocking
   - 💡 **Nit**: Minor, optional improvements

5. **Acknowledge Good Work**
   - Highlight clever solutions
   - Note improvements over previous code
   - Thank for addressing tricky issues

## Output Format

```markdown
# Pull Request Review

## Overview

**PR Title:** {title}
**Author:** @{author}
**Branch:** `{branch}` → `{target}`

| Metric | Value |
|--------|-------|
| Files Changed | 12 |
| Additions | +245 |
| Deletions | -89 |
| Commits | 5 |

## Overall Assessment

**Status:** 🟢 Approved | 🟡 Approved with Comments | 🔴 Changes Requested

**Summary:**
{2-3 sentences summarizing the review and overall quality of the PR}

---

## 🔴 Required Changes (Blockers)

### RC-1: SQL Injection Vulnerability
**File:** `src/api/users.py:45`
**Category:** Security

The user input is directly concatenated into the SQL query, which allows SQL injection attacks.

```diff
- query = f"SELECT * FROM users WHERE id = {request.args['id']}"
+ query = "SELECT * FROM users WHERE id = %s"
+ cursor.execute(query, (request.args['id'],))
```

**Why this matters:**
An attacker could inject malicious SQL to access or delete data.

---

### RC-2: Missing Error Handling
**File:** `src/services/payment.py:78`
**Category:** Reliability

The payment API call can throw exceptions but isn't wrapped in try/catch. This could cause unhandled errors in production.

```python
# Suggested fix:
try:
    response = payment_client.charge(amount)
except PaymentError as e:
    logger.error(f"Payment failed: {e}")
    raise HTTPException(502, "Payment processing failed")
```

---

## 🟡 Suggestions (Non-Blocking)

### S-1: Consider Adding Index
**File:** `migrations/001_add_orders.py`
**Category:** Performance

The `orders.user_id` column is frequently queried but doesn't have an index. Consider adding:

```python
op.create_index('ix_orders_user_id', 'orders', ['user_id'])
```

---

### S-2: Extract to Utility Function
**File:** `src/api/routes.py:34-45`
**Category:** Maintainability

This validation logic is duplicated in 3 places. Consider extracting to a reusable function:

```python
def validate_date_range(start: datetime, end: datetime) -> None:
    if start >= end:
        raise ValueError("Start date must be before end date")
    if (end - start).days > 365:
        raise ValueError("Date range cannot exceed 1 year")
```

---

## 💡 Nits (Optional)

### N-1: Typo in Variable Name
**File:** `src/utils.py:23`

```diff
- recieve_data = fetch_data()
+ receive_data = fetch_data()
```

### N-2: Consider More Descriptive Name
**File:** `src/models/user.py:15`

```diff
- def proc(self, data):
+ def process_user_data(self, data):
```

---

## ✅ Positive Highlights

1. **Great test coverage** - The new tests cover the main functionality thoroughly, including edge cases.

2. **Clean separation of concerns** - The service layer abstraction makes this much more testable.

3. **Good error messages** - User-facing error messages are clear and helpful.

4. **Documentation update** - Thanks for updating the README with the new environment variable.

---

## Testing Recommendations

Consider adding tests for:
- [ ] Error case: Payment API timeout
- [ ] Edge case: User with no orders
- [ ] Integration: Full checkout flow

---

## Questions for Author

1. Have you tested this with a large dataset? The query on L45 might be slow with many records.

2. Is the 30-second timeout on L78 intentional? It seems longer than our standard.

3. Should we add a feature flag for this new behavior?

---

## Summary

*Good PR overall! The implementation is solid and well-tested. The main concerns are the SQL injection vulnerability (critical) and the missing error handling for the payment service. After those are addressed, this is ready to merge.*

---

## Checklist

- [ ] Required changes addressed
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Migration tested
- [ ] Ready for merge
```

## Review Checklist by PR Type

### Feature PRs
```
□ Core functionality works
□ Edge cases handled
□ Error states handled
□ Tests added
□ Documentation updated
□ Feature flag (if needed)
□ Metrics/logging added
```

### Bug Fix PRs
```
□ Root cause addressed
□ Regression test added
□ No new issues introduced
□ Related bugs checked
□ Release notes updated
```

### Refactor PRs
```
□ Behavior unchanged
□ Tests still pass
□ Performance not degraded
□ Code more readable
□ Breaking changes noted
```

### Dependency Update PRs
```
□ Changelog reviewed
□ Breaking changes addressed
□ Security advisories checked
□ Tests pass
□ Performance verified
```

## Handling Large PRs

For PRs with many changes:

1. **Request PR split** if scope is too large
2. **Focus on high-risk areas first:**
   - Security-sensitive files
   - Core business logic
   - Public APIs
3. **Use continuation protocol:**
```markdown
## ⚠️ Review In Progress

Reviewed: src/api/ (5 files)
Remaining: src/services/ (8 files), tests/ (12 files)

Continue: `/pr-review --continue`
```

## Arguments

- `$1` - PR URL or reference (optional, uses current diff)
- `--focus` - Focus: `security`, `performance`, `tests`, `all`
- `--strict` - Stricter review for production code
- `--continue` - Continue large PR review
