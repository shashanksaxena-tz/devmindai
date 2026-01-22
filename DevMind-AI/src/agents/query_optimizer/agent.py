"""QueryOptimizer agent."""
from __future__ import annotations

from typing import Any

from src.agents.base import BaseAgent, AgentContext
from src.core.llm import TaskComplexity, LLMRouter

from .parser import QueryParser
from .analyzer import ExplainAnalyzer
from .suggester import OptimizationSuggester


class QueryOptimizerAgent(BaseAgent):
    """Agent that optimizes database queries."""

    name = "query_optimizer"
    description = "Analyzes and optimizes slow database queries"
    complexity = TaskComplexity.MODERATE

    def __init__(self, router: LLMRouter | None = None):
        super().__init__(router)
        self.parser = QueryParser()
        self.analyzer = ExplainAnalyzer()
        self.suggester = OptimizationSuggester(self.llm_client)

    async def execute(
        self,
        context: AgentContext,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Optimize a query."""
        sql = kwargs.get("sql", "")
        explain_output = kwargs.get("explain", None)

        if not sql:
            return {"error": "SQL query is required"}

        # Parse query
        parsed = self.parser.parse(sql)

        # Analyze plan if provided
        plan = None
        issues = []
        if explain_output:
            plan = self.analyzer.analyze(explain_output)
            issues = plan.issues
        else:
            # Create a dummy plan if no explain output provided
            from .analyzer import QueryPlan, PlanNode
            plan = QueryPlan(
                root=PlanNode("Unknown", None, 0, 0, 0.0, 0.0),
                total_cost=0.0,
                execution_time_ms=0.0,
                rows_affected=0
            )

        # Generate suggestions
        suggestions = await self.suggester.suggest(
            parsed,
            plan
        )

        return {
            "original_query": sql,
            "query_type": parsed.query_type.value,
            "tables": parsed.tables,
            "issues": issues,
            "suggestions": [
                {
                    "category": s.category,
                    "description": s.description,
                    "sql": s.sql,
                    "estimated_improvement": s.estimated_improvement,
                    "risk": s.risk,
                }
                for s in suggestions
            ],
        }
