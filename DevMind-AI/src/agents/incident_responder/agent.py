"""IncidentResponder agent orchestrating incident response."""
from __future__ import annotations

from typing import Any

from src.agents.base import BaseAgent, AgentContext, TaskComplexity

from .receiver import AlertReceiver, Alert
from .triage import TriageAgent
from .diagnosis import DiagnosisAgent
from .runbook import RunbookExecutor
from .postmortem import PostMortemGenerator


class IncidentResponderAgent(BaseAgent):
    """Agent that handles production incident response."""

    name = "incident_responder"
    description = "Monitors alerts, diagnoses issues, and automates incident response"
    complexity = TaskComplexity.COMPLEX

    def __init__(self, llm_client: Any):
        super().__init__(llm_client)
        self.receiver = AlertReceiver()
        self.triage = TriageAgent(llm_client)
        self.diagnosis = DiagnosisAgent(llm_client)
        self.runbook = RunbookExecutor(llm_client)
        self.postmortem = PostMortemGenerator(llm_client)

    async def execute(
        self,
        context: AgentContext,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Process an incoming alert through the full incident response pipeline."""
        alert_payload = kwargs.get("alert_payload", {})
        source = kwargs.get("source", "pagerduty")

        # Parse alert
        if source == "pagerduty":
            alert = self.receiver.parse_pagerduty(alert_payload)
        elif source == "datadog":
            alert = self.receiver.parse_datadog(alert_payload)
        else:
            return {"error": f"Unsupported source: {source}"}

        # Triage
        triage_result = await self.triage.triage(alert, [])

        # Diagnose
        diagnosis_result = await self.diagnosis.diagnose(alert, [])

        # Execute runbook if suggested
        runbook_result = None
        if triage_result.suggested_runbook:
            runbook_result = await self.runbook.execute(
                triage_result.suggested_runbook,
                context={"alert": alert},
                dry_run=True,
            )

        # Generate PostMortem (Optional? Or always?)
        # The plan doesn't explicitly say when to generate postmortem in execute flow,
        # but usually it's done after resolution.
        # For this implementation, let's include it if runbook was executed or if we have a diagnosis.
        postmortem = await self.postmortem.generate(
            alert.id,
            diagnosis_result,
            runbook_result,
            [{"time": alert.timestamp.isoformat(), "event": "Alert Triggered"}]
        )

        return {
            "alert_id": alert.id,
            "triage": {
                "category": triage_result.category,
                "severity": triage_result.adjusted_severity.value,
                "is_duplicate": triage_result.is_duplicate,
            },
            "diagnosis": {
                "root_cause": diagnosis_result.root_cause,
                "confidence": diagnosis_result.confidence,
                "recommended_actions": diagnosis_result.recommended_actions,
            },
            "runbook": {
                "name": triage_result.suggested_runbook,
                "executed": runbook_result is not None,
                "success": runbook_result.success if runbook_result else None,
            },
            "postmortem": {
                "summary": postmortem.summary,
                "markdown": postmortem.markdown
            }
        }
