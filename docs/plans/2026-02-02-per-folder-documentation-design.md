# Per-Folder Documentation Generator - Design Document

**Date**: 2026-02-02
**Author**: Claude + User
**Status**: Approved - Ready for Implementation

## Problem Statement

The current Project Documenter Agent generates a single top-level README that is superficial and doesn't provide AI coding assistants (Claude, Copilot, Gemini, etc.) with the detailed, per-module context they need to understand and work effectively in different parts of the codebase.

## Solution Overview

Enhance the Project Documenter Agent to generate **two-tier documentation**:
1. **Project-level docs** (existing) - High-level overview with navigation index
2. **Per-folder docs** (new) - Module-specific context and guidelines

## Design Goals

- ✅ Generate AI-optimized context files per folder
- ✅ Generate human-readable README per folder
- ✅ Smart folder selection (only code folders, skip noise)
- ✅ Smart regeneration (preserve custom content)
- ✅ Navigation index in top-level docs
- ✅ Minimal disruption to existing codebase

## Architecture

### Two-Tier Documentation System

**Tier 1: Project-Level Documentation**
- Existing: `CLAUDE.md`, `README.md`, `COPILOT.md`, etc.
- Enhancement: Auto-generated **Documentation Index** section
- Purpose: High-level overview + navigation to modules

**Tier 2: Folder-Level Documentation**
- New: `AI-CONTEXT.md` in each code folder
  - Coding conventions
  - Common patterns
  - Testing approaches
  - Integration points
- New: `README.md` in each code folder
  - Quick overview
  - Key components
  - Usage examples
  - Related docs

### Component Architecture

```
ProjectDocumenterAgent
├── FolderAnalyzer          (new)
│   └── Identifies which folders need docs
├── PerFolderGenerator      (new)
│   ├── Analyzes folder contents
│   ├── Generates AI-CONTEXT.md
│   └── Generates README.md
├── SmartMerger            (new)
│   └── Preserves custom content during regeneration
├── IndexBuilder           (new)
│   └── Updates top-level docs with navigation
└── (existing components)
    ├── CodebaseAnalyzer
    ├── OutputManager
    └── Format-specific generators
```

## Detailed Component Design

### 1. FolderAnalyzer

**Responsibility**: Determine which folders should be documented

**Algorithm**:
```python
def analyze_folders(project_path: Path) -> List[FolderInfo]:
    # 1. Scan directory tree
    # 2. Filter folders with source code
    # 3. Exclude noise (venv, __pycache__, etc.)
    # 4. Score folders by significance
    # 5. Return sorted list
```

**Exclusion Patterns**:
- `__pycache__`, `*.pyc`, `*.pyo`
- `venv`, `.venv`, `env`, `node_modules`
- `.git`, `.svn`, `.hg`
- `dist`, `build`, `target`, `out`
- `.pytest_cache`, `.mypy_cache`, `.tox`
- `coverage`, `.coverage`, `.nyc_output`

**Scoring System** (prioritizes generation order):
- +10: Contains package marker (`__init__.py`, `index.js`, etc.)
- +5: Contains 3+ source files
- +3: Has subdirectories with source code
- +2: Name indicates significance (`core`, `agents`, `api`, `services`, `lib`)
- +1: Contains tests

**Output**:
```python
@dataclass
class FolderInfo:
    path: Path              # Absolute path
    relative_path: Path     # Relative to project root
    score: int             # Priority score
    file_count: int        # Number of source files
    has_subfolders: bool   # Has documented subfolders
    primary_language: str  # Detected language
```

### 2. PerFolderGenerator

**Responsibility**: Generate AI-CONTEXT.md and README.md for a folder

**Input**: `FolderInfo` + `CodebaseProfile`

