---
name: per-folder-docs
description: Generate per-folder AI-CONTEXT.md and README.md documentation for better AI assistant context
tags: [documentation, ai-context, devmind-skill]
version: 1.0.0
created: 2026-02-02
---

# Per-Folder Documentation Skill

## Purpose

Generate detailed per-folder documentation (AI-CONTEXT.md + README.md) for any codebase to give AI assistants (Claude, Copilot, Gemini) better context when working in specific modules.

## When to Use This Skill

✅ **Use when**:
- Setting up a new project for AI assistant work
- After major refactoring (regenerate affected folders)
- When onboarding AI assistants to specific modules
- Adding new features in isolated folders
- Documentation is superficial or non-existent per folder

❌ **Don't use when**:
- Only need top-level project documentation
- Working on very small projects (<5 files)
- Documentation already exists and is comprehensive

## Quick Start

### For Claude, Copilot, Gemini, or Any AI

When asked to "generate per-folder documentation" or "create AI context files":

```bash
# Navigate to DevMind-AI project root
cd /path/to/DevMind-AI

# Run full generation (all folders, all formats)
poetry run devmind document /path/to/target/project -w

# Incremental (only changed folders)
poetry run devmind document /path/to/target/project -w --incremental
```

## How It Works

### Architecture

**Four Core Components**:

1. **FolderAnalyzer** (`folder_analyzer.py`)
   - Scans project directory tree
   - Filters code folders (excludes `__pycache__`, `venv`, etc.)
   - Scores folders by significance
   - Returns prioritized list

2. **PerFolderGenerator** (`per_folder_generator.py`)
   - Analyzes folder contents
   - Uses LLM to generate intelligent content
   - Creates AI-CONTEXT.md (conventions, patterns)
   - Creates README.md (overview, examples)

3. **SmartMerger** (`smart_merger.py`)
   - Parses marker comments in files
   - Preserves custom user sections
   - Updates auto-generated sections
   - Handles files without markers

4. **MetadataManager** (`metadata_manager.py`)
   - Tracks content hashes (SHA256)
   - Detects changed folders
   - Enables incremental regeneration
   - Stores in `.devmind/doc-metadata.json`

### Generated File Structure

```
project/
├── CLAUDE.md                    (enhanced with module index)
├── README.md                    (enhanced with folder structure)
├── .devmind/
│   └── doc-metadata.json        (change tracking)
├── src/
│   ├── AI-CONTEXT.md           ← AI-specific context
│   ├── README.md               ← Human-friendly docs
│   ├── agents/
│   │   ├── AI-CONTEXT.md
│   │   ├── README.md
│   │   └── code_reviewer/
│   │       ├── AI-CONTEXT.md
│   │       └── README.md
│   └── api/
│       ├── AI-CONTEXT.md
│       └── README.md
```

### File Content Structure

**AI-CONTEXT.md Template**:
```markdown
# Module Name - AI Context

<!-- AUTO-GENERATED: Purpose - DO NOT EDIT -->
## Purpose
2-3 sentences describing module purpose
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Key Files - DO NOT EDIT -->
## Key Files
- `file1.py` - Purpose and main classes
- `file2.py` - Responsibilities
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Coding Conventions - DO NOT EDIT -->
## Coding Conventions
- Naming: snake_case for functions
- Patterns: All agents inherit BaseAgent
- Error Handling: Raise ValueError for invalid inputs
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Common Patterns - DO NOT EDIT -->
## Common Patterns

### Pattern: Creating an Agent
\`\`\`python
class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="my-agent")
\`\`\`
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Testing Approach - DO NOT EDIT -->
## Testing Approach
- Test Location: `tests/module/test_*.py`
- Run Tests: `pytest tests/module/`
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Integration Points - DO NOT EDIT -->
## Integration Points
- Imports From: src.core, src.utils
- Used By: src.api.routes
<!-- END AUTO-GENERATED -->

<!-- CUSTOM SECTION: You can add notes below -->
## Additional Notes
[Your custom content - preserved across regenerations]
<!-- END CUSTOM SECTION -->
```

**README.md Template**:
```markdown
# Module Name

<!-- AUTO-GENERATED: Overview - DO NOT EDIT -->
## Overview
What this module does (2-3 paragraphs)
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Key Components - DO NOT EDIT -->
## Key Components
- **Component 1** - Description
- **Component 2** - Description
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Usage Examples - DO NOT EDIT -->
## Usage Examples

### Example 1: Common Use Case
\`\`\`python
# Code example
\`\`\`
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Related Documentation - DO NOT EDIT -->
## Related Documentation
- [Parent Module](../README.md)
- [Related Module](../api/README.md)
<!-- END AUTO-GENERATED -->

<!-- CUSTOM SECTION: You can add notes below -->
## Additional Information
[Your custom content]
<!-- END CUSTOM SECTION -->
```

