---
name: document-project
description: Generate comprehensive AI-ready project documentation including CLAUDE.md, AGENTS.md, GEMINI.md, README, and architecture docs. Use this when asked to document a project, create AI context files, or generate documentation.
---

# Project Documentation Skill

You are a **senior technical writer** creating comprehensive project documentation optimized for both humans and AI assistants.

## Execution Strategy

### Phase 1: Project Analysis

Gather complete project context by examining:

#### 1. Project Identity
```
□ Project name (from package.json, pyproject.toml, go.mod, etc.)
□ Version and release status
□ License
□ Primary purpose/description
□ Target audience
```

#### 2. Technology Stack
```
□ Primary language(s) and versions
□ Framework(s) and versions
□ Database(s) and ORM
□ Build tools
□ Test frameworks
□ Infrastructure (Docker, K8s, cloud providers)
```

#### 3. Project Structure
```
□ Directory layout
□ Key directories and their purposes
□ Entry points (main files, CLI commands, API routes)
□ Configuration files
□ Test organization
```

#### 4. Dependencies
```
□ Production dependencies
□ Development dependencies
□ Peer dependencies
□ Native/system requirements
```

#### 5. Commands
```
□ Installation commands
□ Development server
□ Build commands
□ Test commands
□ Linting/formatting
□ Deployment commands
```

#### 6. Conventions
```
□ Coding style (from .editorconfig, linter configs)
□ Naming conventions
□ File organization patterns
□ Commit message format
□ Branch naming
```

### Phase 2: Documentation Generation

Generate these documentation files:

#### File 1: CLAUDE.md / AGENTS.md / GEMINI.md

Create a unified AI context file that works for all AI assistants:

```markdown
# {Project Name}

{One-sentence description of what this project does}

## Overview

{2-3 paragraphs explaining:}
- What the project does and the problem it solves
- Who the target users are
- Key features and capabilities

## Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python 3.11+ |
| Framework | FastAPI 0.100+ |
| Database | PostgreSQL 15 + SQLAlchemy 2.0 |
| Cache | Redis 7.0 |
| Queue | Celery + Redis |
| Testing | pytest + pytest-asyncio |
| Container | Docker + docker-compose |

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7.0+

### Installation
```bash
# Clone the repository
git clone {repo_url}
cd {project_name}

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -e ".[dev]"

# Set up database
createdb {db_name}
alembic upgrade head

# Start development server
uvicorn src.main:app --reload
```

## Key Commands

| Command | Description |
|---------|-------------|
| `uvicorn src.main:app --reload` | Start dev server |
| `pytest` | Run all tests |
| `pytest --cov=src` | Run tests with coverage |
| `ruff check .` | Lint code |
| `ruff format .` | Format code |
| `alembic upgrade head` | Run migrations |
| `alembic revision --autogenerate -m "msg"` | Create migration |

## Project Structure

```
{project_name}/
├── src/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration management
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/          # API endpoint definitions
│   │   │   ├── users.py
│   │   │   └── items.py
│   │   └── dependencies.py  # Dependency injection
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   └── user_service.py
│   └── utils/               # Utility functions
│       └── helpers.py
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_api/
│   └── test_services/
├── alembic/                  # Database migrations
├── docker/                   # Docker configurations
├── pyproject.toml           # Project configuration
└── .env.example             # Environment variables template
```

## Architecture

### Request Flow
```
Client Request
      ↓
   FastAPI Router (src/api/routes/)
      ↓
   Dependency Injection (src/api/dependencies.py)
      ↓
   Service Layer (src/services/)
      ↓
   Repository/Model Layer (src/models/)
      ↓
   Database (PostgreSQL)
```

### Key Components

- **API Layer**: FastAPI routes handle HTTP requests/responses
- **Service Layer**: Business logic, orchestration, external integrations
- **Model Layer**: SQLAlchemy ORM models, database access
- **Schema Layer**: Pydantic models for validation and serialization

## Code Conventions

### General
- Use type hints for all function signatures
- Write docstrings for all public functions/classes
- Maximum line length: 88 characters (Black default)
- Use absolute imports within the project

### Naming
- `snake_case` for functions and variables
- `PascalCase` for classes
- `UPPER_CASE` for constants
- Prefix private methods with `_`

### File Organization
- One class per file for models/schemas
- Group related routes in single module
- Tests mirror source structure

### Error Handling
- Use custom exceptions in `src/exceptions.py`
- Always log errors before raising
- Return appropriate HTTP status codes

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `REDIS_URL` | Redis connection string | Yes | - |
| `SECRET_KEY` | JWT signing key | Yes | - |
| `DEBUG` | Enable debug mode | No | `false` |
| `LOG_LEVEL` | Logging level | No | `INFO` |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/users` | List users |
| `POST` | `/api/v1/users` | Create user |
| `GET` | `/api/v1/users/{id}` | Get user by ID |
| `PUT` | `/api/v1/users/{id}` | Update user |
| `DELETE` | `/api/v1/users/{id}` | Delete user |

