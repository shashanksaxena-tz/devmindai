"""Per-folder documentation generator."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Optional

from .folder_analyzer import FolderInfo
from .generators.base import GeneratedDoc

if TYPE_CHECKING:
    from src.core.llm import BaseLLMClient
    from .analyzer import CodebaseProfile


class PerFolderGenerator:
    """Generates per-folder documentation (AI-CONTEXT.md and README.md)."""

    # Source code extensions
    SOURCE_EXTENSIONS = {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs"}

    def __init__(self, llm_client: BaseLLMClient):
        """Initialize generator.

        Args:
            llm_client: LLM client for content generation
        """
        self.llm_client = llm_client

    async def generate_ai_context(
        self, folder_info: FolderInfo, profile: CodebaseProfile
    ) -> GeneratedDoc:
        """Generate AI-CONTEXT.md for a folder.

        Args:
            folder_info: Information about the folder
            profile: Codebase profile for context

        Returns:
            GeneratedDoc with AI-CONTEXT.md content
        """
        # Read folder contents
        folder_contents = self._analyze_folder_contents(folder_info.path)

        # Build prompt
        prompt = self._build_ai_context_prompt(folder_info, profile, folder_contents)

        # Generate content with LLM
        try:
            generated_content = await self.llm_client.generate(
                prompt, max_tokens=2000
            )
        except Exception:
            generated_content = ""

        # Wrap in template with markers
        full_content = self._wrap_ai_context_template(
            folder_info.relative_path.name, generated_content, folder_contents
        )

        return GeneratedDoc(
            path=str(folder_info.relative_path / "AI-CONTEXT.md"),
            content=full_content,
            format_name="per_folder",
            description=f"AI context for {folder_info.relative_path}",
        )

    async def generate_readme(
        self, folder_info: FolderInfo, profile: CodebaseProfile
    ) -> GeneratedDoc:
        """Generate README.md for a folder.

        Args:
            folder_info: Information about the folder
            profile: Codebase profile for context

        Returns:
            GeneratedDoc with README.md content
        """
        # Read folder contents
        folder_contents = self._analyze_folder_contents(folder_info.path)

        # Build prompt
        prompt = self._build_readme_prompt(folder_info, profile, folder_contents)

        # Generate content with LLM
        try:
            generated_content = await self.llm_client.generate(
                prompt, max_tokens=1500
            )
        except Exception:
            generated_content = ""

        # Wrap in template with markers
        full_content = self._wrap_readme_template(
            folder_info.relative_path.name, generated_content, folder_contents
        )

        return GeneratedDoc(
            path=str(folder_info.relative_path / "README.md"),
            content=full_content,
            format_name="per_folder",
            description=f"README for {folder_info.relative_path}",
        )

    def _analyze_folder_contents(self, folder_path: Path) -> dict:
        """Analyze folder to extract key information."""
        files = []
        try:
            for file_path in sorted(folder_path.iterdir()):
                if file_path.suffix in self.SOURCE_EXTENSIONS and file_path.is_file():
                    try:
                        # Read first 50 lines for context
                        content = file_path.read_text(encoding="utf-8", errors="ignore")
                        lines = content.split("\n")[:50]
                        files.append({
                            "name": file_path.name,
                            "preview": "\n".join(lines),
                            "line_count": len(content.split("\n")),
                        })
                    except Exception:
                        files.append({"name": file_path.name, "preview": "", "line_count": 0})
        except PermissionError:
            pass

        return {"files": files, "file_count": len(files)}

    def _build_ai_context_prompt(
        self, folder_info: FolderInfo, profile: CodebaseProfile, contents: dict
    ) -> str:
        """Build prompt for AI-CONTEXT.md generation."""
        project_name = getattr(profile, 'name', 'Project')
        primary_lang = getattr(profile, 'primary_language', folder_info.primary_language)
        
        return f"""Generate AI assistant context documentation for a code module.

Project: {project_name}
Primary Language: {primary_lang}
Module Path: {folder_info.relative_path}
Files: {contents['file_count']}

Module Files:
{self._format_file_list(contents['files'])}

Generate structured documentation with these sections:

1. Purpose (2-3 sentences describing what this module does)
2. Key Files (list each file with brief purpose)
3. Coding Conventions (naming, patterns, error handling specific to this module)
4. Common Patterns (with actual code examples from the files)
5. Testing Approach (where tests are, how to run)
6. Integration Points (what it imports, what uses it)

Be specific and use actual examples from the code. Focus on conventions an AI assistant should follow when editing this module.
"""

    def _build_readme_prompt(
        self, folder_info: FolderInfo, profile: CodebaseProfile, contents: dict
    ) -> str:
        """Build prompt for README.md generation."""
        project_name = getattr(profile, 'name', 'Project')
        
        return f"""Generate a developer-friendly README for a code module.

Project: {project_name}
Module Path: {folder_info.relative_path}
Files: {contents['file_count']}

