# src/agents/adr_recorder/capture.py
"""Captures architecture decisions from various sources."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import re
import json


class DecisionSource(Enum):
    """Sources of architecture decisions."""
    SLACK = "slack"
    PR_COMMENT = "pr_comment"
    MEETING = "meeting"
    MANUAL = "manual"


@dataclass
class DecisionPoint:
    """A captured decision point."""
    id: str
    source: DecisionSource
    timestamp: datetime
    participants: list[str]
    context: str
    options_discussed: list[dict]
    decision_made: Optional[str]
    rationale: Optional[str]
    raw_content: str


class DecisionCaptureAgent:
    """Captures decision points from conversations."""

    # Patterns that indicate architecture discussions
    DECISION_PATTERNS = [
        r"should we (use|go with|choose|pick)",
        r"what if we",
        r"let's (use|go with)",
        r"i think we should",
        r"decision:",
        r"decided to",
        r"after discussing",
        r"trade-?offs?",
        r"pros and cons",
        r"vs\.",
        r"alternative",
    ]

    def __init__(self, llm_client: Any):
        self.llm_client = llm_client

    async def analyze_conversation(
        self,
        messages: list[dict],
        source: DecisionSource,
    ) -> list[DecisionPoint]:
        """Analyze a conversation for decision points."""
        decisions = []

        # Combine messages into conversation text
        conversation = "\n".join([
            f"{m.get('author', 'Unknown')}: {m.get('content', '')}"
            for m in messages
        ])

        # Check if contains decision patterns
        if not self._contains_decision_patterns(conversation):
            return []

        # Use LLM to extract decision points
        prompt = f"""Analyze this conversation for architecture decisions:

{conversation[:3000]}

For each decision found, extract:
- context: what problem was being discussed
- options: what alternatives were considered
- decision: what was decided (if any)
- rationale: why this decision was made

Return JSON: {{"decisions": [...]}}
"""
        # Note: If LLM returns string, we try to parse it.
        # But if the client supports structured output, better use it.
        # Assuming the base client has generate_structured if supported, otherwise returns str.
        # Here we assume the client returns a dictionary if response_format is set, OR we handle string.
        # But per review, BaseLLMClient.generate returns str.

        # We'll try to use generate_structured if available, or parse the string.
        if hasattr(self.llm_client, "generate_structured"):
             response = await self.llm_client.generate_structured(
                prompt=prompt,
                system="You are an expert at identifying architecture decisions in conversations.",
                response_format={"type": "json_object"},
            )
        else:
            response_str = await self.llm_client.generate(
                prompt=prompt,
                system="You are an expert at identifying architecture decisions in conversations.",
            )
            try:
                # Clean markdown code blocks if present
                clean_str = response_str.strip().replace("```json", "").replace("```", "")
                response = json.loads(clean_str)
            except json.JSONDecodeError:
                response = {}

        for i, d in enumerate(response.get("decisions", [])):
            decisions.append(DecisionPoint(
                id=f"{source.value}-{datetime.now().timestamp()}-{i}",
                source=source,
                timestamp=datetime.now(),
                participants=list(set(m.get("author", "Unknown") for m in messages)),
                context=d.get("context", ""),
                options_discussed=d.get("options", []),
                decision_made=d.get("decision"),
                rationale=d.get("rationale"),
                raw_content=conversation,
            ))

        return decisions

    def _contains_decision_patterns(self, text: str) -> bool:
        """Check if text contains decision-related patterns."""
        text_lower = text.lower()
        return any(re.search(p, text_lower) for p in self.DECISION_PATTERNS)
