# DevMind API

REST API for programmatic access to DevMind agents.

## Overview

The API provides endpoints for:
- Code review
- Security scanning
- Test generation
- Documentation generation

## Quick Start

```bash
# Start API server
uvicorn src.api.main:app --reload --port 8000

# Or with Docker
docker-compose up -d api

# View interactive docs
open http://localhost:8000/docs
```

## Base URL

```
http://localhost:8000
```

## Authentication

> Authentication is scaffolded but not enforced in development mode.

When enabled:
```
Authorization: Bearer <token>
```

## Endpoints Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/ready` | GET | Readiness check |
| `/api/v1/reviews/review-file` | POST | Review a file |
| `/api/v1/security/{repo_id}/scan` | POST | Scan for vulnerabilities |
| `/api/v1/tests/generate` | POST | Generate tests |
| `/api/v1/project-docs/analyze` | POST | Analyze project |
| `/api/v1/project-docs/generate` | POST | Generate documentation |

## Documentation

| Guide | Description |
|-------|-------------|
| [Reference](REFERENCE.md) | Complete endpoint documentation |
| [Examples](EXAMPLES.md) | Usage examples |

## Quick Examples

### Code Review

```bash
curl -X POST http://localhost:8000/api/v1/reviews/review-file \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "example.py",
    "content": "def add(a, b):\n    return a + b"
  }'
```

### Security Scan

```bash
curl -X POST http://localhost:8000/api/v1/security/scan \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/project"}'
```

### Generate Tests

```bash
curl -X POST http://localhost:8000/api/v1/tests/generate \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def add(a, b): return a + b",
    "file_path": "math.py",
    "framework": "pytest"
  }'
```

## Error Handling

All errors return:

```json
{
  "detail": "Error description"
}
```

Status codes:
- `400` - Bad request
- `401` - Unauthorized
- `404` - Not found
- `422` - Validation error
- `500` - Server error

## Rate Limits

Default limits (configurable):
- 100 requests/minute per IP
- 1000 requests/hour per user

## Requirements

| Component | Required For |
|-----------|--------------|
| LLM API key | All endpoints |
| PostgreSQL | Async jobs, history |
| Redis | Caching, rate limiting |

See [Full Stack Setup](../getting-started/FULL_STACK_SETUP.md) for complete configuration.
