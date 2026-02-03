# DevMind Skills - Polyglot & Deep Context Refactoring

## Summary

Refactored the DevMind AI skills to be **tech-stack agnostic**, **deeply analytical**, and **self-maintaining**.

## 1. 🗑 Cleanup & Focus
- **Removed**: `copilot/`, `cursor/`, and `opencode/` folders.
- **Consolidated**: All intelligence is now centered in the `claude/` skills, which serve as the universal standard for all agents (including Gemini/Copilot/OpenCode).

## 2. 🧠 New Skill: Deep Context Generation (`per-folder-docs`)

The `per-folder-docs` skill has been completely rewritten to solve the "superficiality" problem.

| Feature | Old Behavior | New Behavior |
|---------|--------------|--------------|
| **Depth** | Listed files and basic purpose | **Reads source code** to extract data flow, state machines, and API contracts |
| **Context** | Generic descriptions | **Architectural Mental Models**, Type definitions, and Dependency linking |
| **Logic** | "What is this?" | "How does this work?" + "Why does it exist?" |
| **Update** | Overwrote everything | **Incremental**: Checks `git diff` against metadata JSON to only update changed modules |
| **Linking** | None | Explicit relative links to other `AI-CONTEXT.md` files |

### Artifacts Generated
1.  **`AI-CONTEXT.md`**: The "Brain". Dense, technical, architecture-focused.
2.  **`README.md`**: The "Guide". Human-focused, usage-oriented.
3.  **`.devmind/doc-metadata.json`**: Tracks commit hashes to enable smart incremental updates.

## 3. � New Skill: Project Mapping (`document-project`)

The root-level documentation skill was also upgraded.

- **`CLAUDE.md`**: Now serves as a "Context Window" root, defining the map of the territory and linking to deep module docs.
- **`ARCHITECTURE.md`**: Explicitly extracts system-level diagrams (Mermaid), data flows, and security boundaries.
- **Navigation**: Creates a clear path from Root -> Module -> File.

## 4. 🌍 Universal Language Support
(From previous iteration)
- **Java/C#**: Added specific testing and documentation templates.
- **Go/Python/TS**: Enhanced existing templates.
- **Auto-Detection**: Skills now inspect the codebase to decide which language patterns to apply.

## Usage

To generate the new deep documentation:

```bash
# 1. Generate the Project Map
/document-project

# 2. Generate Deep Module Docs (First run might take time due to deep reading)
/per-folder-docs --deep

# 3. Update later (Fast)
/per-folder-docs --incremental
```

## Verification
You can verify the depth by running `/per-folder-docs` on a complex module (like `backend/tax-engine-service`). The agent is now instructed to read the code logic, not just file names.
