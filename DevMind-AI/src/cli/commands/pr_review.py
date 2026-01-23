import typer
import asyncio
import os
from typing import List, Optional
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.cli.output.formatters import OutputFormatter
from src.cli.utils.config_loader import get_cli_settings
from src.core.llm import get_llm_router, TaskComplexity

async def run_pr_review(
    repo: str,
    pr_number: int,
    post_comments: bool = False,
    reviewers: Optional[List[str]] = None
):
    """Async implementation of PR review."""
    from src.agents.code_reviewer.orchestrator import ReviewOrchestrator
    from src.integrations.github import get_github_client

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        OutputFormatter.print_warning("GITHUB_TOKEN not found. API rate limits may apply or private repos will fail.")

    gh_client = get_github_client()

    # Parse repo
    try:
        owner, repo_name = repo.split("/")
    except ValueError:
        OutputFormatter.print_error("Repo must be in format owner/name")
        raise typer.Exit(code=2)

    OutputFormatter.print_header(f"Fetching PR #{pr_number} from {repo}...")

    try:
        pr_info = gh_client.get_pull(owner, repo_name, pr_number)
        head_sha = pr_info["head"]["sha"]

        pr_files = gh_client.get_pr_files(owner, repo_name, pr_number)
    except Exception as e:
        OutputFormatter.print_error(f"Failed to fetch PR: {e}")
        raise typer.Exit(code=1)

    files_to_review = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("Fetching file contents...", total=len(pr_files))

        for f in pr_files:
            if f["status"] == "removed":
                progress.advance(task)
                continue

            filename = f["filename"]
            # Skip non-code files
            if not filename.endswith((".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs")):
                progress.advance(task)
                continue

            try:
                content_bytes = gh_client.get_file_content(owner, repo_name, filename, ref=head_sha)
                if isinstance(content_bytes, bytes):
                    content = content_bytes.decode("utf-8")
                else:
                    content = str(content_bytes)

                files_to_review.append({
                    "path": filename,
                    "diff": f["patch"] or "", # patch might be None for binary files or too large diffs
                    "content": content
                })
            except Exception as e:
                OutputFormatter.print_warning(f"Could not fetch content for {filename}: {e}")

            progress.advance(task)

    if not files_to_review:
        OutputFormatter.print_warning("No reviewable files found in PR.")
        return

    # Initialize orchestrator
    router = get_llm_router()
    claude = router.get_client(TaskComplexity.COMPLEX)
    gemini = router.get_client(TaskComplexity.SIMPLE)

    orchestrator = ReviewOrchestrator(
        claude_client=claude,
        gemini_client=gemini,
        enabled_reviewers=reviewers
    )

    OutputFormatter.print_header(f"Reviewing {len(files_to_review)} files...")

    # Run review
    results = await orchestrator.review_pr(files_to_review, context={"pr": pr_info})

    # Output results
    total_issues = 0
    for path, res_list in results.items():
        file_issues = []
        for res in res_list:
            file_issues.extend(res.comments)

        if file_issues:
            total_issues += len(file_issues)
            OutputFormatter.print_header(f"File: {path}")
            for issue in file_issues:
                color = "red" if issue.severity == "blocker" else "yellow" if issue.severity == "warning" else "blue"
                from rich.panel import Panel
                from rich.console import Console
                Console().print(Panel(
                    f"{issue.message}\n\n[italic]Fix: {issue.fix}[/italic]",
                    title=f"[{color}]{issue.severity.upper()}: {issue.type} (Line {issue.line})[/{color}]",
                ))

    if total_issues == 0:
        OutputFormatter.print_success("No issues found in PR!")

    if post_comments:
        OutputFormatter.print_warning("Posting comments to GitHub is not yet implemented in CLI.")

def pr_review_command(
    repo: str = typer.Argument(..., help="Repository in owner/name format"),
    pr_number: int = typer.Argument(..., help="Pull request number"),
    post_comments: bool = typer.Option(False, "--post-comments", help="Post review comments to GitHub"),
    reviewers: Optional[List[str]] = typer.Option(None, help="Specific reviewers to run")
):
    """
    Review a GitHub PR.
    """
    asyncio.run(run_pr_review(repo, pr_number, post_comments, reviewers))