**AI-CONTEXT.md Template**:
```markdown
# {folder_name} - AI Context

<!-- AUTO-GENERATED: Purpose - DO NOT EDIT -->
## Purpose
{2-3 sentence description of module purpose}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Key Files - DO NOT EDIT -->
## Key Files
- `file1.py` - {Purpose and main classes/functions}
- `file2.py` - {Purpose and responsibilities}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Coding Conventions - DO NOT EDIT -->
## Coding Conventions
- **Naming**: {Conventions found in this module}
- **Patterns**: {Common patterns used here}
- **Error Handling**: {How errors are handled}
- **Async/Sync**: {Async patterns if applicable}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Common Patterns - DO NOT EDIT -->
## Common Patterns

### Pattern 1: {Pattern Name}
```python
{Code example from actual files}
```

### Pattern 2: {Pattern Name}
```python
{Code example from actual files}
```
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Testing Approach - DO NOT EDIT -->
## Testing Approach
- **Test Location**: `{path to tests}`
- **Run Tests**: `{command to run tests}`
- **Coverage**: `{coverage command if applicable}`
- **Common Mocks**: {Examples of mocks used}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Integration Points - DO NOT EDIT -->
## Integration Points
- **Imports From**: {Modules this depends on}
- **Used By**: {Modules that import this}
- **External Dependencies**: {Third-party packages}
<!-- END AUTO-GENERATED -->

<!-- CUSTOM SECTION: You can add notes below -->
## Additional Notes

<!-- END CUSTOM SECTION -->
```

**README.md Template**:
```markdown
# {folder_name}

<!-- AUTO-GENERATED: Overview - DO NOT EDIT -->
## Overview
{What this folder contains - 2-3 paragraphs}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Key Components - DO NOT EDIT -->
## Key Components

- **{Component 1}** - {Brief description}
- **{Component 2}** - {Brief description}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Usage Examples - DO NOT EDIT -->
## Usage Examples

### Example 1: {Common Use Case}
```python
{Practical code example}
```

### Example 2: {Common Use Case}
```python
{Practical code example}
```
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Related Documentation - DO NOT EDIT -->
## Related Documentation
- [Parent Module](../AI-CONTEXT.md)
- [Related Module 1]({path})
- [Related Module 2]({path})
<!-- END AUTO-GENERATED -->

<!-- CUSTOM SECTION: You can add notes below -->
## Additional Information

<!-- END CUSTOM SECTION -->
```

**LLM Prompting Strategy**:
- Use MODERATE complexity (Gemini Pro or Claude Haiku)
- Provide folder contents, file summaries, and project context
- Request specific examples from actual code
- Ask for conventions based on observed patterns

### 3. SmartMerger

**Responsibility**: Preserve custom content during regeneration

**Algorithm**:
```python
def merge_content(existing_file: str, new_content: str) -> str:
    # 1. Parse existing file for markers
    existing_sections = parse_markers(existing_file)

    # 2. Parse new content for markers
    new_sections = parse_markers(new_content)

    # 3. Merge intelligently
    result = []
    for section_name in all_sections:
        if section_name.startswith("AUTO-GENERATED"):
            result.append(new_sections[section_name])
        elif section_name.startswith("CUSTOM"):
            result.append(existing_sections.get(section_name, ""))

    return join_sections(result)
```

**Marker Format**:
```markdown
<!-- AUTO-GENERATED: {section_name} - DO NOT EDIT -->
{content}
<!-- END AUTO-GENERATED -->

<!-- CUSTOM SECTION: {description} -->
{user content - preserved}
<!-- END CUSTOM SECTION -->
```

**Edge Cases**:
- **No markers found**: Generate fresh file with markers
- **Corrupted markers**: Backup original, generate fresh with warning
- **New sections added**: Append at end with markers
- **Sections removed**: Keep custom content, remove auto-generated

**Backup Strategy**:
- Before first merge: Create `{filename}.backup`
- Store in `.devmind/` hidden folder
- Keep last 3 backups with timestamps

### 4. IndexBuilder

**Responsibility**: Update top-level docs with navigation index

**For CLAUDE.md** (and other AI format files):
```markdown
<!-- AUTO-GENERATED: Documentation Index -->
## 📚 Module Documentation

### Core Modules
- **[src/agents/](src/agents/AI-CONTEXT.md)** - {one-line description}
- **[src/api/](src/api/AI-CONTEXT.md)** - {one-line description}
- **[src/core/](src/core/AI-CONTEXT.md)** - {one-line description}

### Agent Implementations
- **[src/agents/project_documenter/](src/agents/project_documenter/AI-CONTEXT.md)** - {description}
- **[src/agents/code_reviewer/](src/agents/code_reviewer/AI-CONTEXT.md)** - {description}

### Testing
- **[tests/agents/](tests/agents/AI-CONTEXT.md)** - {description}

**💡 Tip**: When working in a specific module, read its AI-CONTEXT.md for detailed conventions and patterns.
<!-- END AUTO-GENERATED -->
```

