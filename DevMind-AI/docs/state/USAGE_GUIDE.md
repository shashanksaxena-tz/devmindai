# DevMind-AI Usage Guide
**Last Updated:** 2026-01-20

This guide explains how to set up and use DevMind-AI for code review, vulnerability scanning, and test generation.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Starting the Server](#starting-the-server)
5. [Using the Agents](#using-the-agents)
6. [Working with Private Repos](#working-with-private-repos)

---

## Prerequisites

- **Python 3.11+**
- **Docker & Docker Compose** (for PostgreSQL, Redis, Qdrant)
- **API Keys:**
  - Anthropic API key (Claude) - Required
  - Google API key (Gemini) - Required
  - GitHub Personal Access Token (for private repos)

---

## Installation

### Step 1: Clone and Setup Python Environment

```bash
cd DevMind-AI
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Step 2: Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```bash
# Required - LLM APIs
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
GOOGLE_API_KEY=AIzaSyxxxxx

# Required - Database
DATABASE_URL=postgresql+asyncpg://devmind:devmind@localhost:5432/devmind

# Optional - For private GitHub repos
GITHUB_TOKEN=ghp_xxxxx
```

### Step 3: Start Infrastructure

```bash
docker-compose up -d postgres redis qdrant
```

Verify services are running:
```bash
docker-compose ps
```

### Step 4: Run Database Migrations

```bash
alembic upgrade head
```

---

## Starting the Server

### Development Mode

```bash
uvicorn src.api.main:app --reload
```

Server runs at: **http://localhost:8000**

### With Docker (Full Stack)

```bash
docker-compose up -d
```

---

## Using the Agents

### Method 1: Swagger UI (Easiest)

1. Open http://localhost:8000/docs
2. Explore and test endpoints interactively

### Method 2: cURL Examples

#### Code Review - Review a Single File (No GitHub Needed!)

```bash
curl -X POST http://localhost:8000/api/v1/reviews/review-file \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "example.py",
    "content": "import pickle\n\ndef load_data(user_input):\n    return pickle.loads(user_input)\n"
  }'
```

**Response:**
```json
{
  "file_path": "example.py",
  "blocker_count": 1,
  "warning_count": 0,
  "suggestion_count": 1,
  "comments": [
    {
      "line_number": 4,
      "severity": "blocker",
      "category": "security",
      "title": "Security: Insecure Deserialization",
      "message": "Using pickle.loads on user input allows arbitrary code execution",
      "suggestion": "Use json.loads() or validate input before deserializing"
    }
  ]
}
```

#### Vulnerability Scan

First, register a repository in the database, then:

```bash
# Trigger scan
curl -X POST http://localhost:8000/api/v1/security/{repo_id}/scan \
  -H "Content-Type: application/json" \
  -d '{"full_scan": true}'

# Check results
curl http://localhost:8000/api/v1/security/{repo_id}/summary
```

#### PR Review (Requires GitHub Token)

```bash
curl -X POST http://localhost:8000/api/v1/reviews/repos/{repo_id}/review \
  -H "Content-Type: application/json" \
  -d '{"pr_number": 42}'

# Check job status
curl http://localhost:8000/api/v1/reviews/jobs/{job_id}/status
```

### Method 3: Python Client

```python
import httpx

client = httpx.Client(base_url="http://localhost:8000/api/v1")

# Review a file
response = client.post("/reviews/review-file", json={
    "file_path": "my_module.py",
    "content": open("my_module.py").read()
})

print(response.json())
```

---

## Working with Private Repos

### Option A: GitHub Personal Access Token

1. Create a PAT at https://github.com/settings/tokens
2. Set in environment:
   ```bash
   export GITHUB_TOKEN=ghp_xxxxx
   ```
3. The GitHub integration will use this for API calls

### Option B: Local Clone Path

For repos you've already cloned locally:

1. Register the repository with a `local_path` in config
2. The VulnScanner will scan files directly from disk

---

## Quick Reference

| Task | Endpoint | Method |
|------|----------|--------|
| Review code snippet | `/api/v1/reviews/review-file` | POST |
| Trigger PR review | `/api/v1/reviews/repos/{repo_id}/review` | POST |
| Check review status | `/api/v1/reviews/jobs/{job_id}/status` | GET |
| Trigger vuln scan | `/api/v1/security/{repo_id}/scan` | POST |
| List vulnerabilities | `/api/v1/security/{repo_id}/vulns` | GET |
| Health check | `/health` | GET |
| API docs | `/docs` | Browser |

---

## Troubleshooting

### "Database connection failed"
- Ensure PostgreSQL is running: `docker-compose ps`
- Check DATABASE_URL in `.env`

### "LLM API error"
- Verify API keys are correct in `.env`
- Check API quotas/limits

### "Repository not found"
- Repository must be registered in the database first
- Use Swagger UI to create a repository record
