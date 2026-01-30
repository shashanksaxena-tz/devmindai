"""CLI command for running DevMind agents through different AI coding assistants."""

import typer
import subprocess
import shutil
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.cli.output.formatters import OutputFormatter


# Available AI tools and their commands
AI_TOOLS = {
    "gemini": {
        "name": "Gemini CLI",
        "command": "gemini",
        "install": "npm install -g @anthropic-ai/gemini-cli",
        "docs": "https://github.com/google-gemini/gemini-cli",
    },
    "claude": {
        "name": "Claude Code",
        "command": "claude",
        "install": "npm install -g @anthropic-ai/claude-code",
        "docs": "https://github.com/anthropics/claude-code",
    },
    "aider": {
        "name": "Aider",
        "command": "aider",
        "install": "pip install aider-chat",
        "docs": "https://aider.chat",
    },
    "opencode": {
        "name": "OpenCode",
        "command": "opencode",
        "install": "npm install -g opencode-ai",
        "docs": "https://opencode.ai",
    },
    "copilot": {
        "name": "GitHub Copilot CLI",
        "command": "gh copilot",
        "install": "gh extension install github/gh-copilot",
        "docs": "https://docs.github.com/en/copilot/github-copilot-in-the-cli",
    },
}

# DevMind agent commands
DEVMIND_AGENTS = {
    "review": {
        "name": "Code Reviewer",
        "command": "devmind review",
        "description": "AI-powered code review",
        "args": "<file>",
    },
    "scan": {
        "name": "Security Scanner",
        "command": "devmind scan",
        "description": "Security vulnerability scanner",
        "args": "<path>",
    },
    "test": {
        "name": "Test Generator",
        "command": "devmind test",
        "description": "Generate unit tests",
        "args": "<file>",
    },
    "document": {
        "name": "Project Documenter",
        "command": "devmind document",
        "description": "Generate AI-ready documentation",
        "args": "<path> -w",
    },
    "pr-review": {
        "name": "PR Reviewer",
        "command": "devmind pr-review",
        "description": "Review pull requests",
        "args": "<pr-url>",
    },
}


def check_tool_installed(tool: str) -> bool:
    """Check if an AI tool is installed."""
    tool_info = AI_TOOLS.get(tool)
    if not tool_info:
        return False

    cmd = tool_info["command"].split()[0]
    return shutil.which(cmd) is not None


