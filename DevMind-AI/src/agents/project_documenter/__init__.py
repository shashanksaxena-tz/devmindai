"""Project Documenter Agent - Generates AI-agent documentation for existing codebases.

This agent analyzes codebases and generates documentation in multiple formats:
- CLAUDE.md for Claude Code
- .github/copilot-instructions.md for GitHub Copilot
- .cursor/rules/*.mdc for Cursor AI
- GEMINI.md for Google Gemini Code Assist
- .windsurf/rules/*.md for Windsurf/Codeium
- .specify/memory/constitution.md for GitHub Spec Kit
- Human-readable documentation (README, architecture docs)
"""

from .agent import ProjectDocumenterAgent
from .analyzer import CodebaseAnalyzer, CodebaseProfile
from .generators.base import BaseDocGenerator, GeneratedDoc
from .output_manager import OutputManager

__all__ = [
    "ProjectDocumenterAgent",
    "CodebaseAnalyzer",
    "CodebaseProfile",
    "BaseDocGenerator",
    "GeneratedDoc",
    "OutputManager",
]
