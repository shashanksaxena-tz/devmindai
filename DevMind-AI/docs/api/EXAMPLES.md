# API Examples

Practical examples for using the DevMind API.

## Setup

```bash
# Start the API server
uvicorn src.api.main:app --reload --port 8000

# Or with Docker
docker-compose up -d
```

Base URL: `http://localhost:8000`

---

## Code Review

### Review a Python File

```bash
curl -X POST http://localhost:8000/api/v1/reviews/review-file \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "auth.py",
    "content": "import os\nimport hashlib\n\ndef check_password(password, stored_hash):\n    # Check if password matches\n    return hashlib.md5(password.encode()).hexdigest() == stored_hash\n\ndef get_user(user_id):\n    query = f\"SELECT * FROM users WHERE id = {user_id}\"\n    return db.execute(query)"
  }'
```

**Response:**
```json
{
  "file_path": "auth.py",
  "blocker_count": 2,
  "warning_count": 1,
  "suggestion_count": 0,
  "comments": [
    {
      "line_number": 5,
      "severity": "blocker",
      "category": "security",
      "title": "Weak hashing algorithm",
      "message": "MD5 is cryptographically broken and should not be used for password hashing",
      "suggestion": "Use bcrypt or argon2 for password hashing"
    },
    {
      "line_number": 8,
      "severity": "blocker",
      "category": "security",
      "title": "SQL Injection",
      "message": "User input is directly interpolated into SQL query",
      "suggestion": "Use parameterized queries: db.execute('SELECT * FROM users WHERE id = ?', [user_id])"
    }
  ]
}
```

### Review with Diff Context

```bash
curl -X POST http://localhost:8000/api/v1/reviews/review-file \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "utils.py",
    "content": "def process_data(data):\n    return data.strip().lower()",
    "diff": "@@ -1,3 +1,2 @@\n def process_data(data):\n-    return data\n+    return data.strip().lower()",
    "language": "python"
  }'
```

---

## Security Scanning

### Scan a Repository

```bash
# Trigger scan
curl -X POST http://localhost:8000/api/v1/security/repo-123/scan \
  -H "Content-Type: application/json" \
  -d '{"full_scan": true}'
```

**Response:**
```json
{
  "id": "scan-456",
  "repo_id": "repo-123",
  "status": "pending",
  "created_at": "2026-01-30T10:00:00Z"
}
```

### Get Vulnerabilities

```bash
# All vulnerabilities
curl "http://localhost:8000/api/v1/security/repo-123/vulns"

# Critical and high only
curl "http://localhost:8000/api/v1/security/repo-123/vulns?severity=critical&severity=high"

# Only exploitable
curl "http://localhost:8000/api/v1/security/repo-123/vulns?exploitable_only=true"
```

### Get Summary

```bash
curl "http://localhost:8000/api/v1/security/repo-123/summary"
```

**Response:**
```json
{
  "total": 12,
  "critical": 1,
  "high": 3,
  "medium": 5,
  "low": 3,
  "exploitable": 2
}
```

### Mark as False Positive

```bash
curl -X PATCH http://localhost:8000/api/v1/security/vulns/vuln-789 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "false_positive",
    "ignored_reason": "This code path is not reachable in production"
  }'
```

---

## Test Generation

### Generate Python Tests

```bash
curl -X POST http://localhost:8000/api/v1/tests/generate \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def calculate_total(items):\n    return sum(item[\"price\"] * item[\"quantity\"] for item in items)\n\ndef apply_discount(total, discount_percent):\n    if discount_percent < 0 or discount_percent > 100:\n        raise ValueError(\"Invalid discount\")\n    return total * (1 - discount_percent / 100)",
    "file_path": "pricing.py",
    "framework": "pytest"
  }'
```

**Response:**
```json
{
  "tests": [
    {
      "name": "test_calculate_total_single_item",
      "code": "def test_calculate_total_single_item():\n    items = [{\"price\": 10, \"quantity\": 2}]\n    assert calculate_total(items) == 20",
      "description": "Test total calculation with single item"
    },
    {
      "name": "test_calculate_total_empty",
      "code": "def test_calculate_total_empty():\n    assert calculate_total([]) == 0",
      "description": "Test total calculation with empty list"
    },
    {
      "name": "test_apply_discount_valid",
      "code": "def test_apply_discount_valid():\n    assert apply_discount(100, 20) == 80",
      "description": "Test valid discount application"
    },
    {
      "name": "test_apply_discount_invalid_negative",
      "code": "def test_apply_discount_invalid_negative():\n    with pytest.raises(ValueError):\n        apply_discount(100, -10)",
      "description": "Test that negative discount raises error"
    }
  ],
  "test_file_content": "import pytest\nfrom pricing import calculate_total, apply_discount\n\n...",
  "test_file_path": "tests/test_pricing.py",
  "functions_analyzed": 2,
  "tests_generated": 8
}
```

