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

    # Note: DATABASE_URL, SECRET_KEY, and API keys are all optional in config now.
    # - DATABASE_URL and SECRET_KEY are only needed for API server mode
    # - The LLM router handles fallback logic when some providers aren't configured
    # - Don't set dummy values - let the router use available providers

def get_cli_settings():
    """Load settings for CLI."""
    # 1. Load from .devmind.yaml
    config = load_config_file()

    # 2. Setup Env Vars
    setup_environment(config)

    # 3. Import and return core settings
    # We import here to ensure env vars are set before Settings is instantiated
    from src.core.config import get_settings

    # Clear any cached settings to pick up new env vars
    get_settings.cache_clear()

    return get_settings()
