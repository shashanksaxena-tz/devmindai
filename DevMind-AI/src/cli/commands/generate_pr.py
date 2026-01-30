"""CLI command for generating documentation and creating PRs for external GitHub repos."""

import typer
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import subprocess

from src.cli.output.formatters import OutputFormatter


def run_command(cmd: str, cwd: Path = None, capture: bool = True) -> tuple[int, str, str]:
    """Run a shell command and return exit code, stdout, stderr."""
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=capture,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def check_gh_installed() -> bool:
    """Check if GitHub CLI is installed."""
    return shutil.which("gh") is not None


def check_gh_authenticated() -> bool:
    """Check if GitHub CLI is authenticated."""
    code, _, _ = run_command("gh auth status")
    return code == 0


async def run_generate_pr(
    repo_url: str,
    formats: List[str],
    branch_name: str,
    commit_message: str,
    pr_title: str,
    pr_body: str,
    cleanup: bool,
    dry_run: bool,
):
    """Generate documentation for a GitHub repo and create a PR."""
    from src.agents.project_documenter import ProjectDocumenterAgent
    from src.agents.base import AgentContext

    console = Console()

    # Parse repo URL
    # Supports: https://github.com/owner/repo or owner/repo
    if repo_url.startswith("https://github.com/"):
        repo_path = repo_url.replace("https://github.com/", "").rstrip("/").rstrip(".git")
    elif repo_url.startswith("git@github.com:"):
        repo_path = repo_url.replace("git@github.com:", "").rstrip("/").rstrip(".git")
    else:
        repo_path = repo_url.rstrip("/")

    parts = repo_path.split("/")
    if len(parts) != 2:
        OutputFormatter.print_error(f"Invalid repo format: {repo_url}")
        console.print("[dim]Expected: owner/repo or https://github.com/owner/repo[/dim]")
        raise typer.Exit(code=1)

    owner, repo = parts
    clone_url = f"https://github.com/{owner}/{repo}.git"

    console.print(Panel(
        f"[bold]Repository:[/bold] {owner}/{repo}\n"
        f"[bold]Branch:[/bold] {branch_name}\n"
        f"[bold]Formats:[/bold] {', '.join(formats)}",
        title="Generate PR for GitHub Repository",
        border_style="cyan",
    ))

    if dry_run:
        console.print("\n[yellow]Dry run mode - no changes will be made[/yellow]")
        console.print("\nWould perform the following steps:")
        console.print(f"  1. Clone {clone_url}")
        console.print(f"  2. Create branch: {branch_name}")
        console.print(f"  3. Generate documentation for: {', '.join(formats)}")
        console.print(f"  4. Commit with message: {commit_message}")
        console.print(f"  5. Push branch and create PR: {pr_title}")
        return

    # Create temp directory for clone
    temp_dir = Path(tempfile.mkdtemp(prefix="devmind-pr-"))
    repo_dir = temp_dir / repo

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            # Step 1: Clone the repository
            task = progress.add_task("Cloning repository...", total=None)
            code, stdout, stderr = run_command(f"git clone {clone_url}", cwd=temp_dir)
            if code != 0:
                OutputFormatter.print_error(f"Failed to clone: {stderr}")
                raise typer.Exit(code=1)
            progress.update(task, description="Repository cloned")

            # Step 2: Create new branch
            progress.update(task, description=f"Creating branch {branch_name}...")
            code, _, stderr = run_command(f"git checkout -b {branch_name}", cwd=repo_dir)
            if code != 0:
                OutputFormatter.print_error(f"Failed to create branch: {stderr}")
                raise typer.Exit(code=1)

            # Step 3: Generate documentation
            progress.update(task, description="Analyzing and generating documentation...")

            agent = ProjectDocumenterAgent()
            context = AgentContext()

            result = await agent.execute(
                context,
                path=str(repo_dir),
                formats=formats,
                write_files=True,
                output_to_project=True,  # Write directly to the cloned repo
            )

            if not result.get("success"):
                OutputFormatter.print_error(result.get("error", "Unknown error"))
                raise typer.Exit(code=1)

            written_files = result.get("written_files", [])
            if not written_files:
                OutputFormatter.print_warning("No files were generated")
                raise typer.Exit(code=1)

            # Step 4: Stage and commit changes
            progress.update(task, description="Committing changes...")

            # Add all generated files
            for file_path in written_files:
                rel_path = Path(file_path).relative_to(repo_dir)
                run_command(f'git add "{rel_path}"', cwd=repo_dir)

            # Commit
            code, _, stderr = run_command(
                f'git commit -m "{commit_message}"',
                cwd=repo_dir
            )
            if code != 0:
                OutputFormatter.print_error(f"Failed to commit: {stderr}")
                raise typer.Exit(code=1)

            # Step 5: Push branch
            progress.update(task, description="Pushing branch...")
            code, _, stderr = run_command(
                f"git push -u origin {branch_name}",
                cwd=repo_dir
            )
            if code != 0:
                OutputFormatter.print_error(f"Failed to push: {stderr}")
                console.print("[dim]Make sure you have write access to the repository[/dim]")
                raise typer.Exit(code=1)

            # Step 6: Create PR using gh CLI
            progress.update(task, description="Creating pull request...")

            # Build PR body with file list
            full_pr_body = f"{pr_body}\n\n## Generated Files\n\n"
            for file_path in written_files:
                rel_path = Path(file_path).relative_to(repo_dir)
                full_pr_body += f"- `{rel_path}`\n"
            full_pr_body += "\n---\n*Generated by DevMind AI Project Documenter*"

            code, stdout, stderr = run_command(
                f'gh pr create --title "{pr_title}" --body "{full_pr_body}" --head {branch_name}',
                cwd=repo_dir
            )
            if code != 0:
                OutputFormatter.print_error(f"Failed to create PR: {stderr}")
                raise typer.Exit(code=1)

            pr_url = stdout.strip()

        # Success output
        console.print()
        console.print(Panel(
            f"[green]Pull request created successfully![/green]\n\n"
            f"[bold]PR URL:[/bold] {pr_url}\n"
            f"[bold]Branch:[/bold] {branch_name}\n"
            f"[bold]Files:[/bold] {len(written_files)} generated",
            title="Success",
            border_style="green",
        ))

        # Show generated files
        console.print("\n[bold]Generated Files:[/bold]")
        for file_path in written_files:
            rel_path = Path(file_path).relative_to(repo_dir)
            console.print(f"  - {rel_path}")

    finally:
        # Cleanup temp directory
        if cleanup:
            shutil.rmtree(temp_dir, ignore_errors=True)
        else:
            console.print(f"\n[dim]Temp directory preserved: {temp_dir}[/dim]")


