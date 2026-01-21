import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from src.agents.incident_responder.receiver import AlertReceiver, AlertSource, AlertSeverity, Alert
from src.agents.incident_responder.triage import TriageAgent, TriageResult

class TestAlertReceiver:
    def test_parse_pagerduty(self):
        receiver = AlertReceiver()
        payload = {
            "event": {
                "id": "evt123",
                "priority": {"name": "P1"},
                "title": "Database Down",
                "custom_details": {"details": "Connection refused"},
                "created_at": "2023-10-27T10:00:00",
                "service": {"name": "db-service"}
            }
        }
        alert = receiver.parse_pagerduty(payload)
        assert alert.id == "evt123"
        assert alert.source == AlertSource.PAGERDUTY
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.title == "Database Down"
        assert alert.description == "Connection refused"
        assert alert.service == "db-service"

    def test_parse_datadog(self):
        receiver = AlertReceiver()
        payload = {
            "id": "dd123",
            "priority": "critical",
            "title": "High Latency",
            "body": "Latency > 500ms",
            "date": 1698400800, # 2023-10-27 10:00:00 UTC
            "tags": {"service": "api-gateway"}
        }
        alert = receiver.parse_datadog(payload)
        assert alert.id == "dd123"
        assert alert.source == AlertSource.DATADOG
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.title == "High Latency"
        assert alert.description == "Latency > 500ms"
        assert alert.service == "api-gateway"


@pytest.mark.asyncio
class TestTriageAgent:
    @pytest.fixture
    def mock_llm(self):
        client = MagicMock()
        client.generate = AsyncMock()
        return client

    @pytest.fixture
    def triage_agent(self, mock_llm):
        return TriageAgent(mock_llm)

    async def test_triage_categorization(self, triage_agent):
        alert = Alert(
            id="1", source=AlertSource.CUSTOM, severity=AlertSeverity.MEDIUM,
            title="Slow response", description="Latency is high",
            timestamp=datetime.now(), service="web"
        )
        triage_agent.llm_client.generate.return_value = "none"

        result = await triage_agent.triage(alert, [])
        assert result.category == "performance"
        assert result.confidence == 0.85

    async def test_triage_duplicate(self, triage_agent):
        now = datetime.now()
        alert1 = Alert(
            id="1", source=AlertSource.CUSTOM, severity=AlertSeverity.MEDIUM,
            title="Slow response", description="Latency is high",
            timestamp=now, service="web"
        )
        alert2 = Alert(
            id="2", source=AlertSource.CUSTOM, severity=AlertSeverity.MEDIUM,
            title="Slow response", description="Latency is high",
            timestamp=now - timedelta(seconds=100), service="web"
        )

        triage_agent.llm_client.generate.return_value = "none"
        result = await triage_agent.triage(alert1, [alert2])
        assert result.is_duplicate is True

    async def test_triage_severity_adjustment(self, triage_agent):
        # 3 related alerts should escalate severity
        now = datetime.now()
        alert = Alert(
            id="new", source=AlertSource.CUSTOM, severity=AlertSeverity.MEDIUM,
            title="Service down", description="503 errors",
            timestamp=now, service="auth"
        )
        related = [
            Alert(id=f"{i}", source=AlertSource.CUSTOM, severity=AlertSeverity.MEDIUM,
                  title="Service down", description="503 errors",
                  timestamp=now - timedelta(minutes=i), service="auth")
            for i in range(1, 4)
        ]

        triage_agent.llm_client.generate.return_value = "none"
        result = await triage_agent.triage(alert, related)
        assert result.adjusted_severity == AlertSeverity.HIGH

    async def test_suggest_runbook(self, triage_agent):
        alert = Alert(
            id="1", source=AlertSource.CUSTOM, severity=AlertSeverity.HIGH,
            title="Database locked", description="Deadlocks detected",
            timestamp=datetime.now(), service="db"
        )
        triage_agent.llm_client.generate.return_value = "restart_db_runbook"

        result = await triage_agent.triage(alert, [])
        assert result.suggested_runbook == "restart_db_runbook"
