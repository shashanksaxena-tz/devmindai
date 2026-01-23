import os
from pathlib import Path
import yaml
from typing import Any, Dict, Optional
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("devmind.cli")

def load_config_file(path: str = ".devmind.yaml") -> Dict[str, Any]:
    """Load configuration from a YAML file."""
    config_path = Path(path)
    if not config_path.exists():
        return {}

    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        logger.warning(f"Failed to load config file {path}: {e}")
        return {}

def setup_environment(config: Dict[str, Any]):
    """Set environment variables based on config and defaults."""

    # Map config keys to env vars
    # llm.anthropic_api_key -> ANTHROPIC_API_KEY
    if "llm" in config:
        if "anthropic_api_key" in config["llm"]:
            os.environ["ANTHROPIC_API_KEY"] = config["llm"]["anthropic_api_key"]
        if "google_api_key" in config["llm"]:
            os.environ["GOOGLE_API_KEY"] = config["llm"]["google_api_key"]
        if "openai_api_key" in config["llm"]:
            os.environ["OPENAI_API_KEY"] = config["llm"]["openai_api_key"]

    if "github" in config:
        if "token" in config["github"]:
            os.environ["GITHUB_TOKEN"] = config["github"]["token"]

    # Ensure required settings for src.core.config.Settings
    # We provide dummy values if they are missing, as CLI mostly runs in standalone mode
    # without DB access for scanning/analysis tasks.

    if "DATABASE_URL" not in os.environ:
        # Dummy URL to satisfy validation.
        # Note: If an agent actually tries to use the DB, it will fail.
        os.environ["DATABASE_URL"] = "postgresql+asyncpg://dummy:dummy@localhost:5432/dummy"

    if "SECRET_KEY" not in os.environ:
        os.environ["SECRET_KEY"] = "dummy_secret_for_cli_standalone_mode"

    if "ANTHROPIC_API_KEY" not in os.environ:
        os.environ["ANTHROPIC_API_KEY"] = "dummy" # Placeholder, agents will fail if they need it but validation passes

    if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = "dummy"

def get_cli_settings():
    """Load settings for CLI."""
    # 1. Load from .devmind.yaml
    config = load_config_file()

    # 2. Setup Env Vars (including mocks for DB)
    setup_environment(config)

    # 3. Import and return core settings
    # We import here to ensure env vars are set before Settings is instantiated
    from src.core.config import get_settings
    return get_settings()
