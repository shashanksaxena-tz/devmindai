---
name: per-folder-docs
description: Generate AI-CONTEXT.md and README.md for individual code folders to provide module-level documentation. Use this when asked to document folders, create module docs, or add AI context to subdirectories.
---

# Per-Folder Documentation Skill

You are a **technical writer** creating module-level documentation that helps AI assistants understand specific parts of the codebase.

## Execution Strategy

### Phase 1: Folder Discovery

Identify folders that should be documented:

#### Include (Priority Scoring)
| Pattern | Priority | Score |
|---------|----------|-------|
| Has `__init__.py` (Python package) | High | +3 |
| Has 3+ source files | High | +3 |
| Contains `main`, `index`, or entry point | High | +3 |
| Has `models`, `services`, `api` in name | High | +2 |
| Has subdirectories | Medium | +1 |
| Single file with > 200 lines | Medium | +1 |

**Document folders with score ≥ 3**

#### Exclude (Always Skip)
```
node_modules/
__pycache__/
.git/
.venv/
venv/
dist/
build/
coverage/
.next/
.cache/
*.egg-info/
```

### Phase 2: Folder Analysis

For each folder, analyze:

1. **Purpose**
   - What is this module's responsibility?
   - Why does it exist?
   - What problem does it solve?

2. **Contents**
   - Key files and their roles
   - Classes and functions (public API)
   - Constants and configuration

3. **Dependencies**
   - What does this module import?
   - What external libraries are used?

4. **Consumers**
   - What other modules import from here?
   - Who are the primary consumers?

5. **Patterns**
   - Design patterns used
   - Coding conventions specific to this module
   - Testing patterns

### Phase 3: Document Generation

#### File 1: AI-CONTEXT.md

Create AI-specific context for each folder:

```markdown
<!-- AUTO-GENERATED: Header -->
# {folder_name}

{One-line description of what this module does}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Purpose -->
## Purpose

{2-3 sentences explaining:}
- What this module does
- Why it exists
- Its role in the larger system
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Key Files -->
## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | Package exports, public API |
| `models.py` | Database models for X |
| `service.py` | Business logic for Y |
| `exceptions.py` | Custom exceptions |
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Public API -->
## Public API

### Classes

```python
class UserService:
    """Handles user management operations."""
    
    def create_user(self, data: UserCreate) -> User:
        """Create a new user."""
        
    def get_user(self, user_id: int) -> User | None:
        """Get user by ID."""
        
    def update_user(self, user_id: int, data: UserUpdate) -> User:
        """Update existing user."""
```

### Functions

```python
def validate_email(email: str) -> bool:
    """Validate email format."""

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
```
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Dependencies -->
## Dependencies

### Internal
- `../core/config` - Configuration settings
- `../database/session` - Database session management
- `../models/user` - User model definition

### External
- `sqlalchemy` - ORM
- `pydantic` - Validation
- `bcrypt` - Password hashing
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Used By -->
## Used By

- `../api/routes/users.py` - User API endpoints
- `../cli/commands/user.py` - CLI user commands
- `../tasks/notifications.py` - User notification tasks
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Patterns -->
## Patterns & Conventions

### Repository Pattern
This module uses the repository pattern:
```python
class UserRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, id: int) -> User | None:
        return self.session.query(User).get(id)
```

### Error Handling
- Raise `UserNotFoundError` for missing users
- Raise `ValidationError` for invalid data
- Log all errors before raising

### Testing
- Mock `UserRepository` in service tests
- Use factories for test data: `UserFactory`
<!-- END AUTO-GENERATED -->

<!-- CUSTOM SECTION: Project-Specific Notes -->
## Notes

Add project-specific notes here. This section is preserved during regeneration.

{User can add custom documentation here that won't be overwritten}
<!-- END CUSTOM SECTION -->

<!-- AUTO-GENERATED: Examples -->
## Usage Examples

### Creating a User
```python
from src.services.users import UserService

service = UserService(db_session)
user = service.create_user(UserCreate(
    email="user@example.com",
    name="John Doe"
))
```

### Querying Users
```python
# Get single user
user = service.get_user(user_id=1)

# List users with filters
users = service.list_users(
    status="active",
    limit=10
)
```
<!-- END AUTO-GENERATED -->
```

#### File 2: README.md (Human-Focused)

