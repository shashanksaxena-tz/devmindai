# DevMind-AI Architecture
**Last Updated:** 2026-01-20

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DevMind-AI Platform                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         FastAPI Application                          │   │
│  │                        (src/api/main.py)                             │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │  │   /health   │  │  /reviews   │  │  /security  │  │   /tests    │ │   │
│  │  └─────────────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘ │   │
│  └──────────────────────────┼────────────────┼────────────────┼────────┘   │
│                             │                │                │             │
│  ┌──────────────────────────┼────────────────┼────────────────┼────────┐   │
│  │                        Agent Layer                                   │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │  │CodeReviewer │  │VulnScanner  │  │TestGenerator│  │DebtAnalyzer │ │   │
│  │  │ (6 sub-     │  │ (OSV DB,    │  │ (Analyzer,  │  │ (Complexity,│ │   │
│  │  │  reviewers) │  │  analysis)  │  │  Generator) │  │  Duplication│ │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────────────┘ │   │
│  └─────────┼────────────────┼────────────────┼─────────────────────────┘   │
│            │                │                │                              │
│  ┌─────────┴────────────────┴────────────────┴─────────────────────────┐   │
│  │                         LLM Router (src/core/llm/)                   │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │   │
│  │  │    Claude       │  │     Gemini      │  │     OpenAI      │      │   │
│  │  │ (COMPLEX tasks) │  │ (SIMPLE tasks)  │  │   (fallback)    │      │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
        ▼                             ▼                             ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│  PostgreSQL   │          │     Redis     │          │    Qdrant     │
│   (Metadata)  │          │    (Queue)    │          │   (Vectors)   │
└───────────────┘          └───────────────┘          └───────────────┘
```

---

## Component Details

### 1. API Layer (`src/api/`)

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app initialization, CORS, lifespan |
| `deps.py` | Dependency injection (DB sessions) |
| `routes/reviews.py` | CodeReviewer API endpoints |
| `routes/security.py` | VulnScanner API endpoints |
| `routes/tests.py` | TestGenerator API endpoints |
| `schemas/` | Pydantic request/response models |

### 2. Agent Layer (`src/agents/`)

#### BaseAgent (`base.py`)
Abstract base providing:
- LLM client access via router
- `execute()` method (override in subclasses)
- `generate()` / `generate_structured()` helpers
- Error handling wrapper via `run()`

#### VulnScanner (`vuln_scanner/`)
```
vuln_scanner/
├── agent.py          # Main VulnScannerAgent class
├── parsers/          # NPM, Pip dependency parsers
├── vuln_db/          # OSV (Open Source Vulnerabilities) client
└── analyzer/         # Exploitability analysis
```

#### CodeReviewer (`code_reviewer/`)
```
code_reviewer/
├── orchestrator.py   # Runs reviewers in parallel
├── synthesizer.py    # Combines results, prioritizes
├── context_gatherer.py # Fetches PR context from GitHub
├── diff_parser.py    # Parses unified diffs
└── reviewers/        # 6 specialized reviewers
    ├── security.py
    ├── performance.py
    ├── correctness.py
    ├── style.py
    ├── testing.py
    └── documentation.py
```

#### TestGenerator (`test_generator/`)
```
test_generator/
├── agent.py       # Main TestGeneratorAgent
├── analyzer.py    # Code structure analysis
├── strategist.py  # Test strategy planning
├── generator.py   # Test code generation
├── validator.py   # Syntax validation
└── coverage.py    # Coverage gap finder
```

### 3. Core Layer (`src/core/`)

| Component | Purpose |
|-----------|---------|
| `config.py` | Pydantic settings from environment |
| `llm/` | LLM clients (Claude, Gemini, OpenAI) + Router |
| `auth/` | JWT authentication scaffolding |

### 4. Data Layer (`src/db/`)

| Model | Purpose |
|-------|---------|
| `Repository` | Registered repositories with config |
| `PRReview` | Code review results |
| `VulnerabilityScan` | Scan job records |
| `Vulnerability` | Individual CVE findings |

### 5. Integrations (`src/integrations/`)

| Integration | Purpose |
|-------------|---------|
| `github.py` | PyGitHub wrapper for PR/file access |

---

## Data Flow Examples

### Code Review Flow
```
1. POST /api/v1/reviews/repos/{repo_id}/review
   └── Creates job, returns job_id
   
2. Background Task:
   ├── ContextGatherer.gather_pr_context()  # Fetch PR metadata
   ├── GitHubClient.get_pr_files()          # Get changed files
   ├── For each file:
   │   └── ReviewOrchestrator.review_file()
   │       ├── SecurityReviewer.review()    # Claude
   │       ├── PerformanceReviewer.review() # Claude
   │       ├── StyleReviewer.review()       # Gemini
   │       └── ... (parallel)
   ├── ReviewSynthesizer.synthesize()       # Combine & prioritize
   └── Save PRReview to database
   
3. GET /api/v1/reviews/jobs/{job_id}/status
   └── Returns: completed/failed + results
```

### Vulnerability Scan Flow
```
1. POST /api/v1/security/{repo_id}/scan
   └── Creates VulnerabilityScan record
   
2. Background Task:
   ├── Load repo local_path from config
   ├── VulnScannerAgent.execute()
   │   ├── Parse package-lock.json / requirements.txt
   │   ├── Query OSV database for each package
   │   ├── (Optional) Analyze exploitability
   │   └── Generate remediation advice
   └── Save Vulnerability records

3. GET /api/v1/security/{repo_id}/vulns
   └── Returns filtered vulnerability list
```

---

## LLM Routing Strategy

| Task Complexity | LLM Used | Examples |
|-----------------|----------|----------|
| SIMPLE | Gemini | Style review, documentation check |
| MODERATE | Claude | Test generation, synthesis |
| COMPLEX | Claude | Security analysis, correctness |

The router (`src/core/llm/router.py`) selects the appropriate client based on the agent's declared `complexity` attribute.

---

## Configuration

All configuration via environment variables (see `.env.example`):

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-xxx    # For Claude
GOOGLE_API_KEY=xxx              # For Gemini
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://...

# Optional
GITHUB_TOKEN=xxx                # For private repo access
OPENAI_API_KEY=xxx             # Fallback LLM
```
