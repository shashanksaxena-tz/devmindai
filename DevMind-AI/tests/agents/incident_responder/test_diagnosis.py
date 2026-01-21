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

    async def test_diagnose(self, diagnosis_agent, mock_llm):
        alert = Alert(
            id="1", source=AlertSource.CUSTOM, severity=AlertSeverity.HIGH,
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
            "recommended_actions": ["Check network"]
        }
        mock_llm.generate.return_value = mock_response

        result = await diagnosis_agent.diagnose(alert, correlated)

        assert isinstance(result, DiagnosisResult)
        assert result.root_cause == "Network partition"
        assert result.confidence == 0.9
        assert result.affected_services == ["db-service", "api-gateway"]

        mock_llm.generate.assert_called_once()
