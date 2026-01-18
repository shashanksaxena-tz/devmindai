# DevMind AI Phase 9: QueryOptimizer Agent Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an intelligent database query optimizer that analyzes slow queries, suggests optimizations, recommends indexes, and predicts performance improvements.

**Architecture:** Query analysis pipeline with Parser (SQL extraction), Analyzer (EXPLAIN parsing), Optimizer (suggestion generation), and Validator (improvement prediction). Uses Claude for complex query optimization.

**Tech Stack:** FastAPI, sqlparse, PostgreSQL EXPLAIN, Claude API

**Prerequisites:** Phase 1 (Foundation) completed

---

## Task 1: SQL Query Parser and Extractor

**Files:**
- Create: `src/agents/query_optimizer/parser.py`
- Test: `tests/agents/query_optimizer/test_parser.py`

### Implementation Overview

```python
# src/agents/query_optimizer/parser.py
"""SQL query parsing and extraction."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class QueryType(Enum):
    """Types of SQL queries."""
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    OTHER = "other"


@dataclass
class ParsedQuery:
    """Parsed SQL query."""
    original: str
    query_type: QueryType
    tables: list[str]
    columns: list[str]
    where_conditions: list[str]
    joins: list[dict]
    order_by: list[str]
    group_by: list[str]
    subqueries: list[str]
    has_aggregation: bool = False
    has_window_function: bool = False


class QueryParser:
    """Parses SQL queries to extract components."""

    def parse(self, sql: str) -> ParsedQuery:
        """Parse a SQL query."""
        sql_lower = sql.lower().strip()

        # Determine query type
        query_type = QueryType.OTHER
        if sql_lower.startswith("select"):
            query_type = QueryType.SELECT
        elif sql_lower.startswith("insert"):
            query_type = QueryType.INSERT
        elif sql_lower.startswith("update"):
            query_type = QueryType.UPDATE
        elif sql_lower.startswith("delete"):
            query_type = QueryType.DELETE

        return ParsedQuery(
            original=sql,
            query_type=query_type,
            tables=self._extract_tables(sql),
            columns=self._extract_columns(sql),
            where_conditions=self._extract_where(sql),
            joins=self._extract_joins(sql),
            order_by=self._extract_order_by(sql),
            group_by=self._extract_group_by(sql),
            subqueries=self._extract_subqueries(sql),
            has_aggregation=self._has_aggregation(sql),
            has_window_function=self._has_window_function(sql),
        )

    def _extract_tables(self, sql: str) -> list[str]:
        """Extract table names from query."""
        tables = []
        # FROM clause
        from_match = re.search(r'\bfrom\s+([a-zA-Z_][a-zA-Z0-9_]*)', sql, re.I)
        if from_match:
            tables.append(from_match.group(1))
        # JOIN clauses
        join_matches = re.findall(r'\bjoin\s+([a-zA-Z_][a-zA-Z0-9_]*)', sql, re.I)
        tables.extend(join_matches)
        return tables

    def _extract_columns(self, sql: str) -> list[str]:
        """Extract column names from SELECT."""
        match = re.search(r'select\s+(.+?)\s+from', sql, re.I | re.S)
        if match:
            cols_str = match.group(1)
            if cols_str.strip() == "*":
                return ["*"]
            return [c.strip() for c in cols_str.split(",")]
        return []

    def _extract_where(self, sql: str) -> list[str]:
        """Extract WHERE conditions."""
        match = re.search(r'where\s+(.+?)(?:order|group|limit|$)', sql, re.I | re.S)
        if match:
            return [match.group(1).strip()]
        return []

    def _extract_joins(self, sql: str) -> list[dict]:
        """Extract JOIN clauses."""
        joins = []
        pattern = r'(left|right|inner|outer|cross)?\s*join\s+(\w+)\s+(?:as\s+)?(\w+)?\s*on\s+(.+?)(?=\s+(?:left|right|inner|join|where|order|group|$))'
        for match in re.finditer(pattern, sql, re.I):
            joins.append({
                "type": match.group(1) or "inner",
                "table": match.group(2),
                "alias": match.group(3),
                "condition": match.group(4),
            })
        return joins

    def _extract_order_by(self, sql: str) -> list[str]:
        """Extract ORDER BY columns."""
        match = re.search(r'order\s+by\s+(.+?)(?:limit|$)', sql, re.I)
        if match:
            return [c.strip() for c in match.group(1).split(",")]
        return []

    def _extract_group_by(self, sql: str) -> list[str]:
        """Extract GROUP BY columns."""
        match = re.search(r'group\s+by\s+(.+?)(?:having|order|limit|$)', sql, re.I)
        if match:
            return [c.strip() for c in match.group(1).split(",")]
        return []

    def _extract_subqueries(self, sql: str) -> list[str]:
        """Extract subqueries."""
        subqueries = []
        depth = 0
        start = -1
        for i, char in enumerate(sql):
            if char == "(":
                if depth == 0:
                    start = i
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0 and start != -1:
                    inner = sql[start + 1:i].strip()
                    if inner.lower().startswith("select"):
                        subqueries.append(inner)
                    start = -1
        return subqueries

    def _has_aggregation(self, sql: str) -> bool:
        """Check for aggregate functions."""
        return bool(re.search(r'\b(count|sum|avg|min|max)\s*\(', sql, re.I))

    def _has_window_function(self, sql: str) -> bool:
        """Check for window functions."""
        return bool(re.search(r'\bover\s*\(', sql, re.I))
```