### Generate Jest Tests

```bash
curl -X POST http://localhost:8000/api/v1/tests/generate \
  -H "Content-Type: application/json" \
  -d '{
    "code": "export function formatCurrency(amount, currency = \"USD\") {\n  return new Intl.NumberFormat(\"en-US\", {\n    style: \"currency\",\n    currency\n  }).format(amount);\n}",
    "file_path": "utils.js",
    "framework": "jest"
  }'
```

---

## Project Documentation

### Analyze Project

```bash
curl -X POST http://localhost:8000/api/v1/project-docs/analyze \
  -H "Content-Type: application/json" \
  -d '{"path": "/home/user/my-project"}'
```

**Response:**
```json
{
  "name": "my-project",
  "languages": ["python", "javascript"],
  "frameworks": ["fastapi", "react"],
  "build_commands": [
    "pip install -e .",
    "npm install"
  ],
  "test_commands": [
    "pytest tests/",
    "npm test"
  ],
  "lint_commands": [
    "ruff check .",
    "eslint src/"
  ],
  "entry_points": [
    "src/main.py",
    "frontend/src/index.tsx"
  ],
  "structure": {
    "type": "monorepo",
    "packages": ["backend", "frontend"]
  }
}
```

### Generate Documentation

```bash
curl -X POST http://localhost:8000/api/v1/project-docs/generate \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/home/user/my-project",
    "formats": ["claude", "copilot", "gemini"],
    "write_files": true
  }'
```

**Response:**
```json
{
  "formats_generated": ["claude", "copilot", "gemini"],
  "output_dir": "/home/user/my-project/devmind-output/project-documenter/my-project-20260130-100000",
  "files": [
    "claude/CLAUDE.md",
    "copilot/copilot-instructions.md",
    "gemini/GEMINI.md"
  ]
}
```

### List Available Formats

```bash
curl http://localhost:8000/api/v1/project-docs/formats
```

---

## Python Client Example

```python
import httpx

class DevMindClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.client = httpx.Client(base_url=base_url)

    def review_file(self, file_path: str, content: str):
        response = self.client.post(
            "/api/v1/reviews/review-file",
            json={"file_path": file_path, "content": content}
        )
        return response.json()

    def scan_vulnerabilities(self, repo_id: str):
        # Trigger scan
        response = self.client.post(f"/api/v1/security/{repo_id}/scan")
        return response.json()

    def generate_tests(self, code: str, file_path: str, framework="pytest"):
        response = self.client.post(
            "/api/v1/tests/generate",
            json={
                "code": code,
                "file_path": file_path,
                "framework": framework
            }
        )
        return response.json()

# Usage
client = DevMindClient()

# Review a file
with open("src/auth.py") as f:
    result = client.review_file("auth.py", f.read())
    for comment in result["comments"]:
        print(f"{comment['severity']}: {comment['title']} (line {comment['line_number']})")

# Generate tests
with open("src/utils.py") as f:
    tests = client.generate_tests(f.read(), "utils.py")
    print(tests["test_file_content"])
```

---

## Error Handling

```bash
# Invalid request
curl -X POST http://localhost:8000/api/v1/reviews/review-file \
  -H "Content-Type: application/json" \
  -d '{"file_path": "test.py"}'
# Missing required field "content"
```

**Response:**
```json
{
  "detail": [
    {
      "loc": ["body", "content"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Async Operations

For long-running operations, use the async job pattern:

```bash
# 1. Start the job
JOB_RESPONSE=$(curl -X POST http://localhost:8000/api/v1/reviews/repos/my-repo/review \
  -H "Content-Type: application/json" \
  -d '{"pr_number": 42}')

JOB_ID=$(echo $JOB_RESPONSE | jq -r '.job_id')

# 2. Poll for completion
while true; do
  STATUS=$(curl -s "http://localhost:8000/api/v1/reviews/jobs/$JOB_ID/status" | jq -r '.status')
  echo "Status: $STATUS"

  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    break
  fi

  sleep 5
done

# 3. Get results
curl "http://localhost:8000/api/v1/reviews/jobs/$JOB_ID/status"
```
