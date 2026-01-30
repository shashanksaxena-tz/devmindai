import typer
from typing import Optional
from pathlib import Path
import os
import yaml

from src.cli.utils.config_loader import get_cli_settings, load_config_file
from src.cli.output.formatters import OutputFormatter

# Initialize settings immediately to handle env vars
settings = get_cli_settings()

app = typer.Typer(
    name="devmind",
    help="DevMind AI CLI - AI-powered developer tools",
    add_completion=True,
)

# Config commands
config_app = typer.Typer(name="config", help="Manage configuration")
app.add_typer(config_app)

@config_app.command("init")
def config_init(path: str = ".devmind.yaml"):
    """Initialize a new configuration file."""
    if Path(path).exists():
        OutputFormatter.print_warning(f"Configuration file {path} already exists.")
        return

    default_config = {
        "llm": {
            "anthropic_api_key": "${ANTHROPIC_API_KEY}",
            "google_api_key": "${GOOGLE_API_KEY}"
        },
        "review": {
            "fail_on": "blocker"
        },
        "scan": {
            "fail_on": "high"
        }
    }

    with open(path, "w") as f:
        yaml.dump(default_config, f, default_flow_style=False)

    OutputFormatter.print_success(f"Created {path}")

@config_app.command("show")
def config_show():
    """Show current configuration."""
    config = load_config_file()
    OutputFormatter.print_json(config)

# Register commands
from src.cli.commands.review import review_command
app.command(name="review")(review_command)

from src.cli.commands.scan import scan_command
app.command(name="scan")(scan_command)

from src.cli.commands.test import test_command
app.command(name="test")(test_command)

from src.cli.commands.pr_review import pr_review_command
app.command(name="pr-review")(pr_review_command)

from src.cli.commands.document import document_command
app.command(name="document")(document_command)

@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version"),
):
    """
    DevMind AI CLI
    """
    if version:
        typer.echo("DevMind AI CLI v0.1.0")
        raise typer.Exit()

if __name__ == "__main__":
    app()