def run_with_command(
    tool: str = typer.Argument(
        ...,
        help=f"AI tool to use: {', '.join(AI_TOOLS.keys())}",
    ),
    agent: str = typer.Argument(
        ...,
        help=f"DevMind agent to run: {', '.join(DEVMIND_AGENTS.keys())}",
    ),
    target: str = typer.Argument(
        ".",
        help="Target file or path for the agent",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run", "-n",
        help="Show the command without executing",
    ),
    interactive: bool = typer.Option(
        True,
        "--interactive/--no-interactive", "-i/-I",
        help="Run in interactive mode (default: True)",
    ),
):
    """
    Run a DevMind agent through an AI coding assistant.

    This command helps you execute DevMind agents using different AI tools
    like Gemini CLI, Claude Code, Aider, OpenCode, or GitHub Copilot CLI.

    \b
    Available AI Tools:
    - gemini: Google Gemini CLI
    - claude: Anthropic Claude Code
    - aider: Aider AI pair programming
    - opencode: OpenCode AI assistant
    - copilot: GitHub Copilot CLI

    \b
    Available DevMind Agents:
    - review: AI code review
    - scan: Security scanning
    - test: Test generation
    - document: Documentation generation
    - pr-review: Pull request review

    \b
    Examples:
        devmind run-with gemini review src/main.py
        devmind run-with aider test src/utils.py
        devmind run-with claude document . --dry-run
        devmind run-with opencode scan . -I
    """
    console = Console()

    # Validate tool
    if tool not in AI_TOOLS:
        OutputFormatter.print_error(f"Unknown AI tool: {tool}")
        console.print(f"[dim]Available tools: {', '.join(AI_TOOLS.keys())}[/dim]")
        raise typer.Exit(code=1)

    # Validate agent
    if agent not in DEVMIND_AGENTS:
        OutputFormatter.print_error(f"Unknown agent: {agent}")
        console.print(f"[dim]Available agents: {', '.join(DEVMIND_AGENTS.keys())}[/dim]")
        raise typer.Exit(code=1)

    tool_info = AI_TOOLS[tool]
    agent_info = DEVMIND_AGENTS[agent]

    # Check if tool is installed
    if not check_tool_installed(tool):
        console.print(Panel(
            f"[yellow]{tool_info['name']} is not installed.[/yellow]\n\n"
            f"Install with:\n[green]{tool_info['install']}[/green]\n\n"
            f"Documentation: {tool_info['docs']}",
            title="Tool Not Found",
            border_style="yellow",
        ))
        raise typer.Exit(code=1)

    # Build the prompt for the AI tool
    devmind_cmd = f"poetry run {agent_info['command']} {target}"
    prompt = f"""Run the DevMind {agent_info['name']} agent:

Command to execute:
```bash
{devmind_cmd}
```

This will {agent_info['description'].lower()}. After running, analyze the output and provide insights."""

    # Build the full command
    if tool == "gemini":
        full_cmd = f'gemini "{prompt}"'
    elif tool == "claude":
        full_cmd = f'claude --print "{prompt}"'
    elif tool == "aider":
        # Aider works differently - it's more of a chat
        full_cmd = f'aider --message "{prompt}"'
    elif tool == "opencode":
        full_cmd = f'opencode "{prompt}"'
    elif tool == "copilot":
        full_cmd = f'gh copilot suggest "{prompt}"'
    else:
        full_cmd = f'{tool_info["command"]} "{prompt}"'

    # Show what we're going to do
    console.print()
    console.print(Panel(
        f"[bold]AI Tool:[/bold] {tool_info['name']}\n"
        f"[bold]Agent:[/bold] {agent_info['name']}\n"
        f"[bold]Target:[/bold] {target}\n\n"
        f"[bold]DevMind Command:[/bold]\n[green]{devmind_cmd}[/green]",
        title="Running DevMind Agent",
        border_style="cyan",
    ))

    if dry_run:
        console.print()
        console.print("[yellow]Dry run - command not executed[/yellow]")
        console.print()
        console.print("[bold]Full command:[/bold]")
        console.print(f"[dim]{full_cmd}[/dim]")
        return

    # Execute directly without the AI wrapper if not interactive
    if not interactive:
        console.print()
        console.print("[bold]Executing directly...[/bold]")
        try:
            result = subprocess.run(
                devmind_cmd,
                shell=True,
                cwd=Path.cwd(),
            )
            raise typer.Exit(code=result.returncode)
        except Exception as e:
            OutputFormatter.print_error(f"Execution failed: {e}")
            raise typer.Exit(code=1)

    # For interactive mode, give instructions
    console.print()
    console.print(Panel(
        f"To run this with {tool_info['name']}, execute:\n\n"
        f"[green]{full_cmd}[/green]\n\n"
        f"Or run the DevMind command directly:\n\n"
        f"[cyan]{devmind_cmd}[/cyan]",
        title="Instructions",
        border_style="green",
    ))


def list_tools_command():
    """
    List available AI coding assistants and their installation status.
    """
    console = Console()

    OutputFormatter.print_header("Available AI Coding Assistants")

    table = Table(show_header=True)
    table.add_column("Tool", style="cyan")
    table.add_column("Name")
    table.add_column("Status")
    table.add_column("Install Command")

    for tool_id, tool_info in AI_TOOLS.items():
        installed = check_tool_installed(tool_id)
        status = "[green]Installed[/green]" if installed else "[red]Not installed[/red]"

        table.add_row(
            tool_id,
            tool_info["name"],
            status,
            tool_info["install"],
        )

    console.print(table)
    console.print()

    # Show agents
    console.print("[bold]DevMind Agents:[/bold]")
    console.print()

    agent_table = Table(show_header=True)
    agent_table.add_column("Agent", style="cyan")
    agent_table.add_column("Description")
    agent_table.add_column("Example")

    for agent_id, agent_info in DEVMIND_AGENTS.items():
        agent_table.add_row(
            agent_id,
            agent_info["description"],
            f"devmind run-with gemini {agent_id} {agent_info['args']}",
        )

    console.print(agent_table)


# Create subcommand app
run_with_app = typer.Typer(name="run-with", help="Run DevMind agents through AI coding assistants")
run_with_app.command(name="execute")(run_with_command)
run_with_app.command(name="list")(list_tools_command)