**For README.md**:
```markdown
<!-- AUTO-GENERATED: Folder Structure -->
## 📂 Repository Structure

```
project/
├── src/
│   ├── agents/          → Agent implementations [📖 Docs](src/agents/README.md)
│   ├── api/             → API routes [📖 Docs](src/api/README.md)
│   └── core/            → Core utilities [📖 Docs](src/core/README.md)
└── tests/               → Test suite [📖 Docs](tests/README.md)
```

**Navigation**: Each folder contains detailed documentation. Click 📖 Docs links.
<!-- END AUTO-GENERATED -->
```

**Insertion Strategy**:
- Find existing "Project Structure" or "Architecture" section
- Insert index after that section
- If no suitable section found, insert after "Overview"
- Maintain existing marker if already present

## Change Tracking System

**Purpose**: Track which folders have changed to enable incremental regeneration

**Approach**: Metadata-based tracking with content hashing

### Tracking Metadata File

Location: `.devmind/doc-metadata.json`

```json
{
  "version": "1.0",
  "last_full_run": "2026-02-02T10:30:00Z",
  "project_root": "/path/to/project",
  "folders": {
    "src/agents": {
      "last_generated": "2026-02-02T10:30:00Z",
      "content_hash": "abc123def456",
      "file_count": 15,
      "files": {
        "base.py": "hash1",
        "agent.py": "hash2"
      }
    },
    "src/api": {
      "last_generated": "2026-02-02T10:30:00Z",
      "content_hash": "xyz789uvw012",
      "file_count": 8,
      "files": {
        "main.py": "hash3",
        "routes.py": "hash4"
      }
    }
  }
}
```

### Change Detection Algorithm

```python
def detect_changed_folders(project_path: Path) -> List[str]:
    metadata = load_metadata()
    changed = []

    for folder_path in all_documented_folders:
        current_hash = compute_folder_hash(folder_path)
        stored_hash = metadata.get("folders", {}).get(folder_path, {}).get("content_hash")

        if current_hash != stored_hash:
            changed.append(folder_path)

    return changed

def compute_folder_hash(folder_path: Path) -> str:
    """Hash all source files in folder"""
    file_hashes = []
    for file in sorted(folder_path.glob("*.py")):  # or other extensions
        content = file.read_text()
        file_hashes.append(hashlib.sha256(content.encode()).hexdigest())

    return hashlib.sha256("".join(file_hashes).encode()).hexdigest()
```

### Incremental Regeneration Flow

```python
async def execute(self, context, **kwargs):
    incremental = kwargs.get("incremental", False)

    if incremental:
        # 1. Load metadata
        metadata = MetadataManager.load()

        # 2. Detect changed folders
        all_folders = self.folder_analyzer.analyze_folders(path)
        changed_folders = detect_changed_folders(all_folders, metadata)

        # 3. Only regenerate changed folders
        folders_to_regenerate = changed_folders

        # 4. Update metadata for regenerated folders
        for folder in folders_to_regenerate:
            await self._generate_folder_docs(folder)
            metadata.update_folder(folder, new_hash)

        # 5. Rebuild index (always, since structure may change)
        await self._update_navigation_index()
    else:
        # Full regeneration (existing logic)
        ...
```

### Git-Based Tracking (Optional Enhancement)

For Git repositories, optionally use Git to detect changes:

```python
def get_changed_folders_from_git(since_commit: str = "HEAD~1") -> List[str]:
    """Get folders with changed files since a commit"""
    result = subprocess.run(
        ["git", "diff", "--name-only", since_commit],
        capture_output=True,
        text=True
    )

    changed_files = result.stdout.strip().split("\n")
    changed_folders = set(Path(f).parent for f in changed_files)

    return list(changed_folders)
```

**Hybrid Approach** (Recommended):
- Use metadata hashing as primary method (works without Git)
- If Git available, cross-reference with `git diff` for validation
- User can specify `--since-commit <commit>` for Git-based detection

## Integration with Existing Agent

### Modified ProjectDocumenterAgent

