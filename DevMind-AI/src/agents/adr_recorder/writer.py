# src/agents/adr_recorder/writer.py
"""Generates Architecture Decision Records."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
import json

from .capture import DecisionPoint


@dataclass
class ADR:
    """An Architecture Decision Record."""
    number: int
    title: str
    status: str  # proposed, accepted, deprecated, superseded
    date: datetime
    context: str
    decision: str
    consequences: str
    options_considered: list[dict]
    deciders: list[str]
    source_link: Optional[str]
    supersedes: Optional[int]
    superseded_by: Optional[int]

    def to_markdown(self) -> str:
        """Convert to Markdown format."""
        return f"""# ADR-{self.number:04d}: {self.title}

**Status**: {self.status}
**Date**: {self.date.strftime('%Y-%m-%d')}
**Deciders**: {', '.join(self.deciders)}

## Context

{self.context}

## Options Considered

{self._format_options()}

## Decision

{self.decision}

## Consequences

{self.consequences}

{f'## Links\\n\\n- Supersedes: ADR-{self.supersedes:04d}' if self.supersedes else ''}
"""

    def _format_options(self) -> str:
        parts = []
        for i, opt in enumerate(self.options_considered, 1):
            chosen = " ✅" if opt.get("chosen") else ""
            parts.append(f"""### Option {i}: {opt.get('name', 'Unnamed')}{chosen}

{opt.get('description', '')}

**Pros**: {', '.join(opt.get('pros', []))}
**Cons**: {', '.join(opt.get('cons', []))}
""")
        return "\n".join(parts)


class ADRWriter:
    """Generates ADRs from decision points."""

    def __init__(self, llm_client: Any):
        self.llm_client = llm_client

    async def generate_adr(
        self,
        decision: DecisionPoint,
        adr_number: int,
        existing_adrs: list[ADR] | None = None,
    ) -> ADR:
        """Generate an ADR from a decision point."""
        # Enrich with context
        enriched = await self._enrich_decision(decision, existing_adrs)

        prompt = f"""Generate an Architecture Decision Record:

Decision Context: {decision.context}
Decision Made: {decision.decision_made}
Rationale: {decision.rationale}
Options Discussed: {decision.options_discussed}
Participants: {decision.participants}

Generate a complete ADR with:
1. Clear title
2. Context explaining the problem
3. Options with pros/cons for each
4. The decision and reasoning
5. Consequences (positive and negative)

Return JSON with: title, context, decision, consequences, options (array with name, description, pros, cons, chosen)
"""

        if hasattr(self.llm_client, "generate_structured"):
             response = await self.llm_client.generate_structured(
                prompt=prompt,
                system="You are a technical writer creating Architecture Decision Records.",
                response_format={"type": "json_object"},
            )
        else:
            response_str = await self.llm_client.generate(
                prompt=prompt,
                system="You are a technical writer creating Architecture Decision Records.",
            )
            try:
                clean_str = response_str.strip().replace("```json", "").replace("```", "")
                response = json.loads(clean_str)
            except json.JSONDecodeError:
                response = {}

        return ADR(
            number=adr_number,
            title=response.get("title", "Untitled Decision"),
            status="accepted" if decision.decision_made else "proposed",
            date=decision.timestamp,
            context=response.get("context", decision.context),
            decision=response.get("decision", decision.decision_made or ""),
            consequences=response.get("consequences", ""),
            options_considered=response.get("options", decision.options_discussed),
            deciders=decision.participants,
            source_link=None,
            supersedes=enriched.get("supersedes"),
            superseded_by=None,
        )

    async def _enrich_decision(
        self,
        decision: DecisionPoint,
        existing_adrs: list[ADR] | None,
    ) -> dict:
        """Enrich decision with related context."""
        result = {}

        if existing_adrs:
            # Check if this supersedes an existing ADR
            for adr in existing_adrs:
                if self._is_related(decision, adr):
                    result["supersedes"] = adr.number
                    break

        return result

    def _is_related(self, decision: DecisionPoint, adr: ADR) -> bool:
        """Check if decision relates to existing ADR."""
        # Simple keyword matching
        decision_words = set(decision.context.lower().split())
        adr_words = set(adr.context.lower().split())
        overlap = len(decision_words & adr_words) / max(len(decision_words), 1)
        return overlap > 0.3
