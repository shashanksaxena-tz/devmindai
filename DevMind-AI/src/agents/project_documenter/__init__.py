"""Project Documenter Agent - Generates AI-agent documentation for existing codebases.

This agent analyzes codebases and generates documentation in multiple formats:
- CLAUDE.md for Claude Code
- .github/copilot-instructions.md for GitHub Copilot
- .cursor/rules/*.mdc for Cursor AI
- GEMINI.md for Google Gemini Code Assist
- .windsurf/rules/*.md for Windsurf/Codeium
- .specify/memory/constitution.md for GitHub Spec Kit
- Human-readable documentation (README, architecture docs)
- AI-CONTEXT.md and README.md per-folder documentation (NEW)
"""

from .agent import ProjectDocumenterAgent
from .analyzer import CodebaseAnalyzer, CodebaseProfile
from .generators.base import BaseDocGenerator, GeneratedDoc
from .output_manager import OutputManager

# Per-folder documentation components
from .folder_analyzer import FolderAnalyzer, FolderInfo
from .smart_merger import SmartMerger, Section, SectionType
from .metadata_manager import MetadataManager, FolderMetadata
from .per_folder_generator import PerFolderGenerator
from .index_builder import IndexBuilder

__all__ = [
    "ProjectDocumenterAgent",
    "CodebaseAnalyzer",
    "CodebaseProfile",
    "BaseDocGenerator",
    "GeneratedDoc",
    "OutputManager",
    # Per-folder components
    "FolderAnalyzer",
    "FolderInfo",
    "SmartMerger",
    "Section",
    "SectionType",
    "MetadataManager",
    "FolderMetadata",
    "PerFolderGenerator",
    "IndexBuilder",
]

