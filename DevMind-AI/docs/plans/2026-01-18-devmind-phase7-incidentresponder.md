# DevMind AI Phase 7: IncidentResponder Agent Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an intelligent incident response agent that monitors production alerts, correlates incidents, identifies root causes, executes runbooks, and generates post-mortems automatically.

**Architecture:** Multi-agent incident response system with Triage (classification), Correlation (linking related alerts), Diagnosis (root cause), Runbook (remediation), and PostMortem (documentation) agents. Uses Claude for complex diagnosis and Gemini for fast triage.

**Tech Stack:** FastAPI, PagerDuty/Datadog webhooks, Slack integration, Redis for alert correlation, Claude API, Gemini API

**Prerequisites:** Phase 1 (Foundation) completed

---

## Task 1: Alert Receiver and Triage Agent

**Files:**
- Create: `src/agents/incident_responder/receiver.py`
- Create: `src/agents/incident_responder/triage.py`
- Test: `tests/agents/incident_responder/test_triage.py`

### Implementation Overview

```python
# src/agents/incident_responder/receiver.py
"""Alert receiver for various monitoring platforms."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class AlertSource(Enum):
    """Supported alert sources."""
    PAGERDUTY = "pagerduty"
    DATADOG = "datadog"
    SENTRY = "sentry"
    CLOUDWATCH = "cloudwatch"
    PROMETHEUS = "prometheus"
    CUSTOM = "custom"


class AlertSeverity(Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Alert:
    """Normalized alert from any source."""
    id: str
    source: AlertSource
    severity: AlertSeverity
    title: str
    description: str
    timestamp: datetime
    service: str
    environment: str = "production"
    metadata: dict = field(default_factory=dict)
    raw_payload: dict = field(default_factory=dict)


class AlertReceiver:
    """Receives and normalizes alerts from various sources."""

    def parse_pagerduty(self, payload: dict) -> Alert:
        """Parse PagerDuty webhook payload."""
        event = payload.get("event", {})
        return Alert(
            id=event.get("id", ""),
            source=AlertSource.PAGERDUTY,
            severity=self._map_pd_severity(event.get("priority", {}).get("name", "P3")),
            title=event.get("title", ""),
            description=event.get("custom_details", {}).get("details", ""),
            timestamp=datetime.fromisoformat(event.get("created_at", datetime.now().isoformat())),
            service=event.get("service", {}).get("name", "unknown"),
            raw_payload=payload,
        )

    def parse_datadog(self, payload: dict) -> Alert:
        """Parse Datadog webhook payload."""
        return Alert(
            id=payload.get("id", ""),
            source=AlertSource.DATADOG,
            severity=self._map_dd_severity(payload.get("priority", "normal")),
            title=payload.get("title", ""),
            description=payload.get("body", ""),
            timestamp=datetime.fromtimestamp(payload.get("date", 0)),
            service=payload.get("tags", {}).get("service", "unknown"),
            raw_payload=payload,
        )

    def _map_pd_severity(self, priority: str) -> AlertSeverity:
        mapping = {"P1": AlertSeverity.CRITICAL, "P2": AlertSeverity.HIGH,
                   "P3": AlertSeverity.MEDIUM, "P4": AlertSeverity.LOW}
        return mapping.get(priority, AlertSeverity.MEDIUM)

    def _map_dd_severity(self, priority: str) -> AlertSeverity:
        mapping = {"critical": AlertSeverity.CRITICAL, "high": AlertSeverity.HIGH,
                   "normal": AlertSeverity.MEDIUM, "low": AlertSeverity.LOW}
        return mapping.get(priority, AlertSeverity.MEDIUM)
```

```python
# src/agents/incident_responder/triage.py
"""Triage agent for initial alert classification."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

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
                (alert.timestamp - other.timestamp).seconds < 300):
                return True
        return False

    def _find_related(self, alert: Alert, recent: list[Alert]) -> list[Alert]:
        return [a for a in recent
                if a.service == alert.service or a.category == self._categorize(alert)]

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
```

---

## Task 2: Correlation and Diagnosis Agents

**Files:**
- Create: `src/agents/incident_responder/correlation.py`
- Create: `src/agents/incident_responder/diagnosis.py`
- Test: `tests/agents/incident_responder/test_diagnosis.py`

### Implementation Overview

```python
# src/agents/incident_responder/diagnosis.py
"""Root cause diagnosis agent."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

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
```

---

## Task 3: Runbook Executor

**Files:**
- Create: `src/agents/incident_responder/runbook.py`
- Test: `tests/agents/incident_responder/test_runbook.py`

### Implementation Overview

