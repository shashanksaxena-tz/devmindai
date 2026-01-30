# Full Stack Setup

Deploy DevMind with API server, database, and all infrastructure components.

## Prerequisites

- Docker & Docker Compose
- At least one LLM API key
- 4GB RAM minimum (8GB recommended)

## Quick Setup with Docker

```bash
# Clone repository
git clone <repository-url>
cd DevMind-AI

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# At minimum, set GOOGLE_API_KEY or ANTHROPIC_API_KEY

# Start all services
docker-compose up -d

# Verify
curl http://localhost:8000/health
```

## Services Started

| Service | Port | Purpose |
|---------|------|---------|
| API Server | 8000 | REST API |
| PostgreSQL | 5432 | Data persistence |
| Redis | 6379 | Caching & job queue |
| Qdrant | 6333, 6334 | Vector search |
| Dashboard | 8501 | Streamlit UI |

## Environment Configuration

Edit `.env` with your settings:

```bash
# === Required: At least one LLM ===
GOOGLE_API_KEY=your-gemini-key
ANTHROPIC_API_KEY=your-claude-key

# === Infrastructure (defaults work for Docker) ===
DATABASE_URL=postgresql+asyncpg://devmind:devmind@postgres:5432/devmind
REDIS_URL=redis://redis:6379/0
QDRANT_URL=http://qdrant:6333

# === Security ===
SECRET_KEY=generate-a-secure-random-string-at-least-32-chars

# === Optional: GitHub Integration ===
GITHUB_APP_ID=your-app-id
GITHUB_CLIENT_ID=your-client-id
GITHUB_CLIENT_SECRET=your-client-secret
GITHUB_PRIVATE_KEY_PATH=/app/config/github-app.pem
GITHUB_WEBHOOK_SECRET=your-webhook-secret
```

## Verifying Services

```bash
# Check all containers are running
docker-compose ps

# API health check
curl http://localhost:8000/health

# Database connection
curl http://localhost:8000/ready

# View logs
docker-compose logs -f api
```

## Using the API

```bash
# Analyze a project
curl -X POST http://localhost:8000/api/v1/project-docs/analyze \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/project"}'

# Generate documentation
curl -X POST http://localhost:8000/api/v1/project-docs/generate \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/project", "formats": ["claude", "copilot"]}'

# Code review
curl -X POST http://localhost:8000/api/v1/reviews/review-file \
  -H "Content-Type: application/json" \
  -d '{"file_path": "example.py", "content": "def add(a, b): return a + b"}'
```

See [API Reference](../api/REFERENCE.md) for all endpoints.

## Dashboard Access

Open http://localhost:8501 for the Streamlit dashboard.

Features:
- Project analysis UI
- Scan results viewer
- Review history
- Configuration management

## Running Without Docker

For development or if Docker isn't available:

### 1. Start Infrastructure

You can use managed services or local installations:

```bash
# PostgreSQL
createdb devmind
export DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/devmind

# Redis
redis-server &
export REDIS_URL=redis://localhost:6379/0

# Qdrant (optional)
docker run -p 6333:6333 qdrant/qdrant
export QDRANT_URL=http://localhost:6333
```

### 2. Install Dependencies

```bash
pip install -e ".[api,dev]"
```

### 3. Run Migrations

```bash
alembic upgrade head
```

### 4. Start API Server

```bash
uvicorn src.api.main:app --reload --port 8000
```

## Background Workers

For async job processing (PR reviews, scans):

```bash
# In a separate terminal
celery -A src.workers.celery_app worker --loglevel=info
```

## GitHub App Setup

For automated PR reviews:

1. Create a GitHub App at github.com/settings/apps
2. Set webhook URL to `https://your-domain/api/v1/webhooks/github`
3. Enable permissions: Pull requests (Read & Write), Contents (Read)
4. Subscribe to events: Pull request, Issue comment
5. Generate private key and save to `config/github-app.pem`
6. Set environment variables

See [GitHub Integration](../integrations/GITHUB.md) for details.

## Scaling

### Multiple API Workers

```bash
# docker-compose.override.yml
services:
  api:
    deploy:
      replicas: 3
```

### Multiple Celery Workers

```bash
docker-compose up -d --scale worker=4
```

## Troubleshooting

**Container won't start**
```bash
docker-compose logs <service-name>
```

**Database connection failed**
```bash
# Check PostgreSQL is ready
docker-compose exec postgres pg_isready
```

**Redis connection failed**
```bash
# Check Redis is responding
docker-compose exec redis redis-cli ping
```

## Next Steps

- [API Reference](../api/REFERENCE.md) - All endpoints
- [GitHub Integration](../integrations/GITHUB.md) - Automated PR reviews
- [Feature Matrix](../features/FEATURE_MATRIX.md) - What each component enables
- [Architecture](../architecture/ARCHITECTURE.md) - System design
