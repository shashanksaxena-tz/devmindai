"""Generates query optimization suggestions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .parser import ParsedQuery
from .analyzer import QueryPlan


@dataclass
class Optimization:
    """A suggested optimization."""
    category: str  # index, rewrite, schema
    description: str
    sql: Optional[str]  # New SQL or CREATE INDEX statement
    estimated_improvement: str  # e.g., "50-80% faster"
    risk: str  # low, medium, high
    priority: int  # 1 = highest


class OptimizationSuggester:
    """Suggests query optimizations."""

    def __init__(self, llm_client: Any):
        self.llm_client = llm_client

    async def suggest(
        self,
        query: ParsedQuery,
        plan: QueryPlan,
    ) -> list[Optimization]:
        """Generate optimization suggestions."""
        optimizations = []

        # Index suggestions based on plan issues
        for issue in plan.issues:
            if "Sequential scan" in issue:
                # issue format: "Sequential scan on {table}: ..."
                parts = issue.split(" on ")
                if len(parts) > 1:
                    table = parts[1].split(":")[0]
                    opts = await self._suggest_indexes(query, table)
                    optimizations.extend(opts)

        # Query rewrite suggestions
        rewrites = await self._suggest_rewrites(query)
        optimizations.extend(rewrites)

        # Sort by priority
        optimizations.sort(key=lambda o: o.priority)

        return optimizations

    async def _suggest_indexes(self, query: ParsedQuery, table: str) -> list[Optimization]:
        """Suggest indexes for a table."""
        suggestions = []

        # Index on WHERE columns
        if not query.where_conditions:
            return []

        for condition in query.where_conditions:
            prompt = f"""Suggest an index for this query condition:
Table: {table}
Condition: {condition}

Return only the CREATE INDEX statement.
"""
            response = await self.llm_client.generate(prompt=prompt)

            # Helper to extract just the response text if the client returns an object
            # (Though in our mock we return string directly, real clients might differ)
            if hasattr(response, "response"):
                response = response.response

            suggestions.append(Optimization(
                category="index",
                description=f"Add index on {table} for WHERE clause",
                sql=str(response).strip(),
                estimated_improvement="50-80% faster",
                risk="low",
                priority=1,
            ))

        return suggestions

    async def _suggest_rewrites(self, query: ParsedQuery) -> list[Optimization]:
        """Suggest query rewrites."""
        suggestions = []

        # N+1 pattern detection / subqueries
        if len(query.subqueries) > 0:
            prompt = f"""Rewrite this query to eliminate subqueries or optimize them:

{query.original}

Return only the optimized query SQL.
"""
            response = await self.llm_client.generate(prompt=prompt)

            if hasattr(response, "response"):
                response = response.response

            suggestions.append(Optimization(
                category="rewrite",
                description="Rewrite subquery optimization",
                sql=str(response).strip(),
                estimated_improvement="30-60% faster",
                risk="medium",
                priority=2,
            ))

        return suggestions
