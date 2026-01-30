"""CLI command for project documentation generation."""

import typer
import asyncio
from pathlib import Path
from typing import List, Optional
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from rich.console import Console

from src.cli.output.formatters import OutputFormatter


async def run_document(
    path: Path,
    formats: List[str],
    output_dir: Optional[Path],
    write_files: bool,
    analyze_only: bool,
    format_output: str,
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
        task = progress.add_task("Analyzing and generating documentation...", total=None)

        context = AgentContext()

        # Determine output location
        target_path = output_dir if output_dir else path

        result = await agent.execute(
            context,
            path=str(path),
            formats=formats,
            write_files=write_files,
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
    table.add_column("File Path")
    table.add_column("Description")

    for doc in docs:
        format_name = doc.get("format", "unknown")
        file_path = doc.get("path", "")
        description = doc.get("description", "")

        # Color code by format
        format_colors = {
            "claude": "green",
            "copilot": "blue",
            "cursor": "magenta",
            "gemini": "yellow",
            "windsurf": "cyan",
            "speckit": "red",
            "human": "white",
        }
        color = format_colors.get(format_name, "white")

        table.add_row(
            f"[{color}]{format_name}[/{color}]",
            file_path,
            description[:50] + "..." if len(description) > 50 else description,
        )

    console.print(table)
    console.print()

    # Summary
    formats_generated = result.get("formats_generated", [])
    console.print(f"[bold]Formats generated:[/bold] {', '.join(formats_generated)}")
    console.print(f"[bold]Total files:[/bold] {len(docs)}")

    if files_written:
        console.print(f"[bold]Files written:[/bold] {len(written)}")
        if written:
            console.print()
            OutputFormatter.print_success(f"Files written to disk ({len(written)} files)")
    else:
        console.print()
        console.print("[dim]Use --write to write files to disk[/dim]")


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
             "Options: claude, copilot, cursor, gemini, windsurf, speckit, human",
    ),
    all_formats: bool = typer.Option(
        False,
        "--all",
        help="Generate all documentation formats",
    ),
    write: bool = typer.Option(
        False,
        "--write", "-w",
        help="Write generated files to disk",
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Output directory (defaults to project path)",
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
):
    """
    Generate AI-agent documentation for a project.

    This command analyzes a codebase and generates documentation for various
    AI coding assistants:

    \b
    AI Agent Formats:
    - claude: CLAUDE.md for Claude Code
    - copilot: .github/copilot-instructions.md for GitHub Copilot
    - cursor: .cursor/rules/*.mdc for Cursor AI
    - gemini: GEMINI.md for Google Gemini Code Assist
    - windsurf: .windsurf/rules/*.md for Windsurf/Codeium

    \b
    Additional Formats:
    - speckit: GitHub Spec Kit constitution files
    - human: Human-readable docs (README, ARCHITECTURE, CONTRIBUTING)

    \b
    Examples:
        devmind document                     # Analyze current dir, show AI docs
        devmind document ./myproject -w      # Generate and write AI docs
        devmind document . --all -w          # Generate all formats and write
        devmind document . -f claude -f copilot -w  # Specific formats
        devmind document . --analyze         # Only analyze, no generation
    """
    # Determine formats
    if all_formats:
        selected_formats = ["claude", "copilot", "cursor", "gemini", "windsurf", "speckit", "human"]
    elif formats:
        selected_formats = list(formats)
    else:
        # Default: AI agent formats only
        selected_formats = ["claude", "copilot", "cursor", "gemini", "windsurf"]

    # Handle convenience flags
    if include_human and "human" not in selected_formats:
        selected_formats.append("human")
    if include_speckit and "speckit" not in selected_formats:
        selected_formats.append("speckit")

    asyncio.run(
        run_document(
            path=path,
            formats=selected_formats,
            output_dir=output_dir,
            write_files=write,
            analyze_only=analyze,
            format_output=format_output,
        )
    )
