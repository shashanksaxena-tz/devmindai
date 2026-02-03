"""CLI command for project documentation generation."""

import typer
import asyncio
from pathlib import Path
from typing import List, Optional
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from rich.tree import Tree

from src.cli.output.formatters import OutputFormatter


async def run_document(
    path: Path,
    formats: List[str],
    output_dir: Optional[Path],
    write_files: bool,
    output_to_project: bool,
    analyze_only: bool,
    format_output: str,
    per_folder: bool = True,
    incremental: bool = False,
):
    """Async implementation of document generation."""
    from src.agents.project_documenter import ProjectDocumenterAgent
    from src.agents.base import AgentContext

    console = Console()

    # Initialize agent
    agent = ProjectDocumenterAgent()

    if analyze_only:
        # Just analyze the codebase
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task("Analyzing codebase...", total=None)
            profile = await agent.analyze_only(str(path))

        if format_output == "json":
            OutputFormatter.print_json(agent._profile_to_dict(profile))
        else:
            _print_profile_summary(console, profile)
        return

    # Full documentation generation
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task("Analyzing and generating documentation...", total=None)

        context = AgentContext()

        result = await agent.execute(
            context,
            path=str(path),
            formats=formats,
            write_files=write_files,
            output_to_project=output_to_project,
            output_dir=str(output_dir) if output_dir else None,
            per_folder_docs=per_folder,
            incremental=incremental,
        )

    if not result.get("success"):
        OutputFormatter.print_error(result.get("error", "Unknown error"))
        raise typer.Exit(code=1)

    if format_output == "json":
        OutputFormatter.print_json(result)
    else:
        _print_generation_summary(console, result, write_files)


def _print_profile_summary(console: Console, profile) -> None:
    """Print codebase profile summary."""
    OutputFormatter.print_header(f"Codebase Analysis: {profile.name}")

    # Basic info table
    table = Table(show_header=False, box=None)
    table.add_column("Property", style="cyan")
    table.add_column("Value")

    table.add_row("Location", profile.root_path)
    table.add_row("Primary Language", profile.primary_language.capitalize())
    if profile.frameworks:
        table.add_row("Frameworks", ", ".join(profile.frameworks))
    if profile.api_style:
        table.add_row("API Style", profile.api_style)
    if profile.architecture_patterns:
        table.add_row("Architecture", ", ".join(profile.architecture_patterns))
    table.add_row("Files", str(len(profile.structure.files)))
    table.add_row("Directories", str(len(profile.structure.directories)))
    if profile.has_git:
        table.add_row("Git Branch", profile.default_branch)

    console.print(table)
    console.print()

    # Commands
    if profile.build_commands or profile.test_commands or profile.lint_commands:
        console.print("[bold]Commands:[/bold]")
        if profile.build_commands:
            console.print(f"  Build: [green]{profile.build_commands[0]}[/green]")
        if profile.test_commands:
            console.print(f"  Test: [green]{profile.test_commands[0]}[/green]")
        if profile.lint_commands:
            console.print(f"  Lint: [green]{profile.lint_commands[0]}[/green]")
        console.print()

    # Code style
    if profile.code_style or profile.naming_conventions:
        console.print("[bold]Code Style:[/bold]")
        if profile.code_style:
            console.print(f"  Tools: {', '.join(profile.code_style.keys())}")
        if profile.naming_conventions:
            for item, conv in profile.naming_conventions.items():
                console.print(f"  {item}: {conv}")
        console.print()