---

## Task 2: EXPLAIN Plan Analyzer

**Files:**
- Create: `src/agents/query_optimizer/analyzer.py`
- Test: `tests/agents/query_optimizer/test_analyzer.py`

### Implementation Overview

```python
# src/agents/query_optimizer/analyzer.py
"""Analyzes query execution plans."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


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
    planning_time_ms: Optional[float]
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

        return QueryPlan(
            root=root,
            total_cost=root.cost,
            execution_time_ms=root.time_ms,
            rows_affected=root.actual_rows or root.estimated_rows,
            issues=issues,
        )

    def _parse_text_explain(self, text: str) -> dict:
        """Parse text EXPLAIN output to dict."""
        # Simplified parser
        return {"operation": "Unknown", "cost": 0}

    def _parse_node(self, data: dict) -> PlanNode:
        """Parse a plan node from JSON."""
        plan = data.get("Plan", data)
        children = []

        for child_data in plan.get("Plans", []):
            children.append(self._parse_node({"Plan": child_data}))

        return PlanNode(
            operation=plan.get("Node Type", "Unknown"),
            table=plan.get("Relation Name"),
            estimated_rows=plan.get("Plan Rows", 0),
            actual_rows=plan.get("Actual Rows"),
            cost=plan.get("Total Cost", 0),
            time_ms=plan.get("Actual Total Time"),
            children=children,
        )

    def _identify_issues(self, node: PlanNode) -> list[str]:
        """Identify performance issues in the plan."""
        issues = []

        if node.operation in self.SLOW_OPERATIONS:
            if node.operation == "Seq Scan" and (node.actual_rows or node.estimated_rows) > 1000:
                issues.append(f"Sequential scan on {node.table}: {self.SLOW_OPERATIONS[node.operation]}")

        for child in node.children:
            issues.extend(self._identify_issues(child))

        return issues
```

---

## Task 3: Optimization Suggester

**Files:**
- Create: `src/agents/query_optimizer/suggester.py`
- Test: `tests/agents/query_optimizer/test_suggester.py`

### Implementation Overview

```python
# src/agents/query_optimizer/suggester.py
"""Generates query optimization suggestions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

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
            if "Seq Scan" in issue:
                table = issue.split(" on ")[-1].split(":")[0]
                optimizations.extend(await self._suggest_indexes(query, table))

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
        for condition in query.where_conditions:
            prompt = f"""Suggest an index for this query condition:
Table: {table}
Condition: {condition}

Return the CREATE INDEX statement.
"""
            response = await self.llm_client.generate(prompt=prompt)

            suggestions.append(Optimization(
                category="index",
                description=f"Add index on {table} for WHERE clause",
                sql=response,
                estimated_improvement="50-80% faster",
                risk="low",
                priority=1,
            ))

        return suggestions

    async def _suggest_rewrites(self, query: ParsedQuery) -> list[Optimization]:
        """Suggest query rewrites."""
        suggestions = []

        # N+1 pattern detection
        if len(query.subqueries) > 0:
            prompt = f"""Rewrite this query to eliminate subqueries:

{query.original}

Return the optimized query.
"""
            response = await self.llm_client.generate(prompt=prompt)

            suggestions.append(Optimization(
                category="rewrite",
                description="Rewrite subquery as JOIN",
                sql=response,
                estimated_improvement="30-60% faster",
                risk="medium",
                priority=2,
            ))

        return suggestions
```

---

## Task 4: QueryOptimizer Agent and API

**Files:**
- Create: `src/agents/query_optimizer/agent.py`
- Create: `src/api/routes/queries.py`
- Test: `tests/agents/query_optimizer/test_agent.py`

### Implementation Overview

```python
# src/agents/query_optimizer/agent.py
"""QueryOptimizer agent."""
from __future__ import annotations

from typing import Any

from src.core.agents import BaseAgent, AgentContext, TaskComplexity

from .parser import QueryParser
from .analyzer import ExplainAnalyzer
from .suggester import OptimizationSuggester


class QueryOptimizerAgent(BaseAgent):
    """Agent that optimizes database queries."""

    name = "query_optimizer"
    description = "Analyzes and optimizes slow database queries"
    complexity = TaskComplexity.MODERATE

    def __init__(self, llm_client: Any):
        super().__init__(llm_client)
        self.parser = QueryParser()
        self.analyzer = ExplainAnalyzer()
        self.suggester = OptimizationSuggester(llm_client)

    async def execute(
        self,
        context: AgentContext,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Optimize a query."""
        sql = kwargs.get("sql", "")
        explain_output = kwargs.get("explain", None)

        # Parse query
        parsed = self.parser.parse(sql)

        # Analyze plan if provided
        plan = None
        issues = []
        if explain_output:
            plan = self.analyzer.analyze(explain_output)
            issues = plan.issues

        # Generate suggestions
        suggestions = await self.suggester.suggest(
            parsed,
            plan or type('Plan', (), {'issues': []})(),
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
```

---

## Summary

Phase 9 (QueryOptimizer Agent) consists of 4 tasks:

1. **SQL Query Parser** - Extract query components (tables, joins, conditions)
2. **EXPLAIN Analyzer** - Parse execution plans and identify issues
3. **Optimization Suggester** - Generate index and rewrite suggestions
4. **QueryOptimizer Agent & API** - Orchestration and REST endpoints

**Estimated Implementation Time:** ~1 week

**Dependencies:** Phase 1 (Foundation)
