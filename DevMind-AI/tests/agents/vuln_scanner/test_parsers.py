"""Tests for dependency parsers."""

import pytest


class TestNpmParser:
    """Test suite for NPM dependency parser."""

    def test_parse_package_lock_json(self):
        """Should parse package-lock.json and extract dependencies."""
        from src.agents.vuln_scanner.parsers.npm import NpmParser

        package_lock = {
            "name": "test-project",
            "version": "1.0.0",
            "lockfileVersion": 3,
            "packages": {
                "": {
                    "name": "test-project",
                    "version": "1.0.0",
                    "dependencies": {
                        "lodash": "^4.17.20",
                        "axios": "^0.21.1"
                    }
                },
                "node_modules/lodash": {
                    "version": "4.17.20",
                    "resolved": "https://registry.npmjs.org/lodash/-/lodash-4.17.20.tgz"
                },
                "node_modules/axios": {
                    "version": "0.21.1",
                    "resolved": "https://registry.npmjs.org/axios/-/axios-0.21.1.tgz"
                }
            }
        }

        parser = NpmParser()
        deps = parser.parse(package_lock)

        assert len(deps) == 2
        assert any(d.name == "lodash" and d.version == "4.17.20" for d in deps)
        assert any(d.name == "axios" and d.version == "0.21.1" for d in deps)

    def test_parse_package_json(self):
        """Should parse package.json dependencies."""
        from src.agents.vuln_scanner.parsers.npm import NpmParser

        package_json = {
            "name": "test-project",
            "version": "1.0.0",
            "dependencies": {
                "express": "^4.18.0",
                "lodash": "^4.17.21"
            },
            "devDependencies": {
                "jest": "^29.0.0"
            }
        }

        parser = NpmParser()
        deps = parser.parse_package_json(package_json, include_dev=True)

        assert len(deps) == 3
        assert any(d.name == "express" for d in deps)
        assert any(d.name == "jest" and d.is_dev for d in deps)


class TestPipParser:
    """Test suite for Python pip dependency parser."""

    def test_parse_requirements_txt(self):
        """Should parse requirements.txt file."""
        from src.agents.vuln_scanner.parsers.pip import PipParser

        requirements = """
# Production dependencies
requests==2.28.0
flask>=2.0.0,<3.0.0
sqlalchemy[asyncio]==2.0.25

# Dev dependencies
-e .
pytest>=7.0.0
        """

        parser = PipParser()
        deps = parser.parse_requirements(requirements)

        assert len(deps) >= 3
        assert any(d.name == "requests" and d.version == "2.28.0" for d in deps)
        assert any(d.name == "flask" for d in deps)
        assert any(d.name == "sqlalchemy" for d in deps)

    def test_parse_poetry_lock(self):
        """Should parse poetry.lock file."""
        from src.agents.vuln_scanner.parsers.pip import PipParser

        poetry_lock = """
[[package]]
name = "requests"
version = "2.28.0"
description = "Python HTTP library"

[[package]]
name = "flask"
version = "2.3.0"
description = "Web framework"

[metadata]
lock-version = "2.0"
python-versions = "^3.11"
        """

        parser = PipParser()
        deps = parser.parse_poetry_lock(poetry_lock)

        assert len(deps) == 2
        assert any(d.name == "requests" and d.version == "2.28.0" for d in deps)


class TestDependencyModel:
    """Test suite for Dependency data model."""

    def test_dependency_model_creation(self):
        """Should create dependency with all fields."""
        from src.agents.vuln_scanner.parsers.base import Dependency

        dep = Dependency(
            name="lodash",
            version="4.17.20",
            ecosystem="npm",
            is_dev=False,
            is_transitive=False,
        )

        assert dep.name == "lodash"
        assert dep.version == "4.17.20"
        assert dep.ecosystem == "npm"

    def test_dependency_to_purl(self):
        """Should generate Package URL (purl) format."""
        from src.agents.vuln_scanner.parsers.base import Dependency

        dep = Dependency(
            name="lodash",
            version="4.17.20",
            ecosystem="npm",
        )

        assert dep.to_purl() == "pkg:npm/lodash@4.17.20"
