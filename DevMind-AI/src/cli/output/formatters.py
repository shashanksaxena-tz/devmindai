import json
from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown

console = Console()

class OutputFormatter:
    @staticmethod
    def print_json(data: Any):
        """Print data as JSON."""
        console.print_json(data=data)

    @staticmethod
    def print_header(title: str, subtitle: str = None):
        """Print a styled header."""
        console.print(Panel(subtitle or "", title=f"[bold blue]{title}[/bold blue]", expand=False))

    @staticmethod
    def print_error(message: str):
        """Print an error message."""
        console.print(f"[bold red]Error:[/bold red] {message}")

    @staticmethod
    def print_success(message: str):
        """Print a success message."""
        console.print(f"[bold green]Success:[/bold green] {message}")

    @staticmethod
    def print_warning(message: str):
        """Print a warning message."""
        console.print(f"[bold yellow]Warning:[/bold yellow] {message}")

    @staticmethod
    def print_table(title: str, columns: List[str], rows: List[List[str]]):
        """Print a table."""
        table = Table(title=title)
        for col in columns:
            table.add_column(col)
        for row in rows:
            table.add_row(*row)
        console.print(table)

    @staticmethod
    def print_markdown(content: str):
        """Print markdown content."""
        console.print(Markdown(content))

    @staticmethod
    def print_code_diff(diff: str, language: str = "diff"):
        """Print a code diff."""
        syntax = Syntax(diff, language, theme="monokai", line_numbers=True)
        console.print(syntax)
