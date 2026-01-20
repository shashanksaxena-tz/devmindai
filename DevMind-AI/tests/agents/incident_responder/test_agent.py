import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.agents.incident_responder.agent import IncidentResponderAgent
from src.agents.incident_responder.receiver import Alert, AlertSource, AlertSeverity
from src.agents.incident_responder.triage import TriageResult
from src.agents.incident_responder.diagnosis import DiagnosisResult
from src.agents.incident_responder.runbook import RunbookResult
from src.agents.incident_responder.postmortem import PostMortem

@pytest.mark.asyncio
class TestIncidentResponderAgent:
    @pytest.fixture
    def mock_llm(self):
        client = MagicMock()
        client.generate = AsyncMock()
        return client

    @pytest.fixture
    def agent(self, mock_llm):
        agent = IncidentResponderAgent(mock_llm)
        # Mock sub-agents
        agent.triage = AsyncMock()
        agent.diagnosis = AsyncMock()
        agent.runbook = AsyncMock()
        agent.postmortem = AsyncMock()
        return agent

    async def test_execute_flow(self, agent):
        # Setup mocks
        triage_res = TriageResult(
            alert_id="1", category="performance", adjusted_severity=AlertSeverity.HIGH,
            is_duplicate=False, related_alerts=[], suggested_runbook="restart_service",
            confidence=0.9
        )
        agent.triage.triage.return_value = triage_res

        diagnosis_res = DiagnosisResult(
            alert_id="1", root_cause="Memory leak", confidence=0.8,
            recommended_actions=["Restart"]
        )
        agent.diagnosis.diagnose.return_value = diagnosis_res

        runbook_res = RunbookResult(
            runbook_name="restart_service", success=True, actions_completed=2,
            actions_total=2, outputs=[]
        )
        agent.runbook.execute.return_value = runbook_res

        postmortem_res = PostMortem(
            title="PM", incident_id="1", summary="Sum", timeline=[],
            root_cause="Bug", impact="High", resolution="Fixed",
            action_items=[], lessons_learned=[], markdown="# PM"
        )
        agent.postmortem.generate.return_value = postmortem_res

        # Execute
        payload = {
            "event": {
                "id": "1",
                "priority": {"name": "P1"},
                "title": "Slow",
                "custom_details": {"details": "Very slow"},
                "created_at": datetime.now().isoformat(),
                "service": {"name": "web"}
            }
        }

        result = await agent.execute(
            context=MagicMock(),
            alert_payload=payload,
            source="pagerduty"
        )

        # Verify flow
        agent.triage.triage.assert_called_once()
        agent.diagnosis.diagnose.assert_called_once()

        # Check runbook execution args
        agent.runbook.execute.assert_called_once()
        call_args = agent.runbook.execute.call_args
        assert call_args.args[0] == "restart_service"
        assert call_args.kwargs["dry_run"] is True
        assert "alert" in call_args.kwargs["context"]
        assert call_args.kwargs["context"]["alert"].id == "1"

        # Check result
        assert result["triage"]["category"] == "performance"
        assert result["diagnosis"]["root_cause"] == "Memory leak"
        assert result["runbook"]["executed"] is True
        assert result["postmortem"]["summary"] == "Sum"
