"""Runbook execution agent."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class RunbookActionType(Enum):
    """Types of runbook actions."""
    COMMAND = "command"  # Shell command
    API_CALL = "api_call"  # HTTP request
    NOTIFICATION = "notification"  # Slack/email
    APPROVAL_REQUIRED = "approval"  # Needs human approval
    QUERY = "query"  # Database/metrics query


@dataclass
class RunbookAction:
    """A single action in a runbook."""
    name: str
    action_type: RunbookActionType
    command: str
    requires_approval: bool = False
    timeout_seconds: int = 60
    rollback_command: Optional[str] = None


@dataclass
class RunbookResult:
    """Result of runbook execution."""
    runbook_name: str
    success: bool
    actions_completed: int
    actions_total: int
    outputs: list[dict]
    error: Optional[str] = None


class RunbookExecutor:
    """Executes runbooks for incident remediation."""

    def __init__(self, llm_client: Any):
        self.llm_client = llm_client
        self.runbooks: dict[str, list[RunbookAction]] = {}

    def register_runbook(self, name: str, actions: list[RunbookAction]):
        """Register a runbook."""
        self.runbooks[name] = actions

    async def execute(
        self,
        runbook_name: str,
        context: dict,
        dry_run: bool = True,
    ) -> RunbookResult:
        """Execute a runbook."""
        if runbook_name not in self.runbooks:
            return RunbookResult(
                runbook_name=runbook_name,
                success=False,
                actions_completed=0,
                actions_total=0,
                outputs=[],
                error=f"Runbook '{runbook_name}' not found",
            )

        actions = self.runbooks[runbook_name]
        outputs = []

        for i, action in enumerate(actions):
            if action.requires_approval and not context.get("approved") and not dry_run:
                return RunbookResult(
                    runbook_name=runbook_name,
                    success=False,
                    actions_completed=i,
                    actions_total=len(actions),
                    outputs=outputs,
                    error=f"Action '{action.name}' requires approval",
                )

            if dry_run:
                status = "dry_run"
                if action.requires_approval and not context.get("approved"):
                    status = "dry_run_requires_approval"
                outputs.append({"action": action.name, "status": status, "would_execute": action.command})
            else:
                result = await self._execute_action(action, context)
                outputs.append(result)
                if not result.get("success"):
                    return RunbookResult(
                        runbook_name=runbook_name,
                        success=False,
                        actions_completed=i,
                        actions_total=len(actions),
                        outputs=outputs,
                        error=result.get("error"),
                    )

        return RunbookResult(
            runbook_name=runbook_name,
            success=True,
            actions_completed=len(actions),
            actions_total=len(actions),
            outputs=outputs,
        )

    async def _execute_action(self, action: RunbookAction, context: dict) -> dict:
        """Execute a single action."""
        # In production, this would actually execute commands
        return {"action": action.name, "status": "executed", "success": True}
