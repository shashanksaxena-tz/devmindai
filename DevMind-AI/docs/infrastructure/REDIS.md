# Redis Setup

Redis provides caching and background job processing for DevMind.

## What Redis Enables

| Feature | Description |
|---------|-------------|
| LLM response caching | Faster repeat queries |
| Background jobs | Async PR review/scan execution |
| Job queues | Celery worker support |
| Rate limiting | Per-user/org request limits |
| Session storage | User session management |

## Quick Setup (Docker)

```bash
# Using docker-compose (recommended)
docker-compose up -d redis

# Or standalone
docker run -d \
  --name devmind-redis \
  -p 6379:6379 \
  redis:7-alpine
```

## Manual Installation

### macOS

```bash
brew install redis
brew services start redis
```

### Ubuntu/Debian

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
```

### Windows

Use WSL2 with Linux instructions, or download from [redis.io](https://redis.io/docs/install/install-redis/install-redis-on-windows/)

## Configuration

Set the connection URL:

```bash
# Environment variable
export REDIS_URL=redis://localhost:6379/0

# Or in .env
REDIS_URL=redis://localhost:6379/0
```

### URL Format

```
redis://[[username]:[password]@]host[:port][/database]
```

- Default port: 6379
- Default database: 0 (Redis has 16 databases, 0-15)

## Caching

DevMind caches LLM responses to reduce costs and latency.

### How It Works

1. Request hash computed from prompt + parameters
2. Check Redis for cached response
3. If found and not expired, return cached
4. Otherwise, call LLM and cache result

### Cache Keys

```
devmind:llm:gemini:<hash>
devmind:llm:claude:<hash>
devmind:rate:<user_id>:<window>
devmind:session:<session_id>
```

### Cache TTL

Default: 1 hour for LLM responses

Configure in `.devmind.yaml`:

```yaml
cache:
  llm_ttl: 3600  # seconds
```

## Background Jobs

DevMind uses Celery with Redis for async tasks.

### Starting Workers

```bash
# Single worker
celery -A src.workers.celery_app worker --loglevel=info

# Multiple workers
celery -A src.workers.celery_app worker --concurrency=4
```

### Job Types

| Job | Purpose |
|-----|---------|
| `review_pr` | Async PR review |
| `scan_repository` | Vulnerability scan |
| `generate_docs_batch` | Batch documentation |
| `process_webhook` | GitHub webhook handling |

### Monitoring

```bash
# Flower (Celery monitoring)
pip install flower
celery -A src.workers.celery_app flower
# Open http://localhost:5555
```

## Rate Limiting

Redis tracks request counts for rate limiting.

```python
# Example: 100 requests per minute per user
rate_key = f"devmind:rate:{user_id}:{minute}"
count = redis.incr(rate_key)
if count == 1:
    redis.expire(rate_key, 60)
if count > 100:
    raise RateLimitExceeded()
```

## Session Storage

For API authentication:

```python
# Store session
redis.setex(f"devmind:session:{session_id}", 3600, user_data)

# Retrieve
user_data = redis.get(f"devmind:session:{session_id}")
```

## Managed Services

### AWS ElastiCache

```bash
REDIS_URL=redis://xxx.cache.amazonaws.com:6379/0
```

### Redis Cloud

```bash
REDIS_URL=redis://user:pass@xxx.redis-cloud.com:port/0
```

### Heroku Redis

```bash
# Heroku sets REDIS_URL automatically
```

## Performance Tuning

### Memory Policy

For caching workload, use allkeys-lru:

```bash
# redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### Connection Pool

DevMind uses connection pooling:

```python
pool = redis.ConnectionPool.from_url(
    REDIS_URL,
    max_connections=20,
)
```

## Troubleshooting

**"Connection refused"**
```bash
# Check Redis is running
redis-cli ping

# Check Docker
docker-compose ps redis
```

**"NOAUTH Authentication required"**
```bash
# Add password to URL
REDIS_URL=redis://:password@localhost:6379/0
```

**"OOM command not allowed"**
```bash
# Redis out of memory
# Increase maxmemory or clear cache
redis-cli FLUSHDB
```

**"Connection pool exhausted"**
- Increase max_connections
- Check for connection leaks
- Ensure connections are released

## Security Considerations

- Use password in production
- Don't expose port 6379 externally
- Use SSL for remote connections
- Regular memory monitoring

```bash
# Production connection with password
REDIS_URL=redis://:strongpassword@localhost:6379/0

# With SSL
REDIS_URL=rediss://:password@host:6379/0
```

## Without Background Jobs

If you don't need async processing:
- Skip Redis entirely
- All operations run synchronously
- CLI commands work without Redis
- API requests block until complete