def _print_generation_summary(console: Console, result: dict, files_written: bool) -> None:
    """Print documentation generation summary."""
    profile = result.get("profile", {})
    docs = result.get("generated_docs", [])
    written = result.get("written_files", [])
    output_path = result.get("output_path")
    readme_path = result.get("readme_path")
    folder_docs_count = result.get("folder_docs_count", 0)

    OutputFormatter.print_header(f"Documentation Generated: {profile.get('name', 'Project')}")

    # Profile summary
    console.print(f"[bold]Language:[/bold] {profile.get('primary_language', 'unknown').capitalize()}")
    if profile.get("frameworks"):
        console.print(f"[bold]Frameworks:[/bold] {', '.join(profile['frameworks'])}")
    console.print()

    # Generated files table
    console.print("[bold]Generated Documentation:[/bold]")
    console.print()

    table = Table(show_header=True)
    table.add_column("Format", style="cyan")
    table.add_column("File")
    table.add_column("Description")

    for doc in docs:
        format_name = doc.get("format", "unknown")
        file_path = doc.get("path", "")
        description = doc.get("description", "")

        # Skip error entries
        if file_path.startswith("error_"):
            continue

        # Color code by format
        format_colors = {
            "claude": "green",
            "copilot": "blue",
            "cursor": "magenta",
            "gemini": "yellow",
            "windsurf": "cyan",
            "aider": "bright_green",
            "cline": "bright_blue",
            "opencode": "bright_magenta",
            "speckit": "red",
            "human": "white",
            "per_folder": "bright_cyan",
        }
        color = format_colors.get(format_name, "white")

        table.add_row(
            f"[{color}]{format_name}[/{color}]",
            file_path,
            description[:40] + "..." if len(description) > 40 else description,
        )

    console.print(table)
    console.print()

    # Summary
    formats_generated = result.get("formats_generated", [])
    console.print(f"[bold]Formats:[/bold] {', '.join(formats_generated)}")
    console.print(f"[bold]Files:[/bold] {len([d for d in docs if not d.get('path', '').startswith('error_')])}")

    if files_written and written:
        console.print(f"[bold]Written:[/bold] {len(written)} files")
        if folder_docs_count > 0:
            console.print(f"[bold]Per-Folder Docs:[/bold] {folder_docs_count} folders documented")
        console.print()

        # Show output location
        if output_path:
            console.print(Panel(
                f"[green]Output saved to:[/green]\n{output_path}",
                title="Output Location",
                border_style="green",
            ))

        # Show tree structure of output
        if output_path:
            console.print()
            _print_output_tree(console, output_path, formats_generated)

        if readme_path:
            console.print()
            console.print(f"[dim]README with usage instructions: {readme_path}[/dim]")

        console.print()
        OutputFormatter.print_success(f"Documentation generated successfully!")

    else:
        # Preview mode - show generated content
        console.print()
        console.print("[bold yellow]Preview Mode - Content Not Written to Disk[/bold yellow]")
        console.print()
        
        # Show the content of generated docs
        for doc in docs[:5]:  # Show first 5 files as preview
            if doc.get('path', '').startswith('error_'):
                continue
            
            format_name = doc.get("format", "unknown")
            file_path = doc.get("path", "")
            content = doc.get("content", "")
            
            if content:
                console.print(Panel(
                    f"[dim]{content[:500]}{'...' if len(content) > 500 else ''}[/dim]",
                    title=f"[cyan]{format_name}:[/cyan] {file_path}",
                    border_style="blue",
                ))
                console.print()
        
        if len(docs) > 5:
            console.print(f"[dim]... and {len(docs) - 5} more files[/dim]")
            console.print()
        
        console.print("[yellow]Use -w or --write to save files to disk[/yellow]")
        console.print("[dim]Use --to-project to write directly to the target project[/dim]")


def _print_output_tree(console: Console, output_path: str, formats: List[str]) -> None:
    """Print tree structure of output directory."""
    tree = Tree(f"[bold]{Path(output_path).name}/[/bold]")

    for fmt in sorted(formats):
        fmt_branch = tree.add(f"[cyan]{fmt}/[/cyan]")
        # Add typical files for each format
        if fmt == "claude":
            fmt_branch.add("CLAUDE.md")
        elif fmt == "copilot":
            fmt_branch.add("copilot-instructions.md")
        elif fmt == "cursor":
            rules = fmt_branch.add("rules/")
            rules.add("index.mdc")
            rules.add("*.mdc")
        elif fmt == "gemini":
            fmt_branch.add("GEMINI.md")
        elif fmt == "windsurf":
            fmt_branch.add("*.md")
        elif fmt == "speckit":
            memory = fmt_branch.add("memory/")
            memory.add("constitution.md")
        elif fmt == "aider":
            fmt_branch.add("CONVENTIONS.md")
            fmt_branch.add(".aider.conf.yml")
        elif fmt == "cline":
            clinerules = fmt_branch.add(".clinerules/")
            clinerules.add("project-overview.md")
            clinerules.add("development-guidelines.md")
            clinerules.add("commands-reference.md")
        elif fmt == "opencode":
            fmt_branch.add("AGENTS.md")
            fmt_branch.add(".opencode.json")
        elif fmt == "human":
            fmt_branch.add("README.generated.md")
            fmt_branch.add("ARCHITECTURE.md")
            fmt_branch.add("CONTRIBUTING.md")

    tree.add("[green]README.md[/green] (usage guide)")

    console.print(tree)


