# PostgreSQL Setup

PostgreSQL provides data persistence for DevMind's API server mode.

## What PostgreSQL Enables

| Feature | Description |
|---------|-------------|
| Scan history | Track vulnerabilities over time |
| Review history | See past code reviews |
| User accounts | Authentication & profiles |
| Organizations | Multi-tenant team management |
| Repository tracking | Monitor multiple repos |
| Audit logs | Record all actions |
| Health scores | Repository quality metrics |
| Trend analysis | Improvement over time |

## Quick Setup (Docker)

```bash
# Using docker-compose (recommended)
docker-compose up -d postgres

# Or standalone
docker run -d \
  --name devmind-postgres \
  -e POSTGRES_USER=devmind \
  -e POSTGRES_PASSWORD=devmind \
  -e POSTGRES_DB=devmind \
  -p 5432:5432 \
  postgres:15
```

## Manual Installation

### macOS

```bash
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb devmind
```

### Ubuntu/Debian

```bash
sudo apt update
sudo apt install postgresql-15

# Create database
sudo -u postgres createdb devmind
sudo -u postgres createuser devmind -P
```

### Windows

Download from [postgresql.org](https://www.postgresql.org/download/windows/)

## Configuration

Set the connection URL:

```bash
# Environment variable
export DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/devmind

# Or in .env
DATABASE_URL=postgresql+asyncpg://devmind:devmind@localhost:5432/devmind
```

### Connection URL Format

```
postgresql+asyncpg://username:password@host:port/database
```

- `asyncpg` - Async driver (required)
- Default port: 5432

## Database Schema

DevMind uses these tables:

| Table | Purpose |
|-------|---------|
| `users` | User accounts |
| `organizations` | Team/company entities |
| `org_members` | User-organization mapping |
| `repositories` | Tracked repositories |
| `pr_reviews` | Code review results |
| `vulnerability_scans` | Scan job records |
| `vulnerabilities` | Individual CVE findings |

### Entity Relationships

```
Organization
  ├── Users (via OrgMember)
  └── Repositories
        ├── PRReviews
        └── VulnerabilityScans
              └── Vulnerabilities
```

## Running Migrations

DevMind uses Alembic for migrations:

```bash
# Apply all migrations
alembic upgrade head

# Check current version
alembic current

# Generate new migration (after model changes)
alembic revision --autogenerate -m "Add new table"
```

## Connection Pooling

For production, configure pooling:

```python
# In src/db/session.py
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)
```

## Backup & Restore

### Backup

```bash
# Full dump
pg_dump -U devmind devmind > backup.sql

# With Docker
docker-compose exec postgres pg_dump -U devmind devmind > backup.sql

# Compressed
pg_dump -U devmind devmind | gzip > backup.sql.gz
```

### Restore

```bash
# From SQL file
psql -U devmind devmind < backup.sql

# With Docker
docker-compose exec -T postgres psql -U devmind devmind < backup.sql

# From compressed
gunzip -c backup.sql.gz | psql -U devmind devmind
```

## Managed Services

### AWS RDS

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@xxx.rds.amazonaws.com:5432/devmind
```

### Google Cloud SQL

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@/devmind?host=/cloudsql/project:region:instance
```

### Heroku Postgres

```bash
# Heroku sets DATABASE_URL automatically
# Just add +asyncpg after postgresql
DATABASE_URL=${DATABASE_URL/postgresql/postgresql+asyncpg}
```

## Performance Tuning

### Connection Limits

```sql
-- Check current connections
SELECT count(*) FROM pg_stat_activity;

-- Set max connections (postgresql.conf)
max_connections = 100
```

### Indexing

DevMind creates indexes automatically, but for large deployments:

```sql
-- Index for vulnerability queries
CREATE INDEX idx_vulns_severity ON vulnerabilities(severity);
CREATE INDEX idx_vulns_status ON vulnerabilities(status);

-- Index for review queries
CREATE INDEX idx_reviews_repo ON pr_reviews(repository_id);
CREATE INDEX idx_reviews_created ON pr_reviews(created_at);
```

## Troubleshooting

**"Connection refused"**
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Check Docker
docker-compose ps postgres
```

**"Authentication failed"**
```bash
# Verify credentials
psql -U devmind -h localhost -d devmind

# Check pg_hba.conf allows connections
```

**"Database does not exist"**
```bash
createdb devmind
# Or with psql
psql -U postgres -c "CREATE DATABASE devmind"
```

**"asyncpg not found"**
```bash
pip install asyncpg
# Or reinstall DevMind
pip install -e ".[api]"
```

## Security Considerations

- Use strong passwords in production
- Don't expose port 5432 externally
- Use SSL for remote connections
- Regular backups
- Limit user permissions

```bash
# Production connection with SSL
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/devmind?ssl=require
```
