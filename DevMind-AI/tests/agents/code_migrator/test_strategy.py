import pytest
from unittest.mock import MagicMock, AsyncMock
from src.agents.code_migrator.strategy import MigrationPlanner, MigrationPhase, MigrationStrategy
from src.agents.code_migrator.scanner import MigrationAnalysis, MigrationTarget, MigrationType

@pytest.fixture
def mock_llm_client():
    client = MagicMock()
    client.generate = AsyncMock()
    return client

@pytest.fixture
def planner(mock_llm_client):
    return MigrationPlanner(mock_llm_client)

@pytest.fixture
def sample_analysis():
    return MigrationAnalysis(
        migration_type=MigrationType.FRAMEWORK,
        source_version="v1",
        target_version="v2",
        targets=[
            MigrationTarget(
                file_path="src/file1.py",
                line_start=1,
                line_end=10,
                pattern_type="pattern",
                current_code="code",
                complexity="simple"
            ),
             MigrationTarget(
                file_path="src/file2.py",
                line_start=1,
                line_end=10,
                pattern_type="pattern",
                current_code="code",
                complexity="simple"
            )
        ]
    )

@pytest.mark.asyncio
async def test_plan_creates_phases(planner, sample_analysis, mock_llm_client):
    mock_llm_client.generate.return_value = {"breaking_changes": []}

    strategy = await planner.plan(sample_analysis)

    assert isinstance(strategy, MigrationStrategy)
    assert len(strategy.phases) == 2
    assert strategy.phases[0].name.startswith("Phase 1")
    assert strategy.phases[1].name.startswith("Phase 2")
    assert strategy.total_phases == 2

@pytest.mark.asyncio
async def test_identify_breaking_changes(planner, sample_analysis, mock_llm_client):
    breaking_changes_data = [
        {"change": "Renamed API", "impact": "High", "mitigation": "Use new name"}
    ]
    mock_llm_client.generate.return_value = {"breaking_changes": breaking_changes_data}

    strategy = await planner.plan(sample_analysis)

    assert len(strategy.breaking_changes) == 1
    assert strategy.breaking_changes[0]["change"] == "Renamed API"

@pytest.mark.asyncio
async def test_generate_rollback_plan(planner, sample_analysis, mock_llm_client):
    mock_llm_client.generate.return_value = {"breaking_changes": []}
    strategy = await planner.plan(sample_analysis)
    assert "Revert commits" in strategy.rollback_plan

def test_get_testing_requirements(planner, sample_analysis):
    reqs = planner._get_testing_requirements(sample_analysis)
    assert len(reqs) > 0
    assert "Run full test suite" in reqs[0]
