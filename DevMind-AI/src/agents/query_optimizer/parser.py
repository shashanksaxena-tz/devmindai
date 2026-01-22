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