```markdown
<!-- AUTO-GENERATED: Header -->
# {Folder Name}

{Brief description for human readers}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Overview -->
## Overview

{More detailed explanation of:}
- What this module does
- How it fits in the project
- Key features and capabilities
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Structure -->
## Structure

```
{folder_name}/
├── __init__.py      # Public exports
├── models.py        # Data models
├── service.py       # Business logic
├── repository.py    # Data access
├── exceptions.py    # Custom exceptions
└── utils.py         # Helper functions
```
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Quick Start -->
## Quick Start

```python
from src.{folder_name} import {MainClass}

instance = MainClass()
result = instance.do_something(input_data)
```
<!-- END AUTO-GENERATED -->

<!-- CUSTOM SECTION: Additional Info -->
## Additional Information

{Space for custom documentation}
<!-- END CUSTOM SECTION -->

<!-- AUTO-GENERATED: Related -->
## Related Modules

- [`../models/`](../models/) - Database models
- [`../api/`](../api/) - API endpoints
<!-- END AUTO-GENERATED -->
```

### Phase 4: Smart Merging

When regenerating documentation, preserve custom sections:

#### Section Markers
```html
<!-- AUTO-GENERATED: SectionName -->
This content will be regenerated
<!-- END AUTO-GENERATED -->

<!-- CUSTOM SECTION: SectionName -->
This content will be PRESERVED
<!-- END CUSTOM SECTION -->
```

#### Merge Algorithm
```python
def smart_merge(existing: str, generated: str) -> str:
    """
    1. Parse existing document for CUSTOM SECTION blocks
    2. Extract and store custom content
    3. Parse generated document
    4. Replace CUSTOM SECTION placeholders with preserved content
    5. Return merged document
    """
```

### Phase 5: Index Generation

Update top-level documentation with navigation:

```markdown
## Module Index

| Module | Description |
|--------|-------------|
| [`src/api/`](src/api/AI-CONTEXT.md) | API endpoint definitions |
| [`src/models/`](src/models/AI-CONTEXT.md) | Database models |
| [`src/services/`](src/services/AI-CONTEXT.md) | Business logic |
| [`src/utils/`](src/utils/AI-CONTEXT.md) | Utility functions |
```

## Output Format

```markdown
# Per-Folder Documentation Generated

**Project:** {project_name}
**Folders Documented:** {count}

## Generated Files

| Folder | AI-CONTEXT.md | README.md | Custom Preserved |
|--------|---------------|-----------|------------------|
| src/api/ | ✅ Created | ✅ Created | N/A (new) |
| src/models/ | ✅ Updated | ✅ Updated | 2 sections |
| src/services/ | ✅ Created | ✅ Created | N/A (new) |
| src/utils/ | ⏭️ Skipped | ⏭️ Skipped | Empty folder |

## Summary

- New folders documented: 8
- Updated folders: 3
- Custom sections preserved: 5
- Folders skipped: 2 (below threshold)

## Top-Level Updates

- CLAUDE.md: Added module index
- README.md: Updated project structure
```

## Incremental Mode

Use incremental mode for large projects:

```bash
/per-folder-docs --incremental
```

This will:
1. Check `.devmind/doc-metadata.json` for cached hashes
2. Only regenerate folders with changed files
3. Update metadata after successful generation

### Metadata Format
```json
{
  "version": "1.0",
  "generated_at": "2025-02-03T14:00:00Z",
  "folders": {
    "src/api/": {
      "hash": "abc123...",
      "last_generated": "2025-02-03T14:00:00Z",
      "files_count": 5
    }
  }
}
```

## Handling Large Codebases

For projects with many folders:

```markdown
## ⚠️ Partial Generation

Documented: 15/35 folders

**Completed:**
- ✅ src/api/ (5 files)
- ✅ src/models/ (8 files)
- ✅ src/services/ (12 files)

**Remaining:**
- ⏳ src/cli/ (3 files)
- ⏳ src/utils/ (7 files)
- ⏳ tests/ (20+ files)

**Continue:** `/per-folder-docs --continue`

**Priority Mode:** `/per-folder-docs --priority-only` (only high-priority folders)
```

## Arguments

- `$1` - Path to document (default: current directory)
- `--incremental` - Only update changed folders
- `--force` - Regenerate all folders
- `--dry-run` - Show what would be generated
- `--priority-only` - Only document high-priority folders
- `--continue` - Continue from checkpoint
- `--no-readme` - Skip README.md generation
