# DevMind AI Feature Matrix

This guide shows what features are available with each component combination.

## Component Overview

| Component | Purpose | Required? |
|-----------|---------|-----------|
| **CLI** | Command-line interface | Yes |
| **Gemini** | Primary LLM (simple tasks) | Yes (one LLM required) |
| **Claude** | Complex reasoning | Optional |
| **OpenAI** | Fallback LLM | Optional |
| **PostgreSQL** | Data persistence | Optional |
| **Redis** | Caching & job queue | Optional |
| **Qdrant** | Vector search | Optional |
| **GitHub App** | PR automation | Optional |

---

## Feature Availability by Setup

### CLI + Gemini Only (Minimal)

The simplest setup - just Python and a free Gemini API key.

| Feature | Available | Notes |
|---------|-----------|-------|
| `devmind document` | Yes | Generate AI assistant docs |
| `devmind scan` | Yes | Security scanning (OSV database) |
| `devmind review` | Yes | Code review |
| `devmind test` | Yes | Test generation |
| `devmind generate-pr` | Yes | Requires `gh` CLI |
| Multi-format output | Yes | All 10 formats |
| Local file output | Yes | `devmind-output/` |

**Limitations:**
- No persistence (results not saved)
- No background jobs
- Simple/moderate task complexity only

---

### CLI + Claude (Complex Tasks)

Add Claude for tasks requiring deep reasoning.

| Feature | Available | Notes |
|---------|-----------|-------|
| Everything above | Yes | |
| Complex security analysis | Yes | Claude handles nuanced vulnerabilities |
| Advanced code review | Yes | Better context understanding |
| Exploitability analysis | Yes | More accurate threat assessment |

**When Claude is used:**
- Security reviewer (COMPLEX)
- Correctness reviewer (COMPLEX)
- Test strategist (MODERATE/COMPLEX)
- Code review synthesis (COMPLEX)

---

### CLI + All AI Providers

Maximum LLM flexibility with Gemini, Claude, and OpenAI.

| Feature | Available | Notes |
|---------|-----------|-------|
| Everything above | Yes | |
| Automatic failover | Yes | Falls back if one provider fails |
| Cost optimization | Yes | Routes simple tasks to cheaper models |
| Provider comparison | Yes | Test outputs across providers |

---

### Full Stack (with PostgreSQL)

Add a database for persistence and history.

| Feature | Available | Notes |
|---------|-----------|-------|
| Everything above | Yes | |
| Scan history | Yes | Track vulnerabilities over time |
| Review history | Yes | See past code reviews |
| User accounts | Yes | Authentication & authorization |
| Organization management | Yes | Multi-tenant support |
| Repository tracking | Yes | Monitor multiple repos |
| Audit logs | Yes | Track all actions |
| Health scores | Yes | Repository quality metrics |
| Trend analysis | Yes | Improvement over time |

**Database Models:**
- `User` - User accounts
- `Organization` - Team management
- `Repository` - Tracked repos with config
- `PRReview` - Code review results
- `VulnerabilityScan` - Scan jobs
- `Vulnerability` - Individual findings

---

### Full Stack (with Redis)

Add Redis for caching and background jobs.

| Feature | Available | Notes |
|---------|-----------|-------|
| Everything above | Yes | |
| LLM response caching | Yes | Faster repeat queries |
| Background jobs | Yes | Async scan/review execution |
| Job queues | Yes | Celery worker support |
| Rate limiting | Yes | Per-user/org limits |
| Session storage | Yes | User sessions |

**Background Job Types:**
- PR reviews (async)
- Vulnerability scans (async)
- Batch documentation generation
- Webhook processing

---

### Full Stack (with Qdrant)

Add Qdrant for vector search and semantic indexing.

| Feature | Available | Notes |
|---------|-----------|-------|
| Everything above | Yes | |
| Semantic code search | Yes | Find similar code patterns |
| ADR indexing | Yes | Search architecture decisions |
| Documentation search | Yes | Natural language queries |
| Similar vulnerability search | Yes | Find related CVEs |
| Context retrieval | Yes | RAG for better LLM responses |

**Vector Collections:**
- Code embeddings
- Documentation embeddings
- ADR embeddings
- Vulnerability descriptions

---

### Full Stack (with GitHub App)

Add GitHub App for automated workflows.

| Feature | Available | Notes |
|---------|-----------|-------|
| Everything above | Yes | |
| Auto PR review | Yes | Review on PR open/update |
| Bot commands | Yes | `/devmind review`, `/devmind scan` |
| Check runs | Yes | GitHub status checks |
| PR comments | Yes | Inline review comments |
| Webhook handling | Yes | Event-driven automation |
| Private repo access | Yes | App installation grants access |

**Supported Events:**
- `pull_request.opened`
- `pull_request.synchronize`
- `issue_comment.created` (bot commands)

---

## Quick Reference: What Do I Need?

| Use Case | Minimum Setup |
|----------|---------------|
| Generate AI docs for a project | CLI + Gemini |
| Security scan with severity check | CLI + Gemini |
| Complex code review | CLI + Claude |
| CI/CD integration | CLI + any LLM |
| Track scan history | + PostgreSQL |
| Background processing | + PostgreSQL + Redis |
| Semantic search across ADRs | + Qdrant |
| Automated PR reviews | + GitHub App |
| Enterprise multi-tenant | Full stack |

---

## Setup Scripts Summary

| Script | Components | Best For |
|--------|------------|----------|
| `setup-cli-gemini.sh` | CLI + Gemini | Quick start, free |
| `setup-cli-claude.sh` | CLI + Gemini + Claude | Complex analysis |
| `setup-cli-full.sh` | CLI + all LLMs + GitHub | CI/CD integration |
| `setup-docker.sh` | Full Docker stack | Production deployment |
| `setup-api.sh` | API + Docker infra | Development |

---

## Cost Considerations

| Component | Cost |
|-----------|------|
| Gemini | Free tier available (60 RPM) |
| Claude | Pay per token (~$3/M input, $15/M output) |
| OpenAI | Pay per token (~$2.50/M input, $10/M output) |
| PostgreSQL | Free (self-hosted) or ~$15/mo (managed) |
| Redis | Free (self-hosted) or ~$10/mo (managed) |
| Qdrant | Free (self-hosted) or cloud pricing |

**Recommendation:** Start with CLI + Gemini (free), add Claude for complex tasks, add infrastructure as needed.
