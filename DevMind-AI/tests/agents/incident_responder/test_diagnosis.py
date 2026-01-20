import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from src.agents.incident_responder.receiver import Alert, AlertSource, AlertSeverity
from src.agents.incident_responder.diagnosis import DiagnosisAgent, DiagnosisResult

@pytest.mark.asyncio
class TestDiagnosisAgent:
    @pytest.fixture
    def mock_llm(self):
        client = MagicMock()
        client.generate = AsyncMock()
        return client

    @pytest.fixture
    def diagnosis_agent(self, mock_llm):
        return DiagnosisAgent(mock_llm)

    async def test_diagnose_basic(self, diagnosis_agent):
        alert = Alert(
            id="1", source=AlertSource.CUSTOM, severity=AlertSeverity.CRITICAL,
            title="Database Connection Failed", description="Connection timed out",
            timestamp=datetime.now(), service="db-service"
        )
        correlated = []

        mock_response = {
            "root_cause": "Network partition",
            "confidence": 0.9,
            "evidence": ["Logs show timeout", "Metrics show drop"],
            "affected_services": ["db-service", "api-gateway"],
            "timeline": [{"time": "10:00", "event": "Start"}],
            "recommended_actions": ["Restart switch"]
        }
        diagnosis_agent.llm_client.generate.return_value = mock_response

        result = await diagnosis_agent.diagnose(alert, correlated)

        assert isinstance(result, DiagnosisResult)
        assert result.alert_id == alert.id
        assert result.root_cause == "Network partition"
        assert result.confidence == 0.9
        assert result.affected_services == ["db-service", "api-gateway"]

        # Verify LLM called
        diagnosis_agent.llm_client.generate.assert_called_once()

    async def test_diagnose_with_logs_metrics(self, diagnosis_agent):
        alert = Alert(
            id="1", source=AlertSource.CUSTOM, severity=AlertSeverity.HIGH,
            title="High CPU", description="CPU usage > 90%",
            timestamp=datetime.now(), service="compute"
        )
        logs = ["Error: Out of memory", "Warning: High load"]
        metrics = {"cpu": "95%", "memory": "99%"}

        mock_response = {
            "root_cause": "Memory leak",
            "confidence": 0.8
        }
        diagnosis_agent.llm_client.generate.return_value = mock_response

        result = await diagnosis_agent.diagnose(alert, [], logs=logs, metrics=metrics)

        assert result.root_cause == "Memory leak"

        # Check if context passed to LLM prompt (indirectly via arguments)
        call_kwargs = diagnosis_agent.llm_client.generate.call_args.kwargs
        prompt = call_kwargs['prompt']
        assert "Out of memory" in prompt
        assert "95%" in prompt

    async def test_diagnose_fallback(self, diagnosis_agent):
        alert = Alert(
            id="1", source=AlertSource.CUSTOM, severity=AlertSeverity.LOW,
            title="Info", description="Just info",
            timestamp=datetime.now(), service="test"
        )
        # LLM returns unexpected format or None (simulating issue)
        diagnosis_agent.llm_client.generate.return_value = {}

        result = await diagnosis_agent.diagnose(alert, [])

        assert result.root_cause == "Unknown"
        assert result.confidence == 0.5
