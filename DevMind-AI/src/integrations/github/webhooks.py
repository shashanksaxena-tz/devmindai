"""GitHub webhook handlers."""
from __future__ import annotations

import hmac
import hashlib
from typing import Any, Dict, Optional
from fastapi import HTTPException


class GitHubWebhookHandler:
    """Handles GitHub webhooks."""

    def __init__(self, webhook_secret: str, agent_orchestrator: Any):
        self.secret = webhook_secret
        self.orchestrator = agent_orchestrator

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature."""
        if not signature:
            return False

        expected = hmac.new(
            self.secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)

    async def handle_webhook(self, event_type: str, payload: dict) -> dict:
        """Route webhook to appropriate handler."""
        handlers = {
            "pull_request": self._handle_pull_request,
            "pull_request_review_comment": self._handle_pr_comment,
            "issue_comment": self._handle_issue_comment,
            "push": self._handle_push,
            "installation": self._handle_installation,
        }

        handler = handlers.get(event_type)
        if not handler:
            return {"status": "ignored", "event": event_type}

        return await handler(payload)

    async def _handle_pull_request(self, payload: dict) -> dict:
        """Handle PR events (opened, synchronize)."""
        action = payload.get("action")
        if action not in ["opened", "synchronize"]:
            return {"status": "ignored", "action": action}

        pr = payload.get("pull_request", {})
        repo = payload.get("repository", {})

        # Trigger code review
        review_result = await self.orchestrator.trigger_review(
            repo_full_name=repo.get("full_name"),
            pr_number=pr.get("number"),
            head_sha=pr.get("head", {}).get("sha"),
        )

        # Trigger security scan
        security_result = await self.orchestrator.trigger_security_scan(
            repo_full_name=repo.get("full_name"),
            pr_number=pr.get("number"),
        )

        return {
            "status": "processed",
            "review_job": review_result.get("job_id"),
            "security_job": security_result.get("job_id"),
        }

    async def _handle_pr_comment(self, payload: dict) -> dict:
        """Handle PR review comments (stub for future use)."""
        return {"status": "processed", "action": "pr_comment"}

    async def _handle_issue_comment(self, payload: dict) -> dict:
        """Handle issue/PR comments for bot commands."""
        comment = payload.get("comment", {})
        body = comment.get("body", "")

        # Check for bot mention
        if "@devmind" not in body.lower():
            return {"status": "ignored", "reason": "no mention"}

        # Parse command
        command = self._parse_command(body)
        if not command:
            return {"status": "ignored", "reason": "no command"}

        # Execute command
        return await self._execute_command(command, payload)

    def _parse_command(self, body: str) -> Optional[Dict[str, Any]]:
        """Parse bot command from comment."""
        import re

        patterns = [
            (r"@devmind\s+review", {"action": "review"}),
            (r"@devmind\s+security", {"action": "security"}),
            (r"@devmind\s+generate-tests", {"action": "generate_tests"}),
            (r"@devmind\s+explain", {"action": "explain"}),
            (r"@devmind\s+optimize", {"action": "optimize"}),
            (r"@devmind\s+docs", {"action": "docs"}),
            (r"@devmind\s+fix\s+(.+)", {"action": "fix", "target": 1}),
        ]

        for pattern, command in patterns:
            match = re.search(pattern, body.lower())
            if match:
                cmd_copy = command.copy()
                if "target" in cmd_copy and isinstance(cmd_copy["target"], int):
                    cmd_copy["target"] = match.group(cmd_copy["target"])
                return cmd_copy

        return None

    async def _execute_command(self, command: dict, payload: dict) -> dict:
        """Execute a bot command."""
        action = command.get("action")
        repo = payload.get("repository", {})
        issue = payload.get("issue", {})

        # Determine if it's a PR or Issue
        pr_number = issue.get("number") # issues and PRs share numbering in GH

        result = {}
        if action == "review":
            result = await self.orchestrator.trigger_review(
                repo_full_name=repo.get("full_name"),
                pr_number=pr_number,
            )
        elif action == "security":
            result = await self.orchestrator.trigger_security_scan(
                repo_full_name=repo.get("full_name"),
                pr_number=pr_number,
            )
        elif action == "generate_tests":
            result = await self.orchestrator.trigger_test_generation(
                repo_full_name=repo.get("full_name"),
                pr_number=pr_number,
            )
        else:
            result = {"status": "unknown_command"}

        return {"status": "executed", "command": action, "result": result}

    async def _handle_push(self, payload: dict) -> dict:
        """Handle push events for main branch."""
        ref = payload.get("ref", "")
        if ref not in ["refs/heads/main", "refs/heads/master"]:
            return {"status": "ignored", "ref": ref}

        repo = payload.get("repository", {})

        # Trigger full analysis on main branch push
        await self.orchestrator.trigger_full_analysis(
            repo_full_name=repo.get("full_name"),
        )

        return {"status": "analysis_triggered"}

    async def _handle_installation(self, payload: dict) -> dict:
        """Handle app installation events."""
        action = payload.get("action")
        installation = payload.get("installation", {})

        if action == "created":
            # New installation
            repos = payload.get("repositories", [])
            await self.orchestrator.setup_repositories(
                installation_id=installation.get("id"),
                repositories=repos,
            )

        return {"status": "processed", "action": action}
