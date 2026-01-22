"""Triage agent for initial alert classification."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .receiver import Alert, AlertSeverity


@dataclass
class TriageResult:
    """Result of alert triage."""
    alert_id: str
    category: str  # performance, availability, security, data, etc.
    adjusted_severity: AlertSeverity
    is_duplicate: bool
    related_alerts: list[str]
    suggested_runbook: Optional[str]
    confidence: float


class TriageAgent:
    """Classifies and prioritizes incoming alerts."""

    CATEGORY_KEYWORDS = {
        "performance": ["latency", "slow", "timeout", "response time", "cpu", "memory"],
        "availability": ["down", "unreachable", "connection", "health check", "503", "502"],
        "security": ["unauthorized", "attack", "breach", "suspicious", "blocked"],
        "data": ["database", "storage", "disk", "corruption", "backup"],
    }

    def __init__(self, llm_client: Any):
        self.llm_client = llm_client

    async def triage(self, alert: Alert, recent_alerts: list[Alert]) -> TriageResult:
        """Triage an incoming alert."""
        # Quick keyword-based categorization
        category = self._categorize(alert)

        # Check for duplicates
        is_duplicate = self._is_duplicate(alert, recent_alerts)
        related = self._find_related(alert, recent_alerts)

        # LLM-assisted severity adjustment
        adjusted_severity = await self._adjust_severity(alert, related)

        # Suggest runbook
        runbook = await self._suggest_runbook(alert, category)

        return TriageResult(
            alert_id=alert.id,
            category=category,
            adjusted_severity=adjusted_severity,
            is_duplicate=is_duplicate,
            related_alerts=[a.id for a in related],
            suggested_runbook=runbook,
            confidence=0.85,
        )

    def _categorize(self, alert: Alert) -> str:
        text = f"{alert.title} {alert.description}".lower()
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                return category
        return "general"

    def _is_duplicate(self, alert: Alert, recent: list[Alert]) -> bool:
        for other in recent:
            if (other.title == alert.title and
                other.service == alert.service and
                abs((alert.timestamp - other.timestamp).total_seconds()) < 300):
                return True
        return False

    def _find_related(self, alert: Alert, recent: list[Alert]) -> list[Alert]:
        current_category = self._categorize(alert)
        return [a for a in recent
                if a.service == alert.service or self._categorize(a) == current_category]

    async def _adjust_severity(self, alert: Alert, related: list[Alert]) -> AlertSeverity:
        # If multiple related alerts, escalate
        if len(related) >= 3:
            if alert.severity == AlertSeverity.MEDIUM:
                return AlertSeverity.HIGH
        return alert.severity

    async def _suggest_runbook(self, alert: Alert, category: str) -> Optional[str]:
        prompt = f"""Suggest a runbook for this alert:
Category: {category}
Title: {alert.title}
Service: {alert.service}

Return the runbook name or "none" if no standard runbook applies.
"""
        response = await self.llm_client.generate(prompt=prompt)
        return response if response != "none" else None
