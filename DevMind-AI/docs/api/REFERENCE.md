# API Reference

Complete endpoint documentation for DevMind API.

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
      "severity": "blocker",
      "category": "security",
      "title": "Issue Title",
      "message": "Detailed description",
      "suggestion": "How to fix"
    }
  ]
}
```

**Severity levels:** `blocker`, `warning`, `suggestion`, `nit`

**Categories:** `security`, `performance`, `correctness`, `style`, `testing`, `documentation`

---

### POST /api/v1/reviews/repos/{repo_id}/review

Trigger async PR review.

**Path Parameters:**
- `repo_id` - Repository UUID or full_name

**Request Body:**
```json
{
  "pr_number": 42,
  "reviewers": ["security", "performance"]  // Optional
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
  "status": "completed",
  "pr_number": 42,
  "created_at": "2026-01-20T10:00:00Z",
  "completed_at": "2026-01-20T10:01:30Z",
  "error": null
}
```

**Status values:** `queued`, `running`, `completed`, `failed`

---

### GET /api/v1/reviews/repos/{repo_id}/reviews

List reviews for a repository.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `page_size` | int | 20 | Results per page (max 100) |

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

## Security Endpoints

### POST /api/v1/security/{repo_id}/scan

Trigger vulnerability scan.

**Request Body:**
```json
{
  "commit_sha": "abc123",  // Optional
  "full_scan": true        // Optional: include exploitability
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
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `severity` | string | - | Filter: `critical`, `high`, `medium`, `low` |
| `status` | string | open | Filter: `open`, `fixed`, `ignored`, `false_positive` |
| `exploitable_only` | bool | false | Only exploitable |
| `limit` | int | 100 | Max results (max 500) |
| `offset` | int | 0 | Pagination offset |

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

Get vulnerability summary.

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
  "status": "ignored",
  "ignored_reason": "Not applicable to our usage"
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

## Project Documentation Endpoints

### POST /api/v1/project-docs/analyze

Analyze project structure.

**Request Body:**
```json
{
  "path": "/path/to/project"
}
```

**Response:**
```json
{
  "name": "my-project",
  "languages": ["python", "typescript"],
  "frameworks": ["fastapi", "react"],
  "build_commands": ["pip install -e .", "npm install"],
  "test_commands": ["pytest", "npm test"],
  "entry_points": ["src/main.py", "src/index.ts"],
  "structure": {...}
}
```

---

### POST /api/v1/project-docs/generate

Generate documentation.

**Request Body:**
```json
{
  "path": "/path/to/project",
  "formats": ["claude", "copilot", "gemini"],
  "write_files": true,
  "output_dir": "devmind-output"
}
```

**Response:**
```json
{
  "formats_generated": ["claude", "copilot", "gemini"],
  "output_dir": "/path/to/project/devmind-output/project-documenter/...",
  "files": [
    "claude/CLAUDE.md",
    "copilot/copilot-instructions.md",
    "gemini/GEMINI.md"
  ]
}
```

---

### GET /api/v1/project-docs/formats

List available formats.

**Response:**
```json
{
  "formats": [
    {
      "id": "claude",
      "name": "Claude Code",
      "output_files": ["CLAUDE.md"]
    },
    {
      "id": "copilot",
      "name": "GitHub Copilot",
      "output_files": [".github/copilot-instructions.md"]
    }
  ]
}
```

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "detail": "Error message"
}
```

### Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 202 | Accepted (async job queued) |
| 400 | Bad request (invalid input) |
| 401 | Unauthorized |
| 404 | Not found |
| 422 | Validation error |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

---

## Authentication

> Authentication is scaffolded but not enforced in development mode.

When enabled:

```
Authorization: Bearer <token>
```

### Get Token

```bash
POST /api/v1/auth/token
Content-Type: application/x-www-form-urlencoded

username=user&password=pass
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```
