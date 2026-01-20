# DevMind-AI API Reference
**Last Updated:** 2026-01-20

Base URL: `http://localhost:8000`

---

## Health Endpoints

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "app": "DevMind AI"
}
```

### GET /ready
Readiness check with dependency status.

**Response:**
```json
{
  "status": "ready",
  "database": "connected",
  "redis": "connected"
}
```

---

## Code Review Endpoints

### POST /api/v1/reviews/review-file
Review a single file without GitHub integration.

**Request Body:**
```json
{
  "file_path": "string",     // Required: filename for context
  "content": "string",       // Required: full file content
  "diff": "string",          // Optional: unified diff
  "language": "string"       // Optional: language hint
}
```

**Response:**
```json
{
  "file_path": "example.py",
  "blocker_count": 1,
  "warning_count": 2,
  "suggestion_count": 3,
  "comments": [
    {
      "line_number": 10,
      "severity": "blocker|warning|suggestion|nit",
      "category": "security|performance|correctness|style|testing|documentation",
      "title": "Issue Title",
      "message": "Detailed description",
      "suggestion": "How to fix"
    }
  ]
}
```

---

### POST /api/v1/reviews/repos/{repo_id}/review
Trigger async PR review.

**Path Parameters:**
- `repo_id`: Repository UUID or full_name

**Request Body:**
```json
{
  "pr_number": 42,
  "reviewers": ["security", "performance"]  // Optional: filter reviewers
}
```

**Response (202 Accepted):**
```json
{
  "job_id": "uuid",
  "status": "queued",
  "pr_number": 42,
  "message": "Review queued for PR #42"
}
```

---

### GET /api/v1/reviews/jobs/{job_id}/status
Check async job status.

**Response:**
```json
{
  "job_id": "uuid",
  "status": "queued|running|completed|failed",
  "pr_number": 42,
  "created_at": "2026-01-20T10:00:00Z",
  "completed_at": "2026-01-20T10:01:30Z",
  "error": null
}
```

---

### GET /api/v1/reviews/repos/{repo_id}/reviews
List reviews for a repository.

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Results per page (default: 20, max: 100)

**Response:**
```json
{
  "reviews": [
    {
      "id": "uuid",
      "pr_number": 42,
      "status": "completed",
      "blocker_count": 1,
      "warning_count": 5,
      "suggestion_count": 12,
      "created_at": "2026-01-20T10:00:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 20
}
```

---

### GET /api/v1/reviews/reviews/{review_id}
Get detailed review results.

**Response:**
```json
{
  "id": "uuid",
  "pr_number": 42,
  "status": "completed",
  "blocker_count": 1,
  "warning_count": 5,
  "suggestion_count": 12,
  "created_at": "2026-01-20T10:00:00Z",
  "comments": [
    {
      "file_path": "src/auth.py",
      "line_number": 45,
      "severity": "blocker",
      "category": "security",
      "title": "SQL Injection",
      "message": "User input directly concatenated into query",
      "suggestion": "Use parameterized queries"
    }
  ]
}
```

---

## Security (VulnScanner) Endpoints

### POST /api/v1/security/{repo_id}/scan
Trigger vulnerability scan.

**Request Body:**
```json
{
  "commit_sha": "abc123",  // Optional: specific commit
  "full_scan": true        // Optional: include exploitability analysis
}
```

**Response (202 Accepted):**
```json
{
  "id": "uuid",
  "repo_id": "uuid",
  "status": "pending",
  "created_at": "2026-01-20T10:00:00Z"
}
```

---

### GET /api/v1/security/{repo_id}/vulns
List vulnerabilities.

**Query Parameters:**
- `severity`: Filter by `critical|high|medium|low`
- `status`: Filter by `open|fixed|ignored|false_positive` (default: open)
- `exploitable_only`: `true` to show only exploitable (default: false)
- `limit`: Max results (default: 100, max: 500)
- `offset`: Pagination offset

**Response:**
```json
[
  {
    "id": "uuid",
    "cve_id": "CVE-2023-12345",
    "package_name": "lodash",
    "package_version": "4.17.15",
    "severity": "high",
    "cvss_score": 7.5,
    "title": "Prototype Pollution",
    "fix_version": "4.17.21",
    "is_exploitable": true,
    "status": "open",
    "first_seen_at": "2026-01-20T10:00:00Z"
  }
]
```

---

### GET /api/v1/security/{repo_id}/summary
Get vulnerability summary counts.

**Response:**
```json
{
  "total": 15,
  "critical": 1,
  "high": 5,
  "medium": 7,
  "low": 2,
  "exploitable": 3
}
```

---

### PATCH /api/v1/security/vulns/{vuln_id}
Update vulnerability status.

**Request Body:**
```json
{
  "status": "ignored|false_positive|fixed",
  "ignored_reason": "Required when ignoring"
}
```

---

## Test Generation Endpoints

### POST /api/v1/tests/generate
Generate tests for code.

**Request Body:**
```json
{
  "code": "def add(a, b):\n    return a + b",
  "file_path": "math_utils.py",
  "framework": "pytest"  // Optional: pytest, unittest, jest
}
```

**Response:**
```json
{
  "tests": [
    {
      "name": "test_add_positive_numbers",
      "code": "def test_add_positive_numbers():\n    assert add(2, 3) == 5",
      "description": "Test addition of positive integers"
    }
  ],
  "test_file_content": "import pytest\nfrom math_utils import add\n\n...",
  "test_file_path": "tests/test_math_utils.py",
  "functions_analyzed": 1,
  "tests_generated": 5
}
```

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common Status Codes:**
- `400` - Bad request (invalid input)
- `401` - Unauthorized (missing/invalid auth)
- `404` - Resource not found
- `422` - Validation error
- `500` - Internal server error

---

## Authentication

> ⚠️ **Note:** Authentication is scaffolded but not fully enforced in development mode.

When enabled, include JWT token in header:
```
Authorization: Bearer <token>
```
