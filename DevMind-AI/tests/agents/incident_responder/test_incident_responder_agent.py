import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.agents.incident_responder.agent import IncidentResponderAgent
from src.agents.base import AgentContext
from src.agents.incident_responder.receiver import AlertSeverity
from src.agents.incident_responder.triage import TriageResult
from src.agents.incident_responder.diagnosis import DiagnosisResult
from src.agents.incident_responder.runbook import RunbookResult

@pytest.mark.asyncio
class TestIncidentResponderAgent:
    @pytest.fixture
    def mock_router(self):
        router = MagicMock()
        client = MagicMock()
        client.generate = AsyncMock()
        router.get_client.return_value = client
        return router

    @pytest.fixture
    def agent(self, mock_router):
        return IncidentResponderAgent(router=mock_router)

    async def test_execute_pagerduty(self, agent, mocker):
        # Mock sub-agents
        mocker.patch.object(agent.receiver, 'parse_pagerduty')
        mocker.patch.object(agent.triage, 'triage')
        mocker.patch.object(agent.diagnosis, 'diagnose')
        mocker.patch.object(agent.runbook, 'execute')

        # Setup return values
        alert_mock = MagicMock()
        alert_mock.id = "evt123"
        agent.receiver.parse_pagerduty.return_value = alert_mock

        agent.triage.triage.return_value = TriageResult(
            alert_id="evt123", category="db", adjusted_severity=AlertSeverity.HIGH,
            is_duplicate=False, related_alerts=[], suggested_runbook="restart_db", confidence=1.0
        )

        agent.diagnosis.diagnose.return_value = DiagnosisResult(
            alert_id="evt123", root_cause="timeout", confidence=0.9,
            evidence=[], affected_services=[], timeline=[], recommended_actions=[]
        )

        agent.runbook.execute.return_value = RunbookResult(
            runbook_name="restart_db", success=True, actions_completed=1,
            actions_total=1, outputs=[]
        )

        # Execute
        context = AgentContext()
        result = await agent.execute(
            context,
            alert_payload={"event": {"id": "evt123"}},
            source="pagerduty"
        )

        # Verify
        assert result["alert_id"] == "evt123"
        assert result["triage"]["category"] == "db"
        assert result["diagnosis"]["root_cause"] == "timeout"
        assert result["runbook"]["name"] == "restart_db"
        assert result["runbook"]["success"] is True

        agent.receiver.parse_pagerduty.assert_called_once()
        agent.triage.triage.assert_called_once()
        agent.diagnosis.diagnose.assert_called_once()
        agent.runbook.execute.assert_called_once()