```python
class ProjectDocumenterAgent(BaseAgent):
    def __init__(self, router: LLMRouter | None = None):
        super().__init__(router)
        self.analyzer = CodebaseAnalyzer()

        # NEW components
        self.folder_analyzer = FolderAnalyzer()
        self.per_folder_generator = PerFolderGenerator(self.llm_client)
        self.smart_merger = SmartMerger()
        self.index_builder = IndexBuilder()
        self.metadata_manager = MetadataManager()

        # Existing generators...
        self._generators = {...}

    async def execute(self, context: AgentContext, **kwargs) -> dict:
        # 1. Existing: Analyze codebase
        profile = self.analyzer.analyze(path)

        # 2. Existing: Generate top-level docs
        generated_docs = []
        for format_name in formats:
            docs = await self._generators[format_name].generate(profile)
            generated_docs.extend(docs)

        # 3. NEW: Generate per-folder docs
        folder_docs = []
        if kwargs.get("per_folder_docs", True):
            # Analyze folders
            folders = self.folder_analyzer.analyze_folders(Path(path))

            # Detect changes for incremental mode
            if kwargs.get("incremental", False):
                metadata = self.metadata_manager.load(path)
                folders = self._filter_changed_folders(folders, metadata)

            # Generate docs for each folder
            for folder_info in folders:
                ai_context = await self.per_folder_generator.generate_ai_context(
                    folder_info, profile
                )
                readme = await self.per_folder_generator.generate_readme(
                    folder_info, profile
                )

                # Smart merge if files exist
                if (folder_info.path / "AI-CONTEXT.md").exists():
                    ai_context.content = self.smart_merger.merge(
                        existing=(folder_info.path / "AI-CONTEXT.md").read_text(),
                        new=ai_context.content
                    )

                if (folder_info.path / "README.md").exists():
                    readme.content = self.smart_merger.merge(
                        existing=(folder_info.path / "README.md").read_text(),
                        new=readme.content
                    )

                folder_docs.extend([ai_context, readme])

            # 4. Update top-level docs with navigation index
            for doc in generated_docs:
                if doc.format_name in ["claude", "copilot", "cursor", "gemini"]:
                    doc.content = self.index_builder.add_module_index(
                        doc.content, folders, link_to="AI-CONTEXT.md"
                    )
                elif doc.format_name == "human":
                    doc.content = self.index_builder.add_folder_structure(
                        doc.content, folders, link_to="README.md"
                    )

            generated_docs.extend(folder_docs)

            # 5. Update metadata
            if kwargs.get("write_files", False):
                self.metadata_manager.update_folders(path, folders)

        # 6. Write files (existing logic)
        if kwargs.get("write_files", False):
            written_files = await self._write_files(root_path, generated_docs)

        return {
            "success": True,
            "profile": profile_dict,
            "generated_docs": doc_list,
            "folder_docs_count": len(folder_docs),
            "written_files": written_files,
        }
```

### CLI Enhancements

```python
def document_command(
    path: Path = typer.Argument(...),
    formats: Optional[List[str]] = typer.Option(None, "--format", "-f"),
    write: bool = typer.Option(False, "--write", "-w"),

    # NEW OPTIONS
    per_folder: bool = typer.Option(
        True,
        "--per-folder/--no-per-folder",
        help="Generate per-folder documentation (AI-CONTEXT.md + README.md)"
    ),
    incremental: bool = typer.Option(
        False,
        "--incremental",
        help="Only regenerate changed folders (based on content hash)"
    ),
    force_regenerate: bool = typer.Option(
        False,
        "--force",
        help="Force regenerate all folders (ignore metadata)"
    ),
    since_commit: Optional[str] = typer.Option(
        None,
        "--since-commit",
        help="Regenerate folders with changes since Git commit (e.g., HEAD~1, main)"
    ),
):
    """
    Generate AI-agent documentation for a project.

    NEW: Per-folder documentation generates AI-CONTEXT.md and README.md
    in each code folder for better AI assistant and developer context.

    Examples:
        # Full generation with per-folder docs
        devmind document ./project -w

        # Skip per-folder docs
        devmind document ./project -w --no-per-folder

        # Incremental: only regenerate changed folders
        devmind document ./project -w --incremental

        # Force regenerate everything
        devmind document ./project -w --force

        # Regenerate folders changed since last commit
        devmind document ./project -w --since-commit HEAD~1
    """
    asyncio.run(run_document(
        path=path,
        formats=formats or ["claude", "copilot", "cursor", "gemini"],
        write_files=write,
        per_folder_docs=per_folder,
        incremental=incremental and not force_regenerate,
        force_regenerate=force_regenerate,
        since_commit=since_commit,
    ))
```

## File Structure After Generation

