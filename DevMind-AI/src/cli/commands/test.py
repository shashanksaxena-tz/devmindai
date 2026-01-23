import typer
import asyncio
from pathlib import Path
from typing import Optional

from src.cli.output.formatters import OutputFormatter
from src.cli.utils.config_loader import get_cli_settings
from src.core.llm import get_llm_router

async def run_test(
    file: Path,
    output: Path = Path("tests"),
    framework: str = "pytest",
    coverage: Optional[Path] = None,
    dry_run: bool = False
):
    """Async implementation of test generation."""
    from src.agents.test_generator.agent import TestGeneratorAgent
    from src.agents.base import AgentContext

    if not file.exists():
        OutputFormatter.print_error(f"File not found: {file}")
        raise typer.Exit(code=2)

    code = file.read_text(encoding="utf-8")

    # Initialize agent
    router = get_llm_router()
    agent = TestGeneratorAgent(router=router)

    OutputFormatter.print_header(f"Generating tests for {file}...")

    # Coverage data loading (simplified)
    coverage_data = None
    if coverage and coverage.exists():
        # TODO: Load coverage data properly. For now we just pass the path string
        # or implement a loader if TestGenerator expects dict.
        # TestGenerator expects dict mapping file path to covered lines.
        # We'll skip complex loading for this CLI phase unless required.
        pass

    try:
        context = AgentContext() # dummy context
        result = await agent.execute(
            context=context,
            code=code,
            file_path=str(file),
            framework=framework,
            coverage_data=coverage_data
        )
    except Exception as e:
        OutputFormatter.print_error(f"Test generation failed: {e}")
        raise typer.Exit(code=1)

    # Process results
    test_content = result.get("test_file_content")
    suggested_path = result.get("test_file_path", f"test_{file.name}")

    # Adjust output path
    # If output is a directory, append suggested filename
    # If output ends in .py, use it as is
    if str(output).endswith(".py"):
        target_path = output
    else:
        target_path = output / suggested_path

    if dry_run:
        OutputFormatter.print_header(f"Preview: {target_path}")
        OutputFormatter.print_code_diff(test_content, language="python")
    else:
        # Write file
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(test_content, encoding="utf-8")
        OutputFormatter.print_success(f"Generated tests written to {target_path}")

    # Stats
    OutputFormatter.print_table(
        "Generation Stats",
        ["Metric", "Value"],
        [
            ["Functions Analyzed", str(result.get("functions_analyzed", 0))],
            ["Classes Analyzed", str(result.get("classes_analyzed", 0))],
            ["Tests Generated", str(result.get("tests_generated", 0))],
        ]
    )

def test_command(
    file: Path = typer.Argument(..., help="Source file to generate tests for"),
    output: Path = typer.Option(Path("tests"), "--output", "-o", help="Output directory or file"),
    framework: str = typer.Option("pytest", help="Test framework: pytest, unittest, jest"),
    coverage: Path = typer.Option(None, help="Existing coverage file to find gaps"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print tests without writing files")
):
    """
    Generate tests for source file.
    """
    asyncio.run(run_test(file, output, framework, coverage, dry_run))
