# DevMind AI Phase 10: ADRRecorder Agent Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an intelligent Architecture Decision Record (ADR) agent that captures architecture discussions, generates structured ADRs, maintains decision history, and suggests relevant past decisions.

**Architecture:** Decision capture system with Capture (conversation monitoring), Enrichment (context addition), Writer (ADR generation), and Indexer (semantic search). Uses Claude for decision understanding and Gemini for fast indexing.

**Tech Stack:** FastAPI, Slack API, Qdrant for semantic search, Claude API, Gemini API

**Prerequisites:** Phase 1 (Foundation) completed

---

## Task 1: Decision Capture Agent

**Files:**
- Create: `src/agents/adr_recorder/capture.py`
- Test: `tests/agents/adr_recorder/test_capture.py`

### Implementation Overview

```python
# src/agents/adr_recorder/capture.py
"""Captures architecture decisions from various sources."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


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

        response = await self.llm_client.generate(
            prompt=prompt,
            system="You are an expert at identifying architecture decisions in conversations.",
            response_format={"type": "json_object"},
        )

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
        import re
        text_lower = text.lower()
        return any(re.search(p, text_lower) for p in self.DECISION_PATTERNS)
```

---

## Task 2: ADR Writer

**Files:**
- Create: `src/agents/adr_recorder/writer.py`
- Test: `tests/agents/adr_recorder/test_writer.py`

### Implementation Overview

```python
# src/agents/adr_recorder/writer.py
"""Generates Architecture Decision Records."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

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

        response = await self.llm_client.generate(
            prompt=prompt,
            system="You are a technical writer creating Architecture Decision Records.",
            response_format={"type": "json_object"},
        )

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
```

---

## Task 3: ADR Indexer (Semantic Search)

**Files:**
- Create: `src/agents/adr_recorder/indexer.py`
- Test: `tests/agents/adr_recorder/test_indexer.py`

### Implementation Overview

```python
# src/agents/adr_recorder/indexer.py
"""Indexes ADRs for semantic search."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .writer import ADR


@dataclass
class SearchResult:
    """A search result."""
    adr_number: int
    title: str
    score: float
    context_preview: str


class ADRIndexer:
    """Indexes and searches ADRs using vector embeddings."""

    def __init__(self, qdrant_client: Any, embedding_client: Any):
        self.qdrant = qdrant_client
        self.embedder = embedding_client
        self.collection_name = "adr_embeddings"

    async def index_adr(self, adr: ADR) -> None:
        """Index an ADR for semantic search."""
        # Create embedding from title + context + decision
        text = f"{adr.title}\n{adr.context}\n{adr.decision}"
        embedding = await self.embedder.embed(text)

        # Store in Qdrant
        await self.qdrant.upsert(
            collection_name=self.collection_name,
            points=[{
                "id": adr.number,
                "vector": embedding,
                "payload": {
                    "number": adr.number,
                    "title": adr.title,
                    "status": adr.status,
                    "context": adr.context[:500],
                    "decision": adr.decision[:500],
                    "date": adr.date.isoformat(),
                },
            }],
        )

    async def search(
        self,
        query: str,
        limit: int = 5,
        status_filter: Optional[str] = None,
    ) -> list[SearchResult]:
        """Search for relevant ADRs."""
        embedding = await self.embedder.embed(query)

        filter_conditions = None
        if status_filter:
            filter_conditions = {"status": status_filter}

        results = await self.qdrant.search(
            collection_name=self.collection_name,
            query_vector=embedding,
            limit=limit,
            query_filter=filter_conditions,
        )

        return [
            SearchResult(
                adr_number=r.payload["number"],
                title=r.payload["title"],
                score=r.score,
                context_preview=r.payload["context"][:200],
            )
            for r in results
        ]

    async def find_related(self, adr: ADR, limit: int = 3) -> list[SearchResult]:
        """Find ADRs related to a given ADR."""
        return await self.search(
            f"{adr.title} {adr.context[:200]}",
            limit=limit + 1,  # +1 to exclude self
        )
```

---

## Task 4: ADRRecorder Agent and API

**Files:**
- Create: `src/agents/adr_recorder/agent.py`
- Create: `src/api/routes/adrs.py`
- Test: `tests/agents/adr_recorder/test_agent.py`

### Implementation Overview

```python
# src/agents/adr_recorder/agent.py
"""ADRRecorder agent."""
from __future__ import annotations

from typing import Any

from src.core.agents import BaseAgent, AgentContext, TaskComplexity

from .capture import DecisionCaptureAgent, DecisionSource
from .writer import ADRWriter
from .indexer import ADRIndexer


class ADRRecorderAgent(BaseAgent):
    """Agent that records Architecture Decision Records."""

    name = "adr_recorder"
    description = "Captures and records architecture decisions from conversations"
    complexity = TaskComplexity.MODERATE

    def __init__(self, llm_client: Any, qdrant_client: Any = None, embedding_client: Any = None):
        super().__init__(llm_client)
        self.capture = DecisionCaptureAgent(llm_client)
        self.writer = ADRWriter(llm_client)
        self.indexer = ADRIndexer(qdrant_client, embedding_client) if qdrant_client else None

    async def execute(
        self,
        context: AgentContext,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Process input and generate ADRs."""
        action = kwargs.get("action", "capture")
        messages = kwargs.get("messages", [])
        source = kwargs.get("source", "manual")

        if action == "capture":
            # Capture decisions from conversation
            decisions = await self.capture.analyze_conversation(
                messages,
                DecisionSource(source),
            )

            # Generate ADRs for each decision
            adrs = []
            for i, decision in enumerate(decisions):
                adr = await self.writer.generate_adr(
                    decision,
                    adr_number=kwargs.get("next_adr_number", 1) + i,
                )
                adrs.append(adr)

                # Index if available
                if self.indexer:
                    await self.indexer.index_adr(adr)

            return {
                "decisions_found": len(decisions),
                "adrs_generated": len(adrs),
                "adrs": [
                    {
                        "number": adr.number,
                        "title": adr.title,
                        "status": adr.status,
                        "markdown": adr.to_markdown(),
                    }
                    for adr in adrs
                ],
            }

        elif action == "search":
            # Search existing ADRs
            query = kwargs.get("query", "")
            if not self.indexer:
                return {"error": "Indexer not configured"}

            results = await self.indexer.search(query)
            return {
                "query": query,
                "results": [
                    {
                        "number": r.adr_number,
                        "title": r.title,
                        "score": r.score,
                        "preview": r.context_preview,
                    }
                    for r in results
                ],
            }

        return {"error": f"Unknown action: {action}"}
```

---

## Summary

Phase 10 (ADRRecorder Agent) consists of 4 tasks:

1. **Decision Capture Agent** - Extract decision points from conversations
2. **ADR Writer** - Generate structured ADRs with options and consequences
3. **ADR Indexer** - Semantic search using vector embeddings
4. **ADRRecorder Agent & API** - Orchestration and REST endpoints

**Estimated Implementation Time:** ~1 week

**Dependencies:** Phase 1 (Foundation)
