# DevMind AI

AI-powered developer platform with 10 intelligent agents for code review, security scanning, test generation, and more.

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker (optional)

### Setup

1. Clone and install dependencies:
```bash
cd DevMind-AI
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

2. Copy environment file:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Start services (Docker):
```bash
docker-compose up -d postgres redis qdrant
```

4. Run migrations:
```bash
alembic upgrade head
```

5. Start the API:
```bash
uvicorn src.api.main:app --reload
```

## Project Structure

```
DevMind-AI/
├── src/
│   ├── api/           # FastAPI routes and middleware
│   ├── agents/        # AI agent implementations
│   ├── core/          # Core business logic
│   ├── db/            # Database models and migrations
│   ├── integrations/  # External service integrations
│   └── utils/         # Shared utilities
├── tests/             # Test suite
├── dashboard/         # Streamlit dashboard
├── config/            # Configuration files
└── docs/              # Documentation
```

## Agents

1. **VulnScanner** - Security vulnerability detection
2. **CodeReviewer** - Automated PR reviews
3. **TestGenerator** - AI-generated test suites
4. **DebtAnalyzer** - Technical debt tracking
5. **DocGenerator** - Automated documentation
6. **IncidentResponder** - Alert correlation & diagnosis
7. **CodeMigrator** - Framework/language migrations
8. **QueryOptimizer** - Database query optimization
9. **ADRRecorder** - Architecture decision recording
10. **PipelineGenerator** - CI/CD pipeline generation

## License

MIT