## Common Tasks

### Adding a New API Endpoint
1. Create route handler in `src/api/routes/`
2. Create Pydantic schemas in `src/schemas/`
3. Implement service logic in `src/services/`
4. Add tests in `tests/test_api/`
5. Update API documentation

### Adding a Database Model
1. Create model in `src/models/`
2. Create migration: `alembic revision --autogenerate -m "Add model"`
3. Apply migration: `alembic upgrade head`
4. Create corresponding schema in `src/schemas/`

### Running in Production
```bash
# Build Docker image
docker build -t {project_name} .

# Run with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

## Important Files

- `src/main.py` - Application entry point and FastAPI app creation
- `src/config.py` - Pydantic settings for configuration management
- `src/api/dependencies.py` - Dependency injection (database, auth, etc.)
- `alembic/env.py` - Database migration configuration
- `pyproject.toml` - Project metadata and tool configuration

## Troubleshooting

### Common Issues

**Database connection errors:**
- Verify `DATABASE_URL` is correct
- Ensure PostgreSQL is running
- Check network connectivity

**Import errors:**
- Run `pip install -e .` to install in editable mode
- Verify virtual environment is activated

**Migration errors:**
- Check for pending migrations: `alembic current`
- Clear migration state if needed: `alembic stamp head`
```

#### File 2: README.md (Human-Focused)

```markdown
# {Project Name}

{Badges: build status, coverage, version, license}

{One paragraph description}

## Features

- ✨ Feature 1
- 🚀 Feature 2
- 🔒 Feature 3

## Installation

{Step-by-step installation guide}

## Usage

{Quick usage examples with code}

## Documentation

- [API Documentation](./docs/api.md)
- [Architecture](./docs/architecture.md)
- [Contributing](./CONTRIBUTING.md)

## Contributing

{Brief contribution guidelines}

## License

{License information}
```

#### File 3: ARCHITECTURE.md

```markdown
# Architecture Documentation

## System Overview

{High-level architecture diagram using text/mermaid}

## Component Details

{Detailed explanation of each major component}

## Data Flow

{How data moves through the system}

## External Integrations

{Third-party services and how they're used}

## Security Considerations

{Security architecture and practices}
```

## Output Format

```markdown
# Documentation Generated

**Project:** {project_name}
**Path:** {project_path}

## Files Created/Updated

| File | Status | Description |
|------|--------|-------------|
| CLAUDE.md | ✅ Created | AI context file |
| AGENTS.md | ✅ Symlinked to CLAUDE.md | Cross-compatibility |
| GEMINI.md | ✅ Symlinked to CLAUDE.md | Cross-compatibility |
| README.md | ⚠️ Updated | Added missing sections |
| docs/ARCHITECTURE.md | ✅ Created | System architecture |

## Summary

- Total lines of documentation: ~500
- Key commands documented: 12
- API endpoints documented: 15
- Environment variables: 8

## Recommendations

1. Add API documentation with OpenAPI/Swagger
2. Create CONTRIBUTING.md
3. Add CHANGELOG.md for release tracking
```

## Handling Large Codebases

For large projects with many modules:

1. **Generate skeleton first, then fill:**
```
/document-project --skeleton
/document-project --section api
/document-project --section models
```

2. **Use continuation:**
```markdown
## ⚠️ Documentation In Progress

Documented: src/api/, src/models/
Remaining: src/services/, src/utils/

Continue: `/document-project --continue`
```

## Arguments

- `$1` - Project path (default: current directory)
- `--format` - Output formats: `claude`, `copilot`, `cursor`, `all`
- `--include-api` - Generate API documentation
- `--skeleton` - Generate structure only, fill later
- `--continue` - Continue from checkpoint
