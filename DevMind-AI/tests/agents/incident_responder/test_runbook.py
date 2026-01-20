import pytest
from unittest.mock import AsyncMock, MagicMock

from src.agents.incident_responder.runbook import (
    RunbookExecutor, RunbookAction, RunbookActionType, RunbookResult
)

@pytest.mark.asyncio
class TestRunbookExecutor:
    @pytest.fixture
    def mock_llm(self):
        client = MagicMock()
        client.generate = AsyncMock()
        return client

    @pytest.fixture
    def executor(self, mock_llm):
        return RunbookExecutor(mock_llm)

    @pytest.fixture
    def sample_runbook(self):
        return [
            RunbookAction(
                name="Check DB Status",
                action_type=RunbookActionType.COMMAND,
                command="systemctl status postgresql"
            ),
            RunbookAction(
                name="Restart DB",
                action_type=RunbookActionType.COMMAND,
                command="systemctl restart postgresql",
                requires_approval=True
            )
        ]

    async def test_execute_not_found(self, executor):
        result = await executor.execute("missing_book", {})
        assert result.success is False
        assert "not found" in result.error

    async def test_execute_dry_run(self, executor, sample_runbook):
        executor.register_runbook("db_restart", sample_runbook)

        result = await executor.execute("db_restart", {}, dry_run=True)

        # Dry run should process all actions regardless of approval?
        # The code checks approval first:
        # if action.requires_approval and not context.get("approved"): return error
        # So it should stop at the approval step if not approved.

        assert result.success is False
        assert result.actions_completed == 1 # First action completed (dry run)
        assert "requires approval" in result.error
        assert len(result.outputs) == 1
        assert result.outputs[0]["status"] == "dry_run"

    async def test_execute_dry_run_approved(self, executor, sample_runbook):
        executor.register_runbook("db_restart", sample_runbook)

        result = await executor.execute("db_restart", {"approved": True}, dry_run=True)

        assert result.success is True
        assert result.actions_completed == 2
        assert len(result.outputs) == 2
        assert result.outputs[1]["status"] == "dry_run"

    async def test_execute_real(self, executor, sample_runbook):
        executor.register_runbook("db_restart", sample_runbook)

        # Mock _execute_action to ensure it's called (though default impl returns success)
        # We can't easily mock the method on the instance we're testing without patching
        # But for now, we rely on the default implementation which returns success=True

        result = await executor.execute("db_restart", {"approved": True}, dry_run=False)

        assert result.success is True
        assert result.actions_completed == 2
        assert result.outputs[0]["status"] == "executed"
