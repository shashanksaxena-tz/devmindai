import pytest
from unittest.mock import AsyncMock, MagicMock

from src.agents.incident_responder.diagnosis import DiagnosisResult
from src.agents.incident_responder.runbook import RunbookResult
from src.agents.incident_responder.postmortem import PostMortemGenerator, PostMortem

@pytest.mark.asyncio
class TestPostMortemGenerator:
    @pytest.fixture
    def mock_llm(self):
        client = MagicMock()
        client.generate = AsyncMock()
        return client

    @pytest.fixture
    def generator(self, mock_llm):
        return PostMortemGenerator(mock_llm)

    async def test_generate(self, generator):
        diagnosis = DiagnosisResult(
            alert_id="1", root_cause="Bug", confidence=1.0,
            evidence=["Log error"], affected_services=["api"]
        )
        runbook = RunbookResult(
            runbook_name="restart", success=True, actions_completed=1,
            actions_total=1, outputs=[]
        )
        timeline = [{"time": "12:00", "event": "Alert"}]

        mock_response = {
            "title": "Post-Mortem: Incident 1",
            "summary": "Bad bug",
            "timeline": [{"time": "12:00", "event": "Alert"}, {"time": "12:05", "event": "Fixed"}],
            "root_cause": "Bug",
            "impact": "Downtime",
            "resolution": "Restarted",
            "action_items": [{"description": "Fix bug", "owner": "Alice"}],
            "lessons_learned": ["Test more"]
        }
        generator.llm_client.generate.return_value = mock_response

        result = await generator.generate("inc-123", diagnosis, runbook, timeline)

        assert isinstance(result, PostMortem)
        assert result.title == "Post-Mortem: Incident 1"
        assert result.root_cause == "Bug"
        assert len(result.action_items) == 1
        assert "Alice" in result.markdown
        assert "Test more" in result.markdown
