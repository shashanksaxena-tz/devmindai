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
