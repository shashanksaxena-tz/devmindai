"""Tests for configuration module."""

import os
from unittest.mock import patch

import pytest


class TestSettings:
    """Test suite for Settings configuration."""

    def test_settings_loads_from_environment(self):
        """Settings should load values from environment variables."""
        from src.core.config import Settings

        with patch.dict(os.environ, {
            "DATABASE_URL": "postgresql+asyncpg://test:test@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "SECRET_KEY": "test-secret-key-at-least-32-chars",
            "ANTHROPIC_API_KEY": "sk-ant-test",
            "GOOGLE_API_KEY": "test-google-key",
        }):
            settings = Settings()
            assert settings.DATABASE_URL == "postgresql+asyncpg://test:test@localhost/test"
            assert settings.REDIS_URL == "redis://localhost:6379/0"
            assert settings.SECRET_KEY == "test-secret-key-at-least-32-chars"

    def test_settings_has_required_fields(self):
        """Settings should have all required configuration fields."""
        from src.core.config import Settings

        with patch.dict(os.environ, {
            "DATABASE_URL": "postgresql+asyncpg://test:test@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "SECRET_KEY": "test-secret-key-at-least-32-chars",
            "ANTHROPIC_API_KEY": "sk-ant-test",
            "GOOGLE_API_KEY": "test-google-key",
        }):
            settings = Settings()

            # Check all required fields exist
            assert hasattr(settings, "APP_NAME")
            assert hasattr(settings, "APP_ENV")
            assert hasattr(settings, "DEBUG")
            assert hasattr(settings, "API_V1_PREFIX")
            assert hasattr(settings, "DATABASE_URL")
            assert hasattr(settings, "REDIS_URL")
            assert hasattr(settings, "QDRANT_URL")
            assert hasattr(settings, "ANTHROPIC_API_KEY")
            assert hasattr(settings, "GOOGLE_API_KEY")

    def test_settings_default_values(self):
        """Settings should have sensible defaults."""
        from src.core.config import Settings

        with patch.dict(os.environ, {
            "DATABASE_URL": "postgresql+asyncpg://test:test@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "SECRET_KEY": "test-secret-key-at-least-32-chars",
            "ANTHROPIC_API_KEY": "sk-ant-test",
            "GOOGLE_API_KEY": "test-google-key",
        }):
            settings = Settings()

            assert settings.APP_NAME == "DevMind AI"
            assert settings.API_V1_PREFIX == "/api/v1"
            assert settings.QDRANT_URL == "http://localhost:6333"
