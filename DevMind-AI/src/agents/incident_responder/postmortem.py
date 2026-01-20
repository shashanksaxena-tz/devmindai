"""Post-mortem generation agent."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

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
        return "\n".join([f"- **{e.get('time', 'N/A')}**: {e.get('event', '')}" for e in timeline])

    def _format_action_items(self, items: list) -> str:
        return "\n".join([f"- [ ] {i.get('description', '')} (@{i.get('owner', 'TBD')})" for i in items])

    def _format_list(self, items: list) -> str:
        return "\n".join([f"- {item}" for item in items])
