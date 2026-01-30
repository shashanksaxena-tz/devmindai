# Project Documenter Agent

Generate AI-ready documentation for any codebase. This agent analyzes existing projects and creates documentation optimized for AI coding assistants like Claude, GitHub Copilot, Cursor, Gemini, and Windsurf.

## Quick Start

```bash
# Navigate to the DevMind-AI directory
cd DevMind-AI

# Install dependencies
pip install -e ".[cli,dev]"

# Generate AI documentation for any project
devmind document /path/to/your/project -w
```

## Installation

### Prerequisites

- Python 3.9+
- pip

### Setup

1. **Clone and navigate to the project:**
   ```bash
   git clone <repository-url>
   cd devmindai/DevMind-AI
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -e ".[cli,dev]"
   ```

4. **Set up environment variables:**
   Create a `.env` file in the `DevMind-AI` directory:
   ```bash
   # Required for LLM-based features
   ANTHROPIC_API_KEY=your-anthropic-key
   GOOGLE_API_KEY=your-google-key

   # Optional (defaults work for basic usage)
   APP_NAME="DevMind AI"
   APP_ENV=development
   DEBUG=True
   SECRET_KEY=your-secret-key
   ```

   > **Note:** For basic analysis without LLM features, you can use dummy keys.

## Usage

### Basic Commands

```bash
# Analyze a project and display documentation (no files written)
devmind document /path/to/project

# Generate and write AI documentation to disk
devmind document /path/to/project -w

# Analyze current directory
devmind document .

# Only analyze (no documentation generation)
devmind document /path/to/project --analyze
```

### Selecting Output Formats

By default, the agent generates documentation for all AI coding assistants.

```bash
# Generate all AI formats (default)
devmind document . -w

# Generate specific formats only
devmind document . -f claude -f copilot -w

# Generate ALL formats including human docs and Spec Kit
devmind document . --all -w

# Include GitHub Spec Kit constitution
devmind document . --speckit -w

# Include human-readable documentation
devmind document . --human -w
```

### Available Formats

| Format | Files Generated | Purpose |
|--------|-----------------|---------|
| `claude` | `CLAUDE.md` | Claude Code context |
| `copilot` | `.github/copilot-instructions.md` | GitHub Copilot instructions |
| `cursor` | `.cursor/rules/*.mdc` | Cursor AI rules |
| `gemini` | `GEMINI.md` | Google Gemini Code Assist |
| `windsurf` | `.windsurf/rules/*.md`, `.windsurfrules.md` | Windsurf/Codeium rules |
| `speckit` | `.specify/memory/constitution.md` | GitHub Spec Kit governance |
| `human` | `docs/README.generated.md`, `docs/ARCHITECTURE.md`, `docs/CONTRIBUTING.md` | Human documentation |

### Output Format

```bash
# Text output (default)
devmind document .

# JSON output (for programmatic use)
devmind document . --output-format json
```

## Examples

### Example 1: Document a Python Project

```bash
# Clone a sample project
git clone https://github.com/tiangolo/fastapi.git
cd fastapi

# Generate AI documentation
devmind document . -w

# Check generated files
ls -la CLAUDE.md GEMINI.md .github/copilot-instructions.md
ls -la .cursor/rules/
```

### Example 2: Document a JavaScript/TypeScript Project

```bash
# Clone a sample project
git clone https://github.com/expressjs/express.git
cd express

# Generate documentation for specific AI tools
devmind document . -f copilot -f cursor -w

# Check generated files
cat .github/copilot-instructions.md
ls .cursor/rules/
```

### Example 3: Generate GitHub Spec Kit Constitution

```bash
# For a project using spec-driven development
devmind document . --speckit -w

# Check the constitution
cat .specify/memory/constitution.md
```

### Example 4: Full Documentation Suite

```bash
# Generate everything - AI docs, human docs, and governance
devmind document . --all -w

# This creates:
# - CLAUDE.md
# - GEMINI.md
# - .github/copilot-instructions.md
# - .cursor/rules/*.mdc
# - .windsurf/rules/*.md
# - .specify/memory/constitution.md
# - docs/README.generated.md
# - docs/ARCHITECTURE.md
# - docs/CONTRIBUTING.md
```

