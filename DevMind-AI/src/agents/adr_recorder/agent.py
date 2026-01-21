# src/agents/adr_recorder/agent.py
"""ADRRecorder agent."""
from __future__ import annotations

from typing import Any

from src.agents.base import BaseAgent, AgentContext, TaskComplexity
# Note: BaseAgent is assumed to exist in src.agents.base, adhering to the framework.

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
                DecisionSource(source) if hasattr(DecisionSource, source.upper()) else DecisionSource.MANUAL,
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