```
project/
├── CLAUDE.md                          (enhanced with index)
├── README.md                          (enhanced with folder structure)
├── .devmind/
│   ├── doc-metadata.json             (tracking metadata)
│   └── backups/                      (backup files)
│       ├── src_agents_AI-CONTEXT.md.backup
│       └── src_api_README.md.backup
├── src/
│   ├── AI-CONTEXT.md                 (NEW)
│   ├── README.md                     (NEW)
│   ├── agents/
│   │   ├── AI-CONTEXT.md            (NEW)
│   │   ├── README.md                (NEW)
│   │   ├── base.py
│   │   ├── project_documenter/
│   │   │   ├── AI-CONTEXT.md       (NEW)
│   │   │   ├── README.md           (NEW)
│   │   │   ├── agent.py
│   │   │   └── analyzer.py
│   │   └── code_reviewer/
│   │       ├── AI-CONTEXT.md       (NEW)
│   │       ├── README.md           (NEW)
│   │       └── agent.py
│   ├── api/
│   │   ├── AI-CONTEXT.md            (NEW)
│   │   ├── README.md                (NEW)
│   │   ├── main.py
│   │   └── routes/
│   │       ├── AI-CONTEXT.md       (NEW)
│   │       ├── README.md           (NEW)
│   │       └── agents.py
│   └── core/
│       ├── AI-CONTEXT.md            (NEW)
│       ├── README.md                (NEW)
│       ├── config.py
│       └── llm/
│           ├── AI-CONTEXT.md       (NEW)
│           ├── README.md           (NEW)
│           └── router.py
└── tests/
    ├── AI-CONTEXT.md                (NEW)
    ├── README.md                    (NEW)
    └── agents/
        ├── AI-CONTEXT.md            (NEW)
        ├── README.md                (NEW)
        └── test_code_reviewer.py
```

## Implementation Phases

### Phase 1: Core Infrastructure (Priority 1)
- [ ] Create `FolderAnalyzer` class
- [ ] Create `PerFolderGenerator` base class
- [ ] Create `SmartMerger` class with marker parsing
- [ ] Create `MetadataManager` class
- [ ] Add unit tests for each component

### Phase 2: Content Generation (Priority 1)
- [ ] Implement AI-CONTEXT.md generation with LLM
- [ ] Implement README.md generation with LLM
- [ ] Create prompt templates for folder analysis
- [ ] Test on sample folders

### Phase 3: Integration (Priority 2)
- [ ] Integrate components into `ProjectDocumenterAgent`
- [ ] Add per-folder generation to main workflow
- [ ] Implement incremental mode with change detection
- [ ] Add CLI options

### Phase 4: Navigation & Polish (Priority 2)
- [ ] Create `IndexBuilder` class
- [ ] Update top-level CLAUDE.md with module index
- [ ] Update top-level README.md with folder structure
- [ ] Add backups and safety checks

### Phase 5: Testing & Documentation (Priority 3)
- [ ] End-to-end tests on real projects
- [ ] Test incremental regeneration
- [ ] Test smart merge with custom content
- [ ] Update agent README and documentation

## Success Criteria

✅ **Functional Requirements**:
- Per-folder AI-CONTEXT.md generated with relevant conventions
- Per-folder README.md generated with clear overview
- Top-level docs include navigation index
- Smart merge preserves custom content
- Incremental mode only regenerates changed folders

✅ **Quality Requirements**:
- AI-CONTEXT.md contains actual code examples from folder
- README.md is concise and actionable
- Generated content follows project style
- No loss of custom edits during regeneration

✅ **Performance Requirements**:
- Full generation: <3 minutes for 50 folders
- Incremental: <30 seconds for 5 changed folders
- Memory efficient (process folders one at a time)

## Open Questions & Decisions

### Resolved
- ✅ File naming: `AI-CONTEXT.md` + `README.md` (universal, simple)
- ✅ Preservation: HTML comment markers with AUTO-GENERATED/CUSTOM sections
- ✅ Navigation: Auto-generated index in top-level docs
- ✅ Folder selection: Smart scoring system, exclude noise
- ✅ Change tracking: Metadata-based with optional Git integration

### Future Enhancements (Out of Scope)
- 🔮 Watch mode: Auto-regenerate on file changes
- 🔮 Diff view: Show what changed in regenerated docs
- 🔮 Custom templates: User-provided templates for docs
- 🔮 Multi-language support: Better handling of polyglot repos
- 🔮 Interactive mode: Ask user questions during generation

## References

- Current implementation: `src/agents/project_documenter/`
- Related issue: Per-folder documentation request
- Inspired by: Cursor .cursorrules, GitHub Copilot instructions

---

**Next Steps**: Begin Phase 1 implementation with `FolderAnalyzer` class.
