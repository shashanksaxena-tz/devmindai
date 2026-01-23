import typer
import asyncio
import os
from pathlib import Path
from typing import List, Optional
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.cli.output.formatters import OutputFormatter
from src.cli.utils.config_loader import get_cli_settings
from src.core.llm import get_llm_router, TaskComplexity

async def run_review(
    path: Path,
    reviewers: Optional[List[str]] = None,
    severity: str = "warning",
    format_output: str = "text",
    fail_on: Optional[str] = None
):
    """Async implementation of review."""
    from src.agents.code_reviewer.orchestrator import ReviewOrchestrator

    settings = get_cli_settings()
    router = get_llm_router()

    # Initialize orchestrator
    # Note: Orchestrator expects specific clients, but we can get them from router
    claude = router.get_client(TaskComplexity.COMPLEX) # For complex
    gemini = router.get_client(TaskComplexity.SIMPLE) # For simple

    orchestrator = ReviewOrchestrator(
        claude_client=claude,
        gemini_client=gemini,
        enabled_reviewers=reviewers
    )

    # Collect files
    files_to_review = []
    if path.is_file():
        files_to_review.append(path)
    elif path.is_dir():
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith((".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs")):
                    files_to_review.append(Path(root) / file)

    results = {}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(f"Reviewing {len(files_to_review)} files...", total=len(files_to_review))

        for file_path in files_to_review:
            try:
                content = file_path.read_text(encoding="utf-8")
                # For standalone review, we treat full content as the "diff" (new file)
                diff = f"new file mode 100644\n--- /dev/null\n+++ b/{file_path.name}\n@@ -0,0 +1,{len(content.splitlines())} @@\n" + \
                       "\n".join(f"+{line}" for line in content.splitlines())

                progress.update(task, description=f"Reviewing {file_path.name}...")

                file_results = await orchestrator.review_file(
                    file_path=str(file_path),
                    diff=diff,
                    full_content=content
                )

                results[str(file_path)] = file_results
                progress.advance(task)
            except Exception as e:
                OutputFormatter.print_error(f"Failed to review {file_path}: {e}")

    # Process and Output Results
    exit_code = 0
    total_issues = 0

    json_output = {"files": [], "summary": {"total": 0, "blocker": 0, "warning": 0, "suggestion": 0, "nit": 0}}

    severity_order = {"blocker": 4, "warning": 3, "suggestion": 2, "nit": 1}
    min_severity_score = severity_order.get(severity, 1)
    fail_score = severity_order.get(fail_on, 100) if fail_on else 100

    for fpath, f_results in results.items():
        file_issues = []

        for res in f_results:
            for comment in res.comments:
                s_score = severity_order.get(comment.severity, 0)
                if s_score >= min_severity_score:
                    file_issues.append(comment)
                    json_output["summary"][comment.severity] += 1
                    json_output["summary"]["total"] += 1
                    if s_score >= fail_score:
                        exit_code = 1

        if file_issues:
            total_issues += len(file_issues)

            if format_output == "json":
                json_output["files"].append({
                    "path": fpath,
                    "issues": [
                        {
                            "type": c.type,
                            "severity": c.severity,
                            "line": c.line,
                            "message": c.message,
                            "fix": c.fix,
                            "reviewer": res.reviewer_name
                        } for c in file_issues
                    ]
                })
            else:
                OutputFormatter.print_header(f"Review: {fpath}")
                for issue in file_issues:
                    color = "red" if issue.severity == "blocker" else "yellow" if issue.severity == "warning" else "blue"

                    from rich.panel import Panel
                    from rich.console import Console
                    Console().print(Panel(
                        f"{issue.message}\n\n[italic]Fix: {issue.fix}[/italic]",
                        title=f"[{color}]{issue.severity.upper()}: {issue.type} (Line {issue.line})[/{color}]",
                        subtitle=f"Reviewer: {res.reviewer_name}"
                    ))

    if format_output == "json":
        OutputFormatter.print_json(json_output)
    elif total_issues == 0:
        OutputFormatter.print_success("No issues found!")
    else:
        print()
        OutputFormatter.print_header(f"Summary: {total_issues} issues found")

    if exit_code != 0:
        raise typer.Exit(code=exit_code)

def review_command(
    path: Path = typer.Argument(..., exists=True, help="File or directory to review"),
    reviewers: Optional[List[str]] = typer.Option(None, help="Specific reviewers to run"),
    severity: str = typer.Option("warning", help="Minimum severity: blocker, warning, suggestion, nit"),
    format: str = typer.Option("text", "--format", help="Output format: text, json"),
    fail_on: str = typer.Option(None, help="Exit 1 if issues of this severity found")
):
    """
    Review code for issues.
    """
    asyncio.run(run_review(path, reviewers, severity, format, fail_on))
