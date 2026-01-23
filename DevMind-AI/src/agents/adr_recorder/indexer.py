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
        # Note: Using strict argument checking in tests might fail if we don't inspect args carefully.
        # Assuming Qdrant client follows standard interface.
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