def generate_pr_command(
    repo: str = typer.Argument(
        ...,
        help="GitHub repository (owner/repo or full URL)",
    ),
    formats: Optional[List[str]] = typer.Option(
        None,
        "--format", "-f",
        help="Documentation formats to generate. Default: all AI formats",
    ),
    branch: str = typer.Option(
        "devmind/add-ai-documentation",
        "--branch", "-b",
        help="Branch name for the PR",
    ),
    message: str = typer.Option(
        "Add AI coding assistant documentation",
        "--message", "-m",
        help="Commit message",
    ),
    title: str = typer.Option(
        "Add AI coding assistant documentation",
        "--title", "-t",
        help="PR title",
    ),
    body: str = typer.Option(
        "This PR adds documentation files optimized for AI coding assistants including Claude Code, GitHub Copilot, Cursor AI, Gemini, and more.",
        "--body",
        help="PR body description",
    ),
    all_formats: bool = typer.Option(
        False,
        "--all",
        help="Generate all formats including human docs",
    ),
    no_cleanup: bool = typer.Option(
        False,
        "--no-cleanup",
        help="Don't delete temp directory after PR creation",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run", "-n",
        help="Show what would be done without making changes",
    ),
):
    """
    Generate AI documentation for a GitHub repo and create a PR.

    This command will:
    1. Clone the specified GitHub repository
    2. Generate AI documentation (Claude, Copilot, Cursor, Gemini, etc.)
    3. Commit the changes to a new branch
    4. Push and create a pull request

    Prerequisites:
    - GitHub CLI (gh) installed and authenticated
    - Write access to the repository (or fork it first)

    \b
    Examples:
        # Generate docs and create PR for a public repo
        devmind generate-pr owner/repo

        # Specify formats
        devmind generate-pr owner/repo -f claude -f copilot -f gemini

        # All formats including human docs
        devmind generate-pr owner/repo --all

        # Custom branch and PR title
        devmind generate-pr owner/repo -b feature/ai-docs -t "feat: Add AI documentation"

        # Dry run to see what would happen
        devmind generate-pr owner/repo --dry-run
    """
    console = Console()

    # Check prerequisites
    if not check_gh_installed():
        console.print(Panel(
            "[red]GitHub CLI (gh) is not installed.[/red]\n\n"
            "Install it from: https://cli.github.com/\n\n"
            "macOS: brew install gh\n"
            "Linux: See https://github.com/cli/cli/blob/trunk/docs/install_linux.md\n"
            "Windows: winget install --id GitHub.cli",
            title="Missing Dependency",
            border_style="red",
        ))
        raise typer.Exit(code=1)

    if not dry_run and not check_gh_authenticated():
        console.print(Panel(
            "[red]GitHub CLI is not authenticated.[/red]\n\n"
            "Run: gh auth login",
            title="Authentication Required",
            border_style="red",
        ))
        raise typer.Exit(code=1)

    # Determine formats
    if all_formats:
        selected_formats = ["claude", "copilot", "cursor", "gemini", "windsurf", "aider", "cline", "opencode", "speckit", "human"]
    elif formats:
        selected_formats = list(formats)
    else:
        selected_formats = ["claude", "copilot", "cursor", "gemini", "windsurf", "aider", "cline", "opencode"]

    asyncio.run(
        run_generate_pr(
            repo_url=repo,
            formats=selected_formats,
            branch_name=branch,
            commit_message=message,
            pr_title=title,
            pr_body=body,
            cleanup=not no_cleanup,
            dry_run=dry_run,
        )
    )
