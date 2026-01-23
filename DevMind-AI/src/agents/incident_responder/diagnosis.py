"""Root cause diagnosis agent."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .receiver import Alert


@dataclass
class DiagnosisResult:
    """Result of root cause analysis."""
    alert_id: str
    root_cause: str
    confidence: float
    evidence: list[str]
    affected_services: list[str]
    timeline: list[dict]
    recommended_actions: list[str]


class DiagnosisAgent:
    """Analyzes alerts to identify root cause."""

    def __init__(self, llm_client: Any):
        self.llm_client = llm_client

    async def diagnose(
        self,
        alert: Alert,
        correlated_alerts: list[Alert],
        logs: list[str] | None = None,
        metrics: dict | None = None,
    ) -> DiagnosisResult:
        """Perform root cause analysis."""
        # Build context
        context = self._build_context(alert, correlated_alerts, logs, metrics)

        # LLM analysis
        prompt = f"""Analyze this incident and identify root cause:

Primary Alert: {alert.title}
Service: {alert.service}
Description: {alert.description}

Related Alerts:
{[a.title for a in correlated_alerts]}

Recent Logs:
{logs[:10] if logs else "No logs available"}

Metrics:
{metrics or "No metrics available"}

Provide:
1. Most likely root cause
2. Evidence supporting this
3. Affected services
4. Timeline of events
5. Recommended immediate actions

Return JSON with these fields.
"""

        response = await self.llm_client.generate(
            prompt=prompt,
            system="You are an SRE expert diagnosing production incidents.",
            response_format={"type": "json_object"},
        )

        return DiagnosisResult(
            alert_id=alert.id,
            root_cause=response.get("root_cause", "Unknown"),
            confidence=response.get("confidence", 0.5),
            evidence=response.get("evidence", []),
            affected_services=response.get("affected_services", [alert.service]),
            timeline=response.get("timeline", []),
            recommended_actions=response.get("recommended_actions", []),
        )

    def _build_context(self, alert, correlated, logs, metrics) -> dict:
        return {
            "primary": alert,
            "related": correlated,
            "logs": logs,
            "metrics": metrics,
        }