Module Files:
{self._format_file_list(contents['files'])}

Generate concise documentation with these sections:

1. Overview (what this module does, 2-3 paragraphs)
2. Key Components (bullet list of main components/classes)
3. Usage Examples (1-2 practical code examples)
4. Related Documentation (links to related modules)

Keep it practical and actionable for developers.
"""

    def _format_file_list(self, files: list[dict]) -> str:
        """Format file list for prompt."""
        lines = []
        for file in files[:10]:  # Limit to first 10 files
            lines.append(f"- {file['name']} ({file.get('line_count', 0)} lines)")
            if file.get("preview"):
                # Show first few lines
                preview_lines = file["preview"].split("\n")[:5]
                for line in preview_lines:
                    if line.strip():
                        lines.append(f"  {line[:100]}")  # Truncate long lines
        return "\n".join(lines)

    def _wrap_ai_context_template(self, folder_name: str, content: str, folder_contents: dict) -> str:
        """Wrap generated content in AI-CONTEXT.md template."""
        # Extract sections from LLM response or use defaults
        purpose = self._extract_section(content, "Purpose") or "## Purpose\n\nThis module provides core functionality."
        key_files = self._extract_section(content, "Key Files") or self._generate_key_files_section(folder_contents)
        conventions = self._extract_section(content, "Coding Conventions") or "## Coding Conventions\n\n- Follow project conventions"
        patterns = self._extract_section(content, "Common Patterns") or "## Common Patterns\n\nNo specific patterns documented."
        testing = self._extract_section(content, "Testing Approach") or "## Testing Approach\n\n- Tests located in tests/ directory"
        integration = self._extract_section(content, "Integration Points") or "## Integration Points\n\n- See imports for dependencies"

        return f"""# {folder_name} - AI Context

<!-- AUTO-GENERATED: Purpose - DO NOT EDIT -->
{purpose}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Key Files - DO NOT EDIT -->
{key_files}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Coding Conventions - DO NOT EDIT -->
{conventions}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Common Patterns - DO NOT EDIT -->
{patterns}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Testing Approach - DO NOT EDIT -->
{testing}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Integration Points - DO NOT EDIT -->
{integration}
<!-- END AUTO-GENERATED -->

<!-- CUSTOM SECTION: You can add notes below -->
## Additional Notes

<!-- END CUSTOM SECTION -->
"""

    def _wrap_readme_template(self, folder_name: str, content: str, folder_contents: dict) -> str:
        """Wrap generated content in README.md template."""
        overview = self._extract_section(content, "Overview") or f"## Overview\n\nThe {folder_name} module provides core functionality for the project."
        components = self._extract_section(content, "Key Components") or self._generate_components_section(folder_contents)
        examples = self._extract_section(content, "Usage Examples") or "## Usage Examples\n\nSee individual files for usage examples."
        related = self._extract_section(content, "Related Documentation") or "## Related Documentation\n\n- [Parent Module](../README.md)"

        return f"""# {folder_name}

<!-- AUTO-GENERATED: Overview - DO NOT EDIT -->
{overview}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Key Components - DO NOT EDIT -->
{components}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Usage Examples - DO NOT EDIT -->
{examples}
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Related Documentation - DO NOT EDIT -->
{related}
<!-- END AUTO-GENERATED -->

<!-- CUSTOM SECTION: You can add notes below -->
## Additional Information

<!-- END CUSTOM SECTION -->
"""

    def _generate_key_files_section(self, folder_contents: dict) -> str:
        """Generate key files section from folder contents."""
        lines = ["## Key Files\n"]
        for file in folder_contents.get("files", [])[:10]:
            lines.append(f"- `{file['name']}` - Source file")
        return "\n".join(lines) if lines else "## Key Files\n\nNo files documented."

    def _generate_components_section(self, folder_contents: dict) -> str:
        """Generate components section from folder contents."""
        lines = ["## Key Components\n"]
        for file in folder_contents.get("files", [])[:10]:
            name = file['name'].replace('.py', '').replace('.js', '').replace('.ts', '')
            lines.append(f"- **{name}** - Core component")
        return "\n".join(lines) if len(lines) > 1 else "## Key Components\n\nNo components documented."

    def _extract_section(self, content: str, section_name: str) -> Optional[str]:
        """Extract a section from generated content."""
        if not content:
            return None

        # Simple section extraction - look for ## {section_name}
        lines = content.split("\n")
        section_lines = []
        in_section = False

        for line in lines:
            # Check for section start (various heading levels)
            if line.strip().startswith(f"## {section_name}") or line.strip().startswith(f"# {section_name}"):
                in_section = True
                section_lines.append(f"## {section_name}")
            elif in_section and (line.strip().startswith("## ") or line.strip().startswith("# ")):
                # Hit next section, stop
                break
            elif in_section:
                section_lines.append(line)

        result = "\n".join(section_lines).strip() if section_lines else None
        return result if result else None
