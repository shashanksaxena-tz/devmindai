# Docker Setup

Deploy DevMind with Docker Compose for a complete, self-contained stack.

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum (8GB recommended)

## Quick Start

```bash
# Clone repository
git clone <repository-url>
cd DevMind-AI

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker-compose up -d

# Verify
curl http://localhost:8000/health
```

## Services

| Service | Port | Purpose |
|---------|------|---------|
| `api` | 8000 | REST API server |
| `postgres` | 5432 | Database |
| `redis` | 6379 | Cache & queue |
| `qdrant` | 6333, 6334 | Vector database |
| `dashboard` | 8501 | Streamlit UI |
| `worker` | - | Background jobs (optional) |

## docker-compose.yml

The included `docker-compose.yml` defines all services:

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql+asyncpg://devmind:devmind@postgres:5432/devmind
      - REDIS_URL=redis://redis:6379/0

  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: devmind
      POSTGRES_PASSWORD: devmind
      POSTGRES_DB: devmind
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
```

## Configuration

### Environment Variables

Create `.env` from template:

```bash
cp .env.example .env
```

Required settings:

```bash
# At least one LLM provider
GOOGLE_API_KEY=your-key
ANTHROPIC_API_KEY=your-key

# Security
SECRET_KEY=generate-a-random-string-at-least-32-chars
```

Infrastructure URLs are preset for Docker networking.

### Custom Ports

Override in `docker-compose.override.yml`:

```yaml
services:
  api:
    ports:
      - "3000:8000"  # Map to port 3000
```

## Common Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api
docker-compose logs -f postgres

# Stop all services
docker-compose down

# Stop and remove volumes (data loss!)
docker-compose down -v

# Rebuild after code changes
docker-compose up -d --build

# Check status
docker-compose ps
```

## Accessing Services

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Dashboard | http://localhost:8501 |
| Qdrant UI | http://localhost:6333/dashboard |

## Volume Management

Data is persisted in Docker volumes:

| Volume | Purpose |
|--------|---------|
| `postgres_data` | Database files |
| `qdrant_data` | Vector embeddings |
| `redis_data` | Cache (optional) |

### Backup

```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U devmind devmind > backup.sql

# Restore
docker-compose exec -T postgres psql -U devmind devmind < backup.sql
```

### Reset Data

```bash
# Remove all data (caution!)
docker-compose down -v
docker-compose up -d
```

## Scaling

### Multiple API Workers

```yaml
# docker-compose.override.yml
services:
  api:
    deploy:
      replicas: 3
```

### Multiple Background Workers

```bash
docker-compose up -d --scale worker=4
```

## Health Checks

```bash
# API health
curl http://localhost:8000/health

# API readiness (checks DB/Redis)
curl http://localhost:8000/ready

# PostgreSQL
docker-compose exec postgres pg_isready

# Redis
docker-compose exec redis redis-cli ping
```

## Production Considerations

### Security

```yaml
# docker-compose.prod.yml
services:
  postgres:
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}  # Use secrets
    # Don't expose port externally
    expose:
      - "5432"
```

### Resources

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2'
```

### Logging

```yaml
services:
  api:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

## Troubleshooting

**Container won't start**
```bash
docker-compose logs <service>
```

**Database connection failed**
```bash
# Check postgres is healthy
docker-compose exec postgres pg_isready

# Check connection from api
docker-compose exec api python -c "from src.db.session import engine; print('OK')"
```

**Out of disk space**
```bash
# Clean up unused images/containers
docker system prune -a
```

**Port already in use**
```bash
# Find process using port
lsof -i :8000

# Or change port in docker-compose.override.yml
```

## Development Mode

For development with hot reload:

```bash
# Mount source code
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

`docker-compose.dev.yml`:
```yaml
services:
  api:
    volumes:
      - ./src:/app/src
    command: uvicorn src.api.main:app --reload --host 0.0.0.0
```

## Without Docker

If Docker isn't available, see:
- [PostgreSQL Setup](POSTGRESQL.md) for manual database setup
- [Redis Setup](REDIS.md) for manual cache setup
- [Full Stack Setup](../getting-started/FULL_STACK_SETUP.md) for complete guide