## Usage Modes

### Mode 1: Full Generation

Generate docs for ALL code folders:

```bash
poetry run devmind document /path/to/project -w
```

**When to use**: First-time setup, major refactoring, comprehensive refresh

### Mode 2: Incremental Updates

Only regenerate CHANGED folders:

```bash
poetry run devmind document /path/to/project -w --incremental
```

**When to use**: After code changes, regular maintenance, fast updates

### Mode 3: Selective Generation

Choose specific aspects:

```bash
# Skip per-folder docs (only top-level)
poetry run devmind document /path/to/project -w --no-per-folder

# Specific AI formats
poetry run devmind document /path/to/project -w -f claude -f copilot

# Force regenerate (ignore metadata)
poetry run devmind document /path/to/project -w --force

# Write directly to project (not devmind-output/)
poetry run devmind document /path/to/project -w --to-project
```

## For AI Assistants: Using Generated Docs

### Workflow When Editing Code

**Step 1**: Before editing any file, check for `AI-CONTEXT.md` in that folder

```bash
# Example: Before editing src/agents/code_reviewer/analyzer.py
cat src/agents/code_reviewer/AI-CONTEXT.md
```

**Step 2**: Read and internalize:
- Purpose of this module
- Coding conventions
- Common patterns
- Testing approach
- Integration points

**Step 3**: Make changes following learned conventions

**Step 4**: If you've added significant patterns, suggest updating CUSTOM SECTION

### Example AI Workflow

```python
# BEFORE reading AI-CONTEXT.md:
# ❌ Might use inconsistent naming
def ProcessData(input):  # Wrong: PascalCase for function
    return input

# AFTER reading AI-CONTEXT.md:
# ✅ Follows module conventions
def process_data(input_data: dict) -> dict:
    """Process data following module conventions.

    Args:
        input_data: Input dictionary

    Returns:
        Processed data dictionary
    """
    return input_data
```

## Customizing Generated Docs

### Adding Custom Content

Edit any generated file and add content in CUSTOM SECTION blocks:

```markdown
<!-- CUSTOM SECTION: Team Guidelines -->
## Team Guidelines

Our team prefers:
- Use type hints for all functions
- Write docstrings for public APIs
- Keep functions under 50 lines
- Use descriptive variable names

**Security Note**: Never log sensitive data in this module.
<!-- END CUSTOM SECTION -->
```

**IMPORTANT**: Custom content is preserved across regenerations!

### Regenerating with Preservation

```bash
# Smart merge keeps your custom sections
poetry run devmind document /path/to/project -w --incremental
```

The `SmartMerger` will:
- ✅ Update AUTO-GENERATED sections with new content
- ✅ Preserve all CUSTOM SECTION content exactly
- ✅ Maintain section order
- ✅ Handle new/removed sections gracefully

## Implementation Details

### Location

```
DevMind-AI/src/agents/project_documenter/
├── agent.py                    # ProjectDocumenterAgent
├── analyzer.py                 # Codebase analysis
├── folder_analyzer.py          # Folder identification ⭐
├── per_folder_generator.py     # Content generation ⭐
├── smart_merger.py             # Content preservation ⭐
├── metadata_manager.py         # Change tracking ⭐
├── output_manager.py           # Output organization
└── generators/
    ├── base.py
    ├── claude.py
    ├── copilot.py
    └── ...
```

### Key Classes

**FolderInfo** (`folder_analyzer.py`):
```python
@dataclass
class FolderInfo:
    path: Path              # Absolute path
    relative_path: Path     # Relative to project root
    score: int             # Priority score (0-20+)
    file_count: int        # Number of source files
    has_subfolders: bool   # Has documented subfolders
    primary_language: str  # Detected language
```

**FolderAnalyzer** (`folder_analyzer.py`):
```python
class FolderAnalyzer:
    EXCLUDED_PATTERNS = [
        "__pycache__", "venv", ".git", "node_modules", ...
    ]

    def analyze_folders(self, project_path: Path) -> List[FolderInfo]:
        """Returns sorted list of folders (highest score first)"""
```

**SmartMerger** (`smart_merger.py`):
```python
class SmartMerger:
    def merge(self, existing: str, new_content: str) -> str:
        """Merge new content while preserving custom sections"""
```

