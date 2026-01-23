import typer
import asyncio
from pathlib import Path
from typing import Optional

from src.cli.output.formatters import OutputFormatter
from src.cli.utils.config_loader import get_cli_settings
from src.core.llm import get_llm_router

async def run_scan(
    path: Path,
    full: bool = False,
    severity: str = "medium",
    format_output: str = "text",
    ignore: Optional[str] = None,
    fail_on: Optional[str] = None
):
    """Async implementation of scan."""
    from src.agents.vuln_scanner.agent import VulnScannerAgent

    # Initialize agent
    # We pass None as router because VulnScanner uses OSVClient mainly,
    # but ExploitabilityAnalyzer might use LLM.
    router = get_llm_router()
    agent = VulnScannerAgent(router=router)

    OutputFormatter.print_header(f"Scanning {path}...")

    try:
        results = await agent.scan_repository(str(path), full_scan=full)
        await agent.close()
    except Exception as e:
        OutputFormatter.print_error(f"Scan failed: {e}")
        await agent.close()
        raise typer.Exit(code=2)

    # Process results
    severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    min_severity_score = severity_order.get(severity, 2)
    fail_score = severity_order.get(fail_on, 100) if fail_on else 100

    exit_code = 0
    filtered_details = []

    # Ignore list
    ignore_list = ignore.split(",") if ignore else []

    for issue in results.get("details", []):
        if issue["vulnerability_id"] in ignore_list:
            continue

        s_score = severity_order.get(issue["severity"].lower(), 0)
        if s_score >= min_severity_score:
            filtered_details.append(issue)
            if s_score >= fail_score:
                exit_code = 1

    if format_output == "json":
        output = {
            "summary": results["vulnerabilities"],
            "total_dependencies": results["total_dependencies"],
            "details": filtered_details
        }
        OutputFormatter.print_json(output)
    else:
        # Text output
        stats = results["vulnerabilities"]
        OutputFormatter.print_table(
            "Vulnerability Summary",
            ["Severity", "Count"],
            [
                ["[bold red]Critical[/bold red]", str(stats["critical"])],
                ["[red]High[/red]", str(stats["high"])],
                ["[yellow]Medium[/yellow]", str(stats["medium"])],
                ["[blue]Low[/blue]", str(stats["low"])],
            ]
        )

        if not filtered_details:
            OutputFormatter.print_success("No vulnerabilities found matching criteria.")
        else:
            print()
            for issue in filtered_details:
                sev = issue["severity"].upper()
                color = "red" if sev in ["CRITICAL", "HIGH"] else "yellow" if sev == "MEDIUM" else "blue"

                title = f"[{color}]{sev}: {issue['package']} {issue['version']} ({issue['vulnerability_id']})[/{color}]"
                content = (
                    f"{issue['title']}\n"
                    f"Fixed in: {issue['fix_version'] or 'None'}\n"
                    f"Exploitable: {issue.get('is_exploitable', 'Unknown')}\n\n"
                    f"[italic]Remediation: {issue.get('remediation', 'N/A')}[/italic]"
                )

                from rich.panel import Panel
                from rich.console import Console
                Console().print(Panel(content, title=title, expand=False))

    if exit_code != 0:
        raise typer.Exit(code=exit_code)

def scan_command(
    path: Path = typer.Argument(Path("."), help="Project root to scan"),
    full: bool = typer.Option(False, "--full", help="Include exploitability analysis"),
    severity: str = typer.Option("medium", help="Minimum severity: critical, high, medium, low"),
    format: str = typer.Option("text", "--format", help="Output format: text, json"),
    ignore: str = typer.Option(None, help="Comma-separated CVE IDs to ignore"),
    fail_on: str = typer.Option(None, help="Exit 1 for this severity or above")
):
    """
    Scan for dependency vulnerabilities.
    """
    asyncio.run(run_scan(path, full, severity, format, ignore, fail_on))
