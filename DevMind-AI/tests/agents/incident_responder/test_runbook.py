import pytest
from unittest.mock import MagicMock

from src.agents.incident_responder.runbook import (
    RunbookExecutor, RunbookAction, RunbookActionType, RunbookResult
)

@pytest.mark.asyncio
class TestRunbookExecutor:
    @pytest.fixture
    def mock_llm(self):
        return MagicMock()

    @pytest.fixture
    def runbook_executor(self, mock_llm):
        return RunbookExecutor(mock_llm)

    def test_register_runbook(self, runbook_executor):
        action = RunbookAction(
            name="Restart Service",
            action_type=RunbookActionType.COMMAND,
            command="systemctl restart service"
        )
        runbook_executor.register_runbook("restart_service", [action])
        assert "restart_service" in runbook_executor.runbooks

    async def test_execute_dry_run(self, runbook_executor):
        action = RunbookAction(
            name="Restart Service",
            action_type=RunbookActionType.COMMAND,
            command="systemctl restart service"
        )
        runbook_executor.register_runbook("restart_service", [action])

        result = await runbook_executor.execute("restart_service", {}, dry_run=True)

        assert isinstance(result, RunbookResult)
        assert result.success is True
        assert result.actions_completed == 1
        assert result.outputs[0]["status"] == "dry_run"

    async def test_execute_not_found(self, runbook_executor):
        result = await runbook_executor.execute("non_existent", {})
        assert result.success is False
        assert "not found" in result.error

    async def test_execute_approval_required(self, runbook_executor):
        action = RunbookAction(
            name="Delete DB",
            action_type=RunbookActionType.COMMAND,
            command="rm -rf /db",
            requires_approval=True
        )
        runbook_executor.register_runbook("delete_db", [action])

        # Without approval (actual execution attempt)
        result = await runbook_executor.execute("delete_db", {"approved": False}, dry_run=False)
        assert result.success is False
        assert "requires approval" in result.error

        # With approval
        result = await runbook_executor.execute("delete_db", {"approved": True}, dry_run=True)
        assert result.success is True

    async def test_execute_approval_required_dry_run_no_approval(self, runbook_executor):
        action = RunbookAction(
            name="Delete DB",
            action_type=RunbookActionType.COMMAND,
            command="rm -rf /db",
            requires_approval=True
        )
        runbook_executor.register_runbook("delete_db", [action])

        # Dry run without approval should succeed but indicate requirement
        result = await runbook_executor.execute("delete_db", {"approved": False}, dry_run=True)
        assert result.success is True
        assert result.outputs[0]["status"] == "dry_run_requires_approval"