```python
# src/agents/incident_responder/runbook.py
"""Runbook execution agent."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


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
            if action.requires_approval and not context.get("approved"):
                return RunbookResult(
                    runbook_name=runbook_name,
                    success=False,
                    actions_completed=i,
                    actions_total=len(actions),
                    outputs=outputs,
                    error=f"Action '{action.name}' requires approval",
                )

            if dry_run:
                outputs.append({"action": action.name, "status": "dry_run", "would_execute": action.command})
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
```

---

## Task 4: PostMortem Generator

**Files:**
- Create: `src/agents/incident_responder/postmortem.py`
- Test: `tests/agents/incident_responder/test_postmortem.py`

### Implementation Overview

```python
# src/agents/incident_responder/postmortem.py
"""Post-mortem generation agent."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .diagnosis import DiagnosisResult
from .runbook import RunbookResult


@dataclass
class PostMortem:
    """Generated post-mortem document."""
    title: str
    incident_id: str
    summary: str
    timeline: list[dict]
    root_cause: str
    impact: str
    resolution: str
    action_items: list[dict]
    lessons_learned: list[str]
    markdown: str


class PostMortemGenerator:
    """Generates post-mortem documents."""

    def __init__(self, llm_client: Any):
        self.llm_client = llm_client

    async def generate(
        self,
        incident_id: str,
        diagnosis: DiagnosisResult,
        runbook_result: RunbookResult | None,
        timeline_events: list[dict],
    ) -> PostMortem:
        """Generate a post-mortem document."""
        prompt = f"""Generate a post-mortem for this incident:

Incident ID: {incident_id}
Root Cause: {diagnosis.root_cause}
Confidence: {diagnosis.confidence}
Evidence: {diagnosis.evidence}
Affected Services: {diagnosis.affected_services}

Resolution: {runbook_result.runbook_name if runbook_result else "Manual"}
Timeline Events: {timeline_events}

Generate a comprehensive post-mortem with:
1. Executive summary
2. Detailed timeline
3. Root cause analysis
4. Impact assessment
5. Resolution steps
6. Action items (with owners)
7. Lessons learned

Return JSON with all these sections.
"""

        response = await self.llm_client.generate(
            prompt=prompt,
            system="You are an SRE writing a blameless post-mortem.",
            response_format={"type": "json_object"},
        )

        markdown = self._format_markdown(response)

        return PostMortem(
            title=response.get("title", f"Post-Mortem: {incident_id}"),
            incident_id=incident_id,
            summary=response.get("summary", ""),
            timeline=response.get("timeline", timeline_events),
            root_cause=diagnosis.root_cause,
            impact=response.get("impact", ""),
            resolution=response.get("resolution", ""),
            action_items=response.get("action_items", []),
            lessons_learned=response.get("lessons_learned", []),
            markdown=markdown,
        )

    def _format_markdown(self, data: dict) -> str:
        """Format post-mortem as Markdown."""
        return f"""# {data.get('title', 'Post-Mortem')}

## Summary
{data.get('summary', '')}

## Timeline
{self._format_timeline(data.get('timeline', []))}

## Root Cause
{data.get('root_cause', '')}

## Impact
{data.get('impact', '')}

## Resolution
{data.get('resolution', '')}

## Action Items
{self._format_action_items(data.get('action_items', []))}

## Lessons Learned
{self._format_list(data.get('lessons_learned', []))}
"""

    def _format_timeline(self, timeline: list) -> str:
        return "\n".join([f"- **{e.get('time')}**: {e.get('event')}" for e in timeline])

    def _format_action_items(self, items: list) -> str:
        return "\n".join([f"- [ ] {i.get('description')} (@{i.get('owner', 'TBD')})" for i in items])

    def _format_list(self, items: list) -> str:
        return "\n".join([f"- {item}" for item in items])
```

---

## Task 5: IncidentResponder Agent and API

**Files:**
- Create: `src/agents/incident_responder/agent.py`
- Create: `src/api/routes/incidents.py`
- Test: `tests/agents/incident_responder/test_agent.py`

### Implementation Overview

```python
# src/agents/incident_responder/agent.py
"""IncidentResponder agent orchestrating incident response."""
from __future__ import annotations

from typing import Any

from src.core.agents import BaseAgent, AgentContext, TaskComplexity

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
        }
```

---

## Summary

Phase 7 (IncidentResponder Agent) consists of 5 tasks:

1. **Alert Receiver & Triage** - Normalize alerts from various sources and classify
2. **Correlation & Diagnosis** - Link related alerts and identify root cause
3. **Runbook Executor** - Execute remediation runbooks
4. **PostMortem Generator** - Generate blameless post-mortems
5. **IncidentResponder Agent & API** - Orchestration and REST/webhook endpoints

**Estimated Implementation Time:** ~2 weeks

**Dependencies:** Phase 1 (Foundation)