def document_command(
    path: Path = typer.Argument(
        ".",
        exists=True,
        help="Path to the project to document",
    ),
    formats: Optional[List[str]] = typer.Option(
        None,
        "--format", "-f",
        help="Documentation formats to generate (can specify multiple). "
             "Options: claude, copilot, cursor, gemini, windsurf, aider, cline, opencode, speckit, human",
    ),
    all_formats: bool = typer.Option(
        False,
        "--all",
        help="Generate all documentation formats",
    ),
    write: bool = typer.Option(
        False,
        "--write", "-w",
        help="Write generated files to devmind-output/ directory",
    ),
    to_project: bool = typer.Option(
        False,
        "--to-project", "-p",
        help="Write files directly to the target project (instead of devmind-output/)",
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Custom output directory (default: devmind-output/project-documenter/)",
    ),
    analyze: bool = typer.Option(
        False,
        "--analyze", "-a",
        help="Only analyze the codebase, don't generate docs",
    ),
    include_human: bool = typer.Option(
        False,
        "--human",
        help="Include human-readable documentation",
    ),
    include_speckit: bool = typer.Option(
        False,
        "--speckit",
        help="Include GitHub Spec Kit constitution",
    ),
    format_output: str = typer.Option(
        "text",
        "--output-format",
        help="Output format: text, json",
    ),
    per_folder: bool = typer.Option(
        True,
        "--per-folder/--no-per-folder",
        help="Generate per-folder AI-CONTEXT.md and README.md",
    ),
    incremental: bool = typer.Option(
        False,
        "--incremental", "-i",
        help="Only regenerate documentation for changed folders",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Force regeneration of all folders (ignore cache)",
    ),
):
    """
    Generate AI-agent documentation for a project.

    This command analyzes a codebase and generates documentation for various
    AI coding assistants. Output is organized in devmind-output/ by default.

    \b
    AI Agent Formats:
    - claude: CLAUDE.md for Claude Code
    - copilot: .github/copilot-instructions.md for GitHub Copilot
    - cursor: .cursor/rules/*.mdc for Cursor AI
    - gemini: GEMINI.md/.gemini/ for Gemini CLI
    - windsurf: .windsurf/rules/*.md for Windsurf/Codeium
    - aider: CONVENTIONS.md and .aider.conf.yml for Aider
    - cline: .clinerules/*.md for Cline VS Code extension
    - opencode: AGENTS.md and .opencode.json for OpenCode

    \b
    Additional Formats:
    - speckit: GitHub Spec Kit constitution files
    - human: Human-readable docs (README, ARCHITECTURE, CONTRIBUTING)

    \b
    Output Modes:
    - Default (-w): Write to devmind-output/project-documenter/{project}-{timestamp}/
    - To project (-p): Write directly to target project directory

    \b
    Examples:
        devmind document                         # Analyze only, show results
        devmind document ./myproject -w          # Generate to devmind-output/
        devmind document ./myproject -w -p       # Generate directly to project
        devmind document . --all -w              # All formats to devmind-output/
        devmind document . -f claude -f aider -w # Specific formats
        devmind document . --analyze             # Only analyze, no generation
        devmind document . -w --incremental      # Only regenerate changed folders
        devmind document . -w --no-per-folder    # Skip per-folder docs
    """
    # Determine formats
    if all_formats:
        selected_formats = ["claude", "copilot", "cursor", "gemini", "windsurf", "aider", "cline", "opencode", "speckit", "human"]
    elif formats:
        selected_formats = list(formats)
    else:
        # Default: AI agent formats only
        selected_formats = ["claude", "copilot", "cursor", "gemini", "windsurf", "aider", "cline", "opencode"]

    # Handle convenience flags
    if include_human and "human" not in selected_formats:
        selected_formats.append("human")
    if include_speckit and "speckit" not in selected_formats:
        selected_formats.append("speckit")

    # Handle force flag
    use_incremental = incremental and not force

    asyncio.run(
        run_document(
            path=path,
            formats=selected_formats,
            output_dir=output_dir,
            write_files=write,
            output_to_project=to_project,
            analyze_only=analyze,
            format_output=format_output,
            per_folder=per_folder,
            incremental=use_incremental,
        )
    )