### Example 5: Analyze Without Generating

```bash
# Just see what the agent detects about your project
devmind document . --analyze

# Output includes:
# - Detected language and frameworks
# - Project structure
# - Build/test/lint commands
# - Code style conventions
# - Existing documentation
```

## API Usage

The Project Documenter is also available via REST API.

### Start the API Server

```bash
cd DevMind-AI
uvicorn src.api.main:app --reload
```

### API Endpoints

```bash
# Analyze a project
curl -X POST http://localhost:8000/api/project-docs/analyze \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/project"}'

# Generate documentation
curl -X POST http://localhost:8000/api/project-docs/generate \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/path/to/project",
    "formats": ["claude", "copilot", "cursor"],
    "write_files": true
  }'

# List available formats
curl http://localhost:8000/api/project-docs/formats

# Preview a specific format
curl "http://localhost:8000/api/project-docs/doc/claude/preview?path=/path/to/project"
```

## Programmatic Usage

```python
import asyncio
from src.agents.project_documenter import ProjectDocumenterAgent
from src.agents.base import AgentContext

async def generate_docs():
    agent = ProjectDocumenterAgent()
    context = AgentContext()

    # Generate documentation
    result = await agent.execute(
        context,
        path="/path/to/your/project",
        formats=["claude", "copilot", "cursor", "gemini", "windsurf"],
        write_files=True,
    )

    print(f"Generated {len(result['generated_docs'])} documentation files")
    print(f"Formats: {result['formats_generated']}")

    # Access the analyzed profile
    profile = result['profile']
    print(f"Language: {profile['primary_language']}")
    print(f"Frameworks: {profile['frameworks']}")

asyncio.run(generate_docs())
```

### Analyze Only

```python
async def analyze_only():
    agent = ProjectDocumenterAgent()

    # Just analyze without generating docs
    profile = await agent.analyze_only("/path/to/project")

    print(f"Project: {profile.name}")
    print(f"Language: {profile.primary_language}")
    print(f"Frameworks: {profile.frameworks}")
    print(f"Test command: {profile.test_commands}")

asyncio.run(analyze_only())
```

## What Each Format Provides

### CLAUDE.md (Claude Code)
Concise context file with:
- Project overview and tech stack
- Key directories and their purposes
- Build/test/lint commands
- Coding conventions and guidelines
- Important files to reference

### .github/copilot-instructions.md (GitHub Copilot)
Natural language instructions including:
- Project context and architecture
- Coding standards
- Testing requirements
- Security considerations

### .cursor/rules/*.mdc (Cursor AI)
Multiple rule files with frontmatter:
- `index.mdc` - Always-applied project rules
- `{language}.mdc` - Language-specific guidelines
- `testing.mdc` - Testing conventions
- `api.mdc` - API development rules (if applicable)
- Framework-specific rules

### GEMINI.md (Google Gemini)
Structured context file with:
- Project identity and goals
- Architecture overview
- Development guidelines
- Testing and quality standards

### .windsurf/rules/*.md (Windsurf/Codeium)
Rule files including:
- `global_rules.md` - Project-wide rules
- Language and framework-specific rules

### .specify/memory/constitution.md (GitHub Spec Kit)
Governance document with articles covering:
- Project identity
- Code quality standards
- Testing requirements
- Documentation requirements
- Security requirements
- Architecture constraints
- Development workflow

## Troubleshooting

### Import Errors
```bash
# Ensure PYTHONPATH includes the project
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

### Missing API Keys
For basic analysis, you can use placeholder keys:
```bash
export ANTHROPIC_API_KEY=dummy
export GOOGLE_API_KEY=dummy
```
Note: LLM-generated content (guidelines, descriptions) will be limited without valid keys.

### Permission Errors
Ensure you have write permissions to the target directory when using `-w` flag.

## Running Tests

```bash
cd DevMind-AI

# Set up environment
export PYTHONPATH=$PYTHONPATH:$(pwd)
export ANTHROPIC_API_KEY=dummy
export GOOGLE_API_KEY=dummy
export SECRET_KEY=dummy

# Run tests
pytest tests/agents/project_documenter/ -v
```

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## License

See the project's LICENSE file.
