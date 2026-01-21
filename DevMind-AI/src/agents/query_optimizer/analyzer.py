"""Analyzes query execution plans."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class PlanNode:
    """A node in the execution plan."""
    operation: str  # Seq Scan, Index Scan, Hash Join, etc.
    table: Optional[str]
    estimated_rows: int
    actual_rows: Optional[int]
    cost: float
    time_ms: Optional[float]
    children: list["PlanNode"] = field(default_factory=list)


@dataclass
class QueryPlan:
    """Parsed query execution plan."""
    root: PlanNode
    total_cost: float
    execution_time_ms: Optional[float]
    rows_affected: int
    planning_time_ms: Optional[float] = None
    issues: list[str] = field(default_factory=list)


class ExplainAnalyzer:
    """Analyzes PostgreSQL EXPLAIN output."""

    # Problematic operations
    SLOW_OPERATIONS = {
        "Seq Scan": "Consider adding an index",
        "Nested Loop": "May be slow for large datasets",
        "Sort": "Consider adding index on ORDER BY columns",
    }

    def analyze(self, explain_output: str | dict) -> QueryPlan:
        """Analyze EXPLAIN output."""
        if isinstance(explain_output, str):
            plan_data = self._parse_text_explain(explain_output)
        else:
            plan_data = explain_output

        root = self._parse_node(plan_data)
        issues = self._identify_issues(root)

        # Helper to get rows affected from root (actual if avail, else estimate)
        rows = root.actual_rows if root.actual_rows is not None else root.estimated_rows

        return QueryPlan(
            root=root,
            total_cost=root.cost,
            execution_time_ms=root.time_ms,
            rows_affected=rows,
            issues=issues,
        )

    def _parse_text_explain(self, text: str) -> dict:
        """Parse text EXPLAIN output to dict."""
        # Simplified placeholder parser for text output.
        # In a real scenario, we might want a more robust text parser or rely on JSON.
        return {"operation": "Unknown", "cost": 0, "Plan": {"Node Type": "Unknown"}}

    def _parse_node(self, data: dict) -> PlanNode:
        """Parse a plan node from JSON."""
        # Postgres EXPLAIN (FORMAT JSON) wraps the plan in a list, then a "Plan" key sometimes
        # Depending on input structure, we handle "Plan" key.

        plan = data.get("Plan", data)
        children = []

        for child_data in plan.get("Plans", []):
            children.append(self._parse_node(child_data))

        return PlanNode(
            operation=plan.get("Node Type", "Unknown"),
            table=plan.get("Relation Name"),
            estimated_rows=plan.get("Plan Rows", 0),
            actual_rows=plan.get("Actual Rows"),
            cost=plan.get("Total Cost", 0.0),
            time_ms=plan.get("Actual Total Time"),
            children=children,
        )

    def _identify_issues(self, node: PlanNode) -> list[str]:
        """Identify performance issues in the plan."""
        issues = []

        if node.operation in self.SLOW_OPERATIONS:
            # Heuristic: Seq Scan is only bad if rows > threshold
            if node.operation == "Seq Scan":
                rows = node.actual_rows if node.actual_rows is not None else node.estimated_rows
                if rows > 1000:
                    issues.append(f"Sequential scan on {node.table}: {self.SLOW_OPERATIONS[node.operation]}")
            else:
                # For others, just flagging them for now
                issues.append(f"{node.operation}: {self.SLOW_OPERATIONS[node.operation]}")

        for child in node.children:
            issues.extend(self._identify_issues(child))

        return issues
