# Infrastructure

Optional infrastructure components that enable advanced features.

## Overview

| Component | What It Enables | Required? |
|-----------|-----------------|-----------|
| [Docker](DOCKER.md) | Containerized deployment | No |
| [PostgreSQL](POSTGRESQL.md) | Persistence, history, multi-tenant | No |
| [Redis](REDIS.md) | Caching, background jobs | No |
| [Qdrant](QDRANT.md) | Vector search, semantic queries | No |

## Quick Reference

### CLI Only (No Infrastructure)

```bash
# Just Python + API key
pip install -e ".[cli]"
export GOOGLE_API_KEY=your-key
devmind --help
```

All core features work without infrastructure.

### Full Stack (All Components)

```bash
# Docker handles everything
docker-compose up -d
```

## What Each Component Enables

### Without Infrastructure
- All CLI commands work
- All documentation formats
- Security scanning
- Code review
- Test generation
- Results output to terminal/files

### + PostgreSQL
- Scan history and trends
- Review history
- User accounts
- Organization management
- Repository tracking
- Audit logs

### + Redis
- LLM response caching
- Background job processing
- Rate limiting
- Session storage

### + Qdrant
- Semantic code search
- ADR indexing and search
- Similar vulnerability lookup
- RAG-enhanced analysis

## Deployment Options

| Option | Components | Best For |
|--------|------------|----------|
| CLI only | Python + LLM | Individual developers |
| Docker Compose | All services | Small teams, self-hosted |
| Kubernetes | Scalable deployment | Enterprise |
| Managed services | Cloud PostgreSQL/Redis | Production |

## Cost Considerations

| Component | Self-Hosted | Managed |
|-----------|-------------|---------|
| PostgreSQL | Free | ~$15/mo (AWS RDS) |
| Redis | Free | ~$10/mo (ElastiCache) |
| Qdrant | Free | Cloud pricing |

## Getting Started

1. Start with [CLI Setup](../getting-started/CLI_SETUP.md) - no infrastructure needed
2. Add infrastructure when you need:
   - History/persistence → [PostgreSQL](POSTGRESQL.md)
   - Background processing → [Redis](REDIS.md)
   - Semantic search → [Qdrant](QDRANT.md)
3. Or use [Docker](DOCKER.md) for everything at once

See [Feature Matrix](../features/FEATURE_MATRIX.md) for detailed feature comparison.
