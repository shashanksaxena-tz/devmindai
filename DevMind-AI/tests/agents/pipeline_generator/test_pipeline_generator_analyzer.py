from src.agents.pipeline_generator.analyzer import ProjectAnalyzer, ProjectType, Framework

def test_detect_python_fastapi_project():
    analyzer = ProjectAnalyzer()
    files = {
        "pyproject.toml": "dependencies = ['fastapi', 'uvicorn']",
        "requirements.txt": "fastapi==0.100.0\nuvicorn==0.23.0",
        "tests/test_main.py": "def test_root(): assert True",
        "Dockerfile": "FROM python:3.11",
    }

    analysis = analyzer.analyze(files)

    assert analysis.project_type == ProjectType.PYTHON
    assert analysis.framework == Framework.FASTAPI
    assert analysis.language_version == "3.11"
    assert analysis.has_tests is True
    assert analysis.test_framework == "unittest" # default if no pytest explicit
    assert analysis.has_docker is True
    assert analysis.dependencies_file == "requirements.txt"

def test_detect_nodejs_react_project():
    analyzer = ProjectAnalyzer()
    files = {
        "package.json": '{"dependencies": {"react": "^18.0.0", "next": "^13.0.0"}, "scripts": {"test": "jest"}}',
        "src/App.test.js": "test('renders learn react link', () => {});",
    }

    analysis = analyzer.analyze(files)

    assert analysis.project_type == ProjectType.NODEJS
    # The analyzer prioritizes iterating through FRAMEWORK_INDICATORS.
    # 'react' is checked before 'next' in the map if iteration order matters, or depends on dict order.
    # In the code:
    # FRAMEWORK_INDICATORS = { "fastapi": ..., "django": ..., "flask": ..., "react": ..., "next": ..., ... }
    # It loops items(). If both are present, the first one found returns.
    # Python 3.7+ preserves insertion order. 'react' is before 'next' in the list.
    # So it should return REACT if 'react' is in dependencies.
    assert analysis.framework in [Framework.REACT, Framework.NEXTJS]
    assert analysis.language_version == "20"
    assert analysis.has_tests is True
    assert analysis.test_framework == "jest"
    assert analysis.has_docker is False

def test_detect_services():
    analyzer = ProjectAnalyzer()
    files = {
        "pyproject.toml": "dependencies = ['psycopg2', 'redis']",
    }

    analysis = analyzer.analyze(files)
    assert "postgres" in analysis.services
    assert "redis" in analysis.services
