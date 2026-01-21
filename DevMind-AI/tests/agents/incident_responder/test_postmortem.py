import pytest
from unittest.mock import AsyncMock, MagicMock

from src.agents.incident_responder.postmortem import PostMortemGenerator, PostMortem
from src.agents.incident_responder.diagnosis import DiagnosisResult
from src.agents.incident_responder.runbook import RunbookResult

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

    async def test_generate(self, generator, mock_llm):
        diagnosis = DiagnosisResult(
            alert_id="1", root_cause="Bug in code", confidence=1.0,
            evidence=[], affected_services=[], timeline=[], recommended_actions=[]
        )
        runbook = RunbookResult(
            runbook_name="rollback", success=True, actions_completed=1,
            actions_total=1, outputs=[]
        )
        timeline = [{"time": "10:00", "event": "Alert"}, {"time": "10:05", "event": "Resolved"}]

        mock_response = {
            "title": "Incident 1 Post-Mortem",
            "summary": "Summary text",
            "timeline": timeline,
            "root_cause": "Bug in code",
            "impact": "Low",
            "resolution": "Rollback",
            "action_items": [{"description": "Fix bug", "owner": "Alice"}],
            "lessons_learned": ["Test more"]
        }
        mock_llm.generate.return_value = mock_response

        result = await generator.generate("inc-1", diagnosis, runbook, timeline)

        assert isinstance(result, PostMortem)
        assert result.title == "Incident 1 Post-Mortem"
        assert result.root_cause == "Bug in code"
        assert "# Incident 1 Post-Mortem" in result.markdown
        assert "- [ ] Fix bug (@Alice)" in result.markdown
