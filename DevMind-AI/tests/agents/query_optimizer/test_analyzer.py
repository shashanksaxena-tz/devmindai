"""Tests for ExplainAnalyzer."""
import pytest
from src.agents.query_optimizer.analyzer import ExplainAnalyzer, QueryPlan

def test_analyze_seq_scan_large_table():
    analyzer = ExplainAnalyzer()

    # Mock JSON output from Postgres EXPLAIN (FORMAT JSON)
    explain_output = {
        "Plan": {
            "Node Type": "Seq Scan",
            "Relation Name": "users",
            "Plan Rows": 5000,
            "Total Cost": 100.0,
            "Actual Rows": 5000,
            "Actual Total Time": 50.0
        }
    }

    plan = analyzer.analyze(explain_output)

    assert plan.root.operation == "Seq Scan"
    assert plan.root.table == "users"
    assert plan.rows_affected == 5000
    assert len(plan.issues) == 1
    assert "Sequential scan on users" in plan.issues[0]

def test_analyze_seq_scan_small_table():
    analyzer = ExplainAnalyzer()

    explain_output = {
        "Plan": {
            "Node Type": "Seq Scan",
            "Relation Name": "roles",
            "Plan Rows": 10,
            "Total Cost": 1.0,
            "Actual Rows": 10,
            "Actual Total Time": 0.1
        }
    }

    plan = analyzer.analyze(explain_output)

    assert plan.root.operation == "Seq Scan"
    assert len(plan.issues) == 0  # Should not flag small seq scan

def test_analyze_nested_plan():
    analyzer = ExplainAnalyzer()

    explain_output = {
        "Plan": {
            "Node Type": "Nested Loop",
            "Total Cost": 200.0,
            "Actual Total Time": 100.0,
            "Plans": [
                {
                    "Node Type": "Seq Scan",
                    "Relation Name": "orders",
                    "Plan Rows": 2000,
                    "Total Cost": 50.0,
                    "Actual Rows": 2000
                },
                {
                    "Node Type": "Index Scan",
                    "Relation Name": "users",
                    "Plan Rows": 1,
                    "Total Cost": 0.5,
                    "Actual Rows": 1
                }
            ]
        }
    }

    plan = analyzer.analyze(explain_output)

    assert plan.root.operation == "Nested Loop"
    assert len(plan.root.children) == 2
    # Expect 2 issues: Nested Loop itself, and Seq Scan on orders (rows=2000 > 1000)
    assert len(plan.issues) >= 2
    assert any("Nested Loop" in issue for issue in plan.issues)
    assert any("Sequential scan on orders" in issue for issue in plan.issues)