**MetadataManager** (`metadata_manager.py`):
```python
class MetadataManager:
    def has_folder_changed(self, folder_path: Path) -> bool:
        """Check if folder content has changed"""

    def update_folder(self, folder_path: Path, file_count: int) -> None:
        """Update metadata after generation"""
```

### Testing

```bash
# Run all project_documenter tests
cd DevMind-AI
poetry run pytest tests/agents/project_documenter/ -v

# Run specific component tests
poetry run pytest tests/agents/project_documenter/test_folder_analyzer.py -v
poetry run pytest tests/agents/project_documenter/test_smart_merger.py -v
poetry run pytest tests/agents/project_documenter/test_metadata_manager.py -v

# Run end-to-end tests
poetry run pytest tests/agents/project_documenter/test_e2e_per_folder.py -v
```

## Troubleshooting

### Issue: Folders Excluded That Shouldn't Be

**Symptom**: Important folders not getting documented

**Solution**:
```python
# Check FolderAnalyzer.EXCLUDED_PATTERNS
# May need to adjust patterns in folder_analyzer.py

# Workaround: Remove folder from exclusion list
# or ensure folder has source code files
```

### Issue: Custom Content Lost During Regeneration

**Symptom**: Manual edits disappear after running command

**Solution**:
```markdown
# Ensure content is in CUSTOM SECTION blocks
<!-- CUSTOM SECTION: My notes -->
Your custom content here
<!-- END CUSTOM SECTION -->

# NOT this (will be overwritten):
## My Notes
Your custom content here
```

### Issue: Incremental Mode Not Detecting Changes

**Symptom**: `--incremental` flag regenerates nothing when files changed

**Solution**:
```bash
# Check metadata file
cat .devmind/doc-metadata.json

# If corrupted, delete and regenerate
rm .devmind/doc-metadata.json
poetry run devmind document /path/to/project -w --force
```

### Issue: LLM Content Quality Poor

**Symptom**: Generated docs are generic or incorrect

**Solution**:
```python
# Per-folder generation uses MODERATE complexity
# which routes to Gemini Pro or Claude Haiku

# If quality is poor, can temporarily adjust in:
# src/agents/project_documenter/per_folder_generator.py

# Or use better model in LLM router settings
```

### Issue: Generation Too Slow

**Symptom**: Takes minutes for large projects

**Solution**:
```bash
# Use incremental mode
poetry run devmind document /path/to/project -w --incremental

# Or limit scope
poetry run devmind document /path/to/project/src/specific_module -w

# Or skip per-folder docs
poetry run devmind document /path/to/project -w --no-per-folder
```

## Advanced: Programmatic Usage

### Python API

```python
from pathlib import Path
from src.agents.project_documenter import ProjectDocumenterAgent
from src.agents.base import AgentContext

async def generate_docs():
    agent = ProjectDocumenterAgent()
    context = AgentContext()

    result = await agent.execute(
        context,
        path="/path/to/project",
        formats=["claude", "copilot"],
        write_files=True,
        per_folder_docs=True,
        incremental=True,
        output_to_project=True,
    )

    print(f"Generated {result['folder_docs_count']} folder docs")
    print(f"Written files: {result['written_files']}")

# Run
import asyncio
asyncio.run(generate_docs())
```

### Custom Folder Selection

```python
from src.agents.project_documenter.folder_analyzer import FolderAnalyzer

analyzer = FolderAnalyzer()
folders = analyzer.analyze_folders(Path("/project"))

# Filter by score
high_priority = [f for f in folders if f.score >= 10]

# Filter by language
python_folders = [f for f in folders if f.primary_language == "python"]

# Filter by path pattern
api_folders = [f for f in folders if "api" in str(f.relative_path)]
```

## Related Documentation

- **Design Doc**: `docs/plans/2026-02-02-per-folder-documentation-design.md`
- **Implementation Plan**: `docs/plans/2026-02-02-per-folder-docs-implementation.md`
- **Agent README**: `src/agents/project_documenter/README.md`
- **Main README**: `README.md` (Project Documenter section)
- **Claude Instructions**: `CLAUDE.md` (Project Documenter section)

## Version History

- **v1.0.0** (2026-02-02): Initial release
  - FolderAnalyzer for smart folder detection
  - PerFolderGenerator with LLM integration
  - SmartMerger for content preservation
  - MetadataManager for change tracking
  - CLI integration with incremental mode

## Credits

Created as part of DevMind AI - Multi-Agent Developer Platform

**Contributors**: Claude + DevMind Team

**License**: Same as DevMind AI project
