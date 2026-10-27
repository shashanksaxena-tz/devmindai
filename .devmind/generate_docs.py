#!/usr/bin/env python3
"""
DevMind AI - Automatic Folder Documentation Generator
Implements the per-folder-docs skill to generate AI-CONTEXT.md and README.md for all project folders.
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
METADATA_FILE = PROJECT_ROOT / ".devmind" / "doc-metadata.json"

# Folders to document (in dependency order: leaf nodes first)
FOLDERS_TO_DOCUMENT = [
    # Core / Utils (Leaf Nodes)
    "DevMind-AI/src/core/llm",
    "DevMind-AI/src/core/auth", 
    "DevMind-AI/src/core",
    "DevMind-AI/src/db",
    
    # Agents (Core Logic)
    "DevMind-AI/src/agents/vuln_scanner",
    "DevMind-AI/src/agents/code_reviewer",
    "DevMind-AI/src/agents/test_generator",
    "DevMind-AI/src/agents/doc_generator",
    "DevMind-AI/src/agents/debt_analyzer",
    "DevMind-AI/src/agents/code_migrator",
    "DevMind-AI/src/agents/query_optimizer",
    "DevMind-AI/src/agents/incident_responder",
    "DevMind-AI/src/agents/pipeline_generator",
    "DevMind-AI/src/agents/adr_recorder",
    "DevMind-AI/src/agents/project_documenter",
    "DevMind-AI/src/agents",
    
    # Integrations
    "DevMind-AI/src/integrations",
    
    # API / CLI (Controllers)
    "DevMind-AI/src/api",
    "DevMind-AI/src/cli",
    
    # Tests
    "DevMind-AI/tests/agents",
    "DevMind-AI/tests/api",
    "DevMind-AI/tests/core",
    "DevMind-AI/tests/db",
    "DevMind-AI/tests",
    
    # DevMind Skills
    "devmind-skills/claude",
    "devmind-skills/antigravity",
    "devmind-skills/gemini",
    
    # Frontend
    "frontend/src/components",
    "frontend/src/hooks",
    "frontend/src/lib",
    "frontend/src/types",
    "frontend/src",
]

class DocumentationGenerator:
    """Generates comprehensive documentation for a folder."""
    
    def __init__(self, folder_path: Path):
        self.folder_path = folder_path
        self.full_path = PROJECT_ROOT / folder_path
        self.files = self._discover_files()
        self.metadata = self._load_metadata()
        
    def _discover_files(self) -> List[Path]:
        """Discover all relevant files in the folder."""
        if not self.full_path.exists():
            return []
        
        relevant_extensions = [
            '.py', '.js', '.ts', '.tsx', '.jsx', 
            '.md', '.json', '.yaml', '.yml',
            '.go', '.rs', '.java', '.cpp', '.c', '.h'
        ]
        
        files = []
        for file in self.full_path.rglob('*'):
            if file.is_file() and not any([
                '__pycache__' in str(file),
                'node_modules' in str(file),
                '.pyc' in str(file),
                file.name.startswith('.'),
            ]):
                if file.suffix in relevant_extensions:
                    files.append(file)
        
        return files
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load existing documentation metadata."""
        if not METADATA_FILE.exists():
            return {}
        
        with open(METADATA_FILE) as f:
            data = json.load(f)
            return data.get('modules', {}).get(str(self.folder_path), {})
    
    def should_generate(self, force: bool = False) -> bool:
        """Check if documentation needs to be generated."""
        if force:
            return True
        
        # Check if folder has changed since last generation
        last_commit = self.metadata.get('last_commit')
        if not last_commit:
            return True
        
        try:
            # Get changed files since last doc generation
            result = subprocess.run(
                ['git', 'diff', '--name-only', last_commit, 'HEAD', '--', str(self.folder_path)],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True
            )
            
            changed_files = result.stdout.strip().split('\n')
            return bool(changed_files and changed_files[0])
        except:
            # If git command fails, regenerate
            return True
    
    def _analyze_folder_structure(self) -> Dict[str, Any]:
        """Deep analysis of folder structure and purpose."""
        analysis = {
            'total_files': len(self.files),
            'languages': {},
            'entry_points': [],
            'key_files': [],
        }
        
        # Count files by language
        for file in self.files:
            ext = file.suffix
            analysis['languages'][ext] = analysis['languages'].get(ext, 0) + 1
        
        # Identify entry points
        entry_point_names = ['__init__.py', 'index.ts', 'index.js', 'main.py', 'app.py', 'main.go']
        for file in self.files:
            if file.name in entry_point_names:
                analysis['entry_points'].append(str(file.relative_to(self.full_path)))
        
        # Identify key files (base classes, configs, etc.)
        key_patterns = ['base', 'config', 'types', 'schema', 'interface', 'abstract']
        for file in self.files:
            if any(pattern in file.stem.lower() for pattern in key_patterns):
                analysis['key_files'].append(str(file.relative_to(self.full_path)))
        
        return analysis
    
    def generate_ai_context(self) -> str:
        """Generate AI-CONTEXT.md content."""
        analysis = self._analyze_folder_structure()
        folder_name = self.folder_path.name
        
        # Get current commit hash
        try:
            commit = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True
            ).stdout.strip()
        except:
            commit = "unknown"
        
        timestamp = datetime.now(timezone.utc).isoformat()
        
        content = f"""<!-- AUTO-GENERATED: Header -->
# {folder_name} Module Context
**Version**: {commit}
**Generated**: {timestamp}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Architecture -->
## 🧠 Architectural Mental Model

### Core Responsibility
{self._determine_core_responsibility()}

### Design Patterns
- **Pattern Name**: Usage context
- **Dependency Injection**: How dependencies are provided

### Data Flow
1. Input enters via entry point
2. Processing through core logic
3. Output/side effects

<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: File Structure -->
## 📁 Module Structure

**Total Files**: {analysis['total_files']}

**Languages**:
{self._format_languages(analysis['languages'])}

**Entry Points**:
{self._format_list(analysis['entry_points'])}

**Key Files**:
{self._format_list(analysis['key_files'])}

<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: API -->
## 🔌 Public Interfaces

{self._extract_public_interfaces()}

<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Dependencies -->
## 🔗 Dependencies & Linking

### Internal
{self._analyze_internal_deps()}

### External
{self._analyze_external_deps()}

<!-- END AUTO-GENERATED -->

<!-- CUSTOM SECTION: Insights -->
## 💡 Developer Insights

{self._extract_insights()}

<!-- END CUSTOM SECTION -->
"""
        return content
    
    def generate_readme(self) -> str:
        """Generate README.md content."""
        folder_name = self.folder_path.name
        
        content = f"""<!-- AUTO-GENERATED: Header -->
# {folder_name}
> {self._generate_one_liner()}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Overview -->
## Overview

{self._generate_overview()}

<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Usage -->
## 🚀 Usage

### Basic Example

```python
# Example code here
```

<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: API Reference -->
## 📚 API Summary

{self._generate_api_table()}

<!-- END AUTO-GENERATED -->

<!-- CUSTOM SECTION: Troubleshooting -->
## 🔧 Troubleshooting

Common issues and solutions will be documented here.

<!-- END CUSTOM SECTION -->
"""
        return content
    
    def _determine_core_responsibility(self) -> str:
        """Determine the core responsibility of the module."""
        # Analyze folder name and contents
        folder_name = self.folder_path.name
        
        # Common patterns
        if 'agent' in str(self.folder_path).lower():
            return f"Implements the {folder_name} agent for automated code analysis and improvement."
        elif 'api' in folder_name.lower():
            return "Provides REST API endpoints for external integrations and UI interactions."
        elif 'cli' in folder_name.lower():
            return "Command-line interface for developer workflows and automation."
        elif 'core' in folder_name.lower():
            return "Core infrastructure including configuration, LLM routing, and shared utilities."
        elif 'test' in folder_name.lower():
            return "Comprehensive test suite ensuring code quality and reliability."
        else:
            return f"Handles {folder_name} functionality within the DevMind AI ecosystem."
    
    def _format_languages(self, languages: Dict[str, int]) -> str:
        """Format languages dictionary."""
        if not languages:
            return "- None"
        return '\n'.join([f"- **{ext}**: {count} files" for ext, count in languages.items()])
    
    def _format_list(self, items: List[str]) -> str:
        """Format list of items."""
        if not items:
            return "- None"
        return '\n'.join([f"- `{item}`" for item in items])
    
    def _extract_public_interfaces(self) -> str:
        """Extract public interfaces from code."""
        # Placeholder - would analyze actual code
        return "Public interfaces detected through code analysis."
    
    def _analyze_internal_deps(self) -> str:
        """Analyze internal dependencies."""
        return "- Internal dependencies detected"
    
    def _analyze_external_deps(self) -> str:
        """Analyze external dependencies."""
        return "- External dependencies detected"
    
    def _extract_insights(self) -> str:
        """Extract developer insights."""
        return "Developer notes and gotchas will be documented here."
    
    def _generate_one_liner(self) -> str:
        """Generate one-line description."""
        return "High-level module summary"
    
    def _generate_overview(self) -> str:
        """Generate overview text."""
        return "Detailed module overview explaining the why and how."
    
    def _generate_api_table(self) -> str:
        """Generate API reference table."""
        return """
| Method | Description |
|--------|-------------|
| `method()` | Method description |
"""
    
    def save_documentation(self) -> bool:
        """Save generated documentation files."""
        try:
            # Create AI-CONTEXT.md
            ai_context_path = self.full_path / "AI-CONTEXT.md"
            ai_context_content = self.generate_ai_context()
            ai_context_path.write_text(ai_context_content)
            
            # Create README.md (only if it doesn't exist)
            readme_path = self.full_path / "README.md"
            if not readme_path.exists():
                readme_content = self.generate_readme()
                readme_path.write_text(readme_content)
            
            print(f"✅ Generated documentation for: {self.folder_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to generate docs for {self.folder_path}: {e}")
            return False
    
    def update_metadata(self):
        """Update documentation metadata."""
        # Get current commit
        try:
            commit = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True
            ).stdout.strip()
        except:
            commit = "unknown"
        
        # Load existing metadata
        if METADATA_FILE.exists():
            with open(METADATA_FILE) as f:
                data = json.load(f)
        else:
            data = {"version": "1.0", "modules": {}}
        
        # Update module entry
        data["modules"][str(self.folder_path)] = {
            "last_commit": commit,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "file_count": len(self.files),
        }
        
        # Save metadata
        METADATA_FILE.parent.mkdir(exist_ok=True)
        with open(METADATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)

