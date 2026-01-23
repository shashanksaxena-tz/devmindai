import pytest
from unittest.mock import MagicMock, AsyncMock
from src.agents.code_migrator.transformer import CodeTransformer, TransformResult
from src.agents.code_migrator.scanner import MigrationTarget

@pytest.fixture
def mock_llm_client():
    client = MagicMock()
    client.generate = AsyncMock()
    return client

@pytest.fixture
def transformer(mock_llm_client):
    return CodeTransformer(mock_llm_client)

@pytest.fixture
def sample_target():
    return MigrationTarget(
        file_path="src/file.py",
        line_start=1,
        line_end=5,
        pattern_type="framework",
        current_code="class Old(Component): pass",
        complexity="simple"
    )

@pytest.mark.asyncio
async def test_transform_success(transformer, sample_target, mock_llm_client):
    mock_llm_client.generate.return_value = "function New() {}"

    result = await transformer.transform(
        sample_target,
        full_file_content="class Old(Component): pass",
        migration_type="framework",
        target_version="v2"
    )

    assert result.success
    assert result.transformed_code == "function New() {}"
    assert result.diff != ""

@pytest.mark.asyncio
async def test_transform_handles_markdown(transformer, sample_target, mock_llm_client):
    mock_llm_client.generate.return_value = "```python\nfunction New() {}\n```"

    result = await transformer.transform(
        sample_target,
        full_file_content="...",
        migration_type="framework",
        target_version="v2"
    )

    assert result.success
    assert result.transformed_code.strip() == "function New() {}"

@pytest.mark.asyncio
async def test_transform_failure(transformer, sample_target, mock_llm_client):
    mock_llm_client.generate.side_effect = Exception("LLM Error")

    result = await transformer.transform(
        sample_target,
        full_file_content="...",
        migration_type="framework",
        target_version="v2"
    )

    assert not result.success
    assert "LLM Error" in result.error
