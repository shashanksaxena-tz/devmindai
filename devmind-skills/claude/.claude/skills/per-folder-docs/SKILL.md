---
name: per-folder-docs
description: Generate deep, inter-linked AI-CONTEXT.md and README.md for individual code folders. Supports incremental updates, version tracking, and deep code analysis.
---

# Per-Folder Documentation Skill

You are a **Technical Architect** and **Documentation Engineer**. Your goal is to create "Source of Truth" documentation that allows an AI to understand a module *without* reading its source code again.

## Core Philosophy

- **Depth over Breadth**: Don't just list files. Explain *how* they work together.
- **AI-First**: The `AI-CONTEXT.md` is for *you* (the future AI). Pack it with types, signatures, and architectural nuances.
- **Human-Friendly**: The `README.md` is for developers. Focus on usage, examples, and "mental models".
- **Living Documents**: Use version tracking to only update what has changed.

## Execution Strategy

### Phase 0: incremental Check (Crucial)

1.  **Locate Metadata**: Look for `.devmind/doc-metadata.json` in the project root.
2.  **Check Version**:
    *   If the file exists, read the `last_commit_hash` for the target folder.
    *   Run `git diff --name-only {stored_hash} HEAD -- {target_folder}` (if inside a git repo).
    *   **IF** no changes are detected AND the user didn't use `--force`, **SKIP** generation for this folder. Return early.
3.  **Capture Current State**:
    *   Get current commit hash: `git rev-parse HEAD`.
    *   Keep this for the update step at the end.

### Phase 1: Deep Discovery & Analysis

**Do not guess.** You must read the code.

1.  **Map the Territory**:
    *   `list_dir` to see the structure.
    *   Identify key files: Entry points (`index.ts`, `main.go`, `__init__.py`), Core Logic, Types/Models.

2.  **Deep Read (The "Credit Heavy" Step)**:
    *   Read *all* interface definitions / type files.
    *   Read the implementation of complex business logic.
    *   Trace imports to understand dependencies.
    *   **Goal**: Understand the *Data Flow* and *Control Flow*.

3.  **Synthesize**:
    *   **Abstract Schema**: What are the core entities? (User, Transaction, GraphNode)
    *   **Public API**: What methods are exposed? What are their inputs/outputs?
    *   **Internal State**: Does this module manage state? How?
    *   **Gotchas**: What are the edge cases? (e.g., "This function is not thread-safe").

### Phase 2: Document Generation

#### File 1: `AI-CONTEXT.md` ( The Brain)

This file replaces the need to read the source code.

```markdown
<!-- AUTO-GENERATED: Header -->
# {Folder Name} Module Context
**Version**: {commit_hash}
**Generated**: {timestamp}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Architecture -->
## 🧠 Architectural Mental Model

### Core Responsibility
{Deep explanation of what this module *actually* does. Not "Handles logic", but "Manages the state machine for user onboarding, enforcing valid transitions and persisting side-effects to the DB".}

### Design Patterns
- **Pattern Name**: Usage context (e.g., "Singleton used for DB connection to ensure pool limit").
- **Dependency Injection**: How dependencies are provided.

### Data Flow
1. Input enters via `Controller.handle()`
2. Validated by `SchemaValidator`
3. Transformed by `Transformer.toDomain()`
4. Persisted via `Repository`
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Type System -->
## 🧬 Type Definitions / Models

> **Note**: Critical type definitions that define the shape of data in this module.

```typescript
// Important Check: Only include *exported* or *critical* types.
interface UserState {
  id: string;
  status: 'active' | 'pending'; // State machine is strict here
  metadata: Record<string, any>; // Flexible payload
}
```
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: API -->
## 🔌 Public Interfaces

### `Service.method(arg)`
- **Input**: `ComplexType`
- **Output**: `Promise<Result>`
- **Behavior**: 
  - Validates X.
  - Throws `ValidationError` if Y.
  - **Side Effect**: Emits 'user.created' event.
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Dependencies -->
## 🔗 Dependencies & Linking

- **Internal**:
  - [Auth Module](../auth/AI-CONTEXT.md) - Used for verifying tokens (see `middleware.ts`).
  - [Database](../db/AI-CONTEXT.md) - Data persistence layer.
- **External**:
  - `lodash` - Utility functions.
  - `zod` - Runtime validation.
<!-- END AUTO-GENERATED -->

<!-- CUSTOM SECTION: Insight -->
## 💡 Developer Insights

{Area for manual notes about "Here be dragons" or historical context}
<!-- END CUSTOM SECTION -->
```

#### File 2: `README.md` (The Guide)

```markdown
<!-- AUTO-GENERATED: Header -->
# {Folder Name}
> {One line high-level summary}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Overview -->
## Overview
{Human-readable explanation. Use analogies if helpful. Explain the "Why".}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Usage -->
## 🚀 Usage

### Installation / Setup
```bash
# If applicable
npm install @scope/module
```

### Basic Example
```python
# Real, runnable example code
from module import Service

svc = Service(config)
result = svc.do_work()
```
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: API Reference -->
## 📚 API Summary

| Method | Description |
|--------|-------------|
| `init()` | Initializes the connection pool |
| `process()` | Main entry point for batch processing |
<!-- END AUTO-GENERATED -->

<!-- CUSTOM SECTION: Troubleshooting -->
## 🔧 Troubleshooting

{Manual section for common issues}
<!-- END CUSTOM SECTION -->
```

### Phase 3: Metadata Update

1.  **Read** `.devmind/doc-metadata.json` (create if missing).
2.  **Update** the entry for the current folder:
    ```json
    {
      "version": "1.1",
      "modules": {
        "src/path/to/folder": {
          "last_commit": "7b3f1...",
          "generated_at": "2024-03-20T10:00:00Z",
          "file_count": 15,
          "hash": "internal_content_hash"
        }
      }
    }
    ```
3.  **Write** the file back.

## Handling "Superficiality"

- **Forbidden Phrases**: "Contains logic", "Standard implementation", "Helper functions".
- **Required Depth**:
  - If a file is `utils.ts`, list *every* utility function and what it solves.
  - If a file is `types.ts`, paste the core schemas.
  - If a file is `api.ts`, explain the error handling strategy used in the endpoints.

## Large Project Strategy

For projects with >50 folders:
1.  **Map first**: Run a high-level scan to build a dependency graph.
2.  **Leaf Nodes First**: Document the "utils" and "models" first, as other modules link to them.
3.  **Core Second**: Document the business logic services.
4.  **Controllers Last**: Document the API entry points (which depend on everything else).

## Arguments

- `$1` (Path): Target directory.
- `--force`: Ignore version checks and regenerate.
- `--recursive`: Document all subfolders appropriately.
- `--deep`: Enable "Credit Heavy" full-file reading mode (Recommended for first run).
