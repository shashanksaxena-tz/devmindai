"""Documentation generators for various AI tools and formats."""

from .base import BaseDocGenerator, GeneratedDoc
from .claude import ClaudeDocGenerator
from .copilot import CopilotDocGenerator
from .cursor import CursorDocGenerator
from .gemini import GeminiDocGenerator
from .windsurf import WindsurfDocGenerator
from .speckit import SpecKitGenerator
from .human import HumanDocGenerator
from .aider import AiderDocGenerator
from .cline import ClineDocGenerator
from .opencode import OpenCodeDocGenerator

__all__ = [
    "BaseDocGenerator",
    "GeneratedDoc",
    "ClaudeDocGenerator",
    "CopilotDocGenerator",
    "CursorDocGenerator",
    "GeminiDocGenerator",
    "WindsurfDocGenerator",
    "SpecKitGenerator",
    "HumanDocGenerator",
    "AiderDocGenerator",
    "ClineDocGenerator",
    "OpenCodeDocGenerator",
]
