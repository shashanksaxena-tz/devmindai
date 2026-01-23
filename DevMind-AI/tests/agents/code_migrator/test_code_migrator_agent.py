import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from src.agents.code_migrator.agent import CodeMigratorAgent
from src.agents.base import AgentContext
from src.agents.code_migrator.scanner import MigrationAnalysis, MigrationTarget, MigrationType
from src.agents.code_migrator.strategy import MigrationStrategy
from src.agents.code_migrator.transformer import TransformResult

@pytest.fixture
def mock_router():
    router = MagicMock()
    router.get_client.return_value = MagicMock()
    return router

@pytest.fixture
def agent(mock_router):
    return CodeMigratorAgent(mock_router)

@pytest.fixture
def context():
    return AgentContext(repository_id="repo-1")

@pytest.mark.asyncio
async def test_execute_dry_run(agent, context):
    files = {"src/file.py": "code"}

    # Mock scanner
    agent.scanner.scan = MagicMock(return_value=MigrationAnalysis(
        migration_type=MigrationType.FRAMEWORK,
        source_version="v1",
        target_version="v2",
        targets=[MigrationTarget("src/file.py", 1, 2, "fw", "code", "simple")],
        total_files=1
    ))

    # Mock planner
    strategy = MigrationStrategy([], 0, [], "rollback", [])
    agent.planner.plan = AsyncMock(return_value=strategy)

    result = await agent.execute(
        context,
        files=files,
        migration_type="framework",
        source_version="v1",
        target_version="v2",
        dry_run=True
    )

    assert result["dry_run"] is True
    assert result["analysis"]["total_files"] == 1
    agent.planner.plan.assert_called_once()

    # Transformer should not be called
    agent.transformer.transform = AsyncMock()
    agent.transformer.transform.assert_not_called()

@pytest.mark.asyncio
async def test_execute_full_run(agent, context):
    files = {"src/file.py": "code"}

    # Mock scanner
    target = MigrationTarget("src/file.py", 1, 2, "fw", "code", "simple")
    agent.scanner.scan = MagicMock(return_value=MigrationAnalysis(
        migration_type=MigrationType.FRAMEWORK,
        source_version="v1",
        target_version="v2",
        targets=[target],
        total_files=1
    ))

    # Mock planner
    from src.agents.code_migrator.strategy import MigrationPhase
    phase = MigrationPhase("p1", "desc", [target], [], 1)
    strategy = MigrationStrategy([phase], 1, [], "rollback", [])
    agent.planner.plan = AsyncMock(return_value=strategy)

    # Mock transformer
    transform_result = TransformResult("src/file.py", "code", "new code", True)
    agent.transformer.transform = AsyncMock(return_value=transform_result)

    result = await agent.execute(
        context,
        files=files,
        migration_type="framework",
        source_version="v1",
        target_version="v2",
        dry_run=False
    )

    assert result["dry_run"] is False
    assert len(result["transforms"]) == 1
    agent.transformer.transform.assert_called_once()