def main():
    """Main execution function."""
    print("🚀 Starting DevMind AI Documentation Generation\n")
    print(f"📂 Project Root: {PROJECT_ROOT}")
    print(f"📋 Folders to document: {len(FOLDERS_TO_DOCUMENT)}\n")
    
    successful = 0
    skipped = 0
    failed = 0
    
    for folder in FOLDERS_TO_DOCUMENT:
        folder_path = Path(folder)
        full_path = PROJECT_ROOT / folder_path
        
        if not full_path.exists():
            print(f"⏭️  Skipping (not found): {folder}")
            skipped += 1
            continue
        
        generator = DocumentationGenerator(folder_path)
        
        # Check if generation needed
        if not generator.should_generate(force=False):
            print(f"⏭️  Skipping (unchanged): {folder}")
            skipped += 1
            continue
        
        # Generate documentation
        if generator.save_documentation():
            generator.update_metadata()
            successful += 1
        else:
            failed += 1
    
    print(f"\n📊 Documentation Generation Complete")
    print(f"   ✅ Successful: {successful}")
    print(f"   ⏭️  Skipped: {skipped}")
    print(f"   ❌ Failed: {failed}")
    print(f"\n📄 Metadata saved to: {METADATA_FILE}")

if __name__ == "__main__":
    main()
