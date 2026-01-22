from src.agents.pipeline_generator.templates import TemplateLibrary, PipelinePlatform, PipelineTemplate
from src.agents.pipeline_generator.analyzer import ProjectAnalysis, ProjectType, Framework

def test_github_actions_python_template():
    library = TemplateLibrary()
    analysis = ProjectAnalysis(
        project_type=ProjectType.PYTHON,
        framework=Framework.FASTAPI,
        language_version="3.11",
        has_tests=True,
        test_framework="pytest",
        has_docker=True,
        has_linting=True,
        dependencies_file="requirements.txt",
        build_command="",
        test_command="pytest",
        services=["postgres", "redis"]
    )

    template = library.get_template(PipelinePlatform.GITHUB_ACTIONS, analysis)

    assert template.platform == PipelinePlatform.GITHUB_ACTIONS
    assert template.filename == ".github/workflows/ci.yml"
    assert "PYTHON_VERSION: '3.11'" in template.content
    assert "postgres:" in template.content
    assert "redis:" in template.content
    assert "pip install -r requirements.txt" in template.content
    assert "pytest --cov" in template.content

def test_github_actions_nodejs_template():
    library = TemplateLibrary()
    analysis = ProjectAnalysis(
        project_type=ProjectType.NODEJS,
        framework=Framework.REACT,
        language_version="20",
        has_tests=True,
        test_framework="jest",
        has_docker=False,
        has_linting=True,
        dependencies_file="package.json",
        build_command="npm run build",
        test_command="npm test",
        services=[]
    )

    template = library.get_template(PipelinePlatform.GITHUB_ACTIONS, analysis)

    assert template.platform == PipelinePlatform.GITHUB_ACTIONS
    assert "NODE_VERSION: '20'" in template.content
    assert "npm ci" in template.content
    assert "npm run build" in template.content

def test_gitlab_ci_template():
    library = TemplateLibrary()
    analysis = ProjectAnalysis(
        project_type=ProjectType.PYTHON,
        framework=Framework.FLASK,
        language_version="3.9",
        has_tests=True,
        test_framework="pytest",
        has_docker=False,
        has_linting=False,
        dependencies_file="requirements.txt",
        build_command="",
        test_command="pytest",
        services=[]
    )

    template = library.get_template(PipelinePlatform.GITLAB_CI, analysis)

    assert template.platform == PipelinePlatform.GITLAB_CI
    assert template.filename == ".gitlab-ci.yml"
    assert "image: python:3.9" in template.content
    assert "pytest" in template.content
