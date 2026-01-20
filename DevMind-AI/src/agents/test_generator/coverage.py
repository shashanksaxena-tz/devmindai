"""Coverage analysis for identifying test gaps."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from .analyzer import FunctionInfo


class GapType(Enum):
    """Types of coverage gaps."""
    UNTESTED = "untested"
    LOW_LINE_COVERAGE = "low_line_coverage"
    LOW_BRANCH_COVERAGE = "low_branch_coverage"
    MISSING_EDGE_CASE = "missing_edge_case"
    MISSING_ERROR_CASE = "missing_error_case"


@dataclass
class CoverageGap:
    """Represents a gap in test coverage."""
    function_name: str
    file_path: str
    gap_type: GapType
    description: str
    priority: int = 1  # 1 = highest
    suggested_tests: list[str] = None

    def __post_init__(self):
        if self.suggested_tests is None:
            self.suggested_tests = []


class CoverageAnalyzer:
    """Analyzes test coverage to identify gaps."""

    # Edge case patterns by type
    EDGE_CASE_PATTERNS = {
        "int": ["zero", "negative", "max_int", "min_int"],
        "float": ["zero", "negative", "infinity", "nan", "very_small"],
        "str": ["empty_string", "whitespace", "unicode", "very_long"],
        "list": ["empty_list", "single_element", "large_list", "nested"],
        "dict": ["empty_dict", "missing_key", "nested_dict"],
        "Optional": ["none_value", "some_value"],
        "bool": ["true", "false"],
    }

    def find_gaps(
        self,
        source_functions: list[FunctionInfo],
        test_coverage: dict[str, bool],
    ) -> list[CoverageGap]:
        """Find functions that lack test coverage."""
        gaps = []

        for func in source_functions:
            coverage_key = f"{func.file}::{func.name}"

            if not test_coverage.get(coverage_key, False):
                gaps.append(CoverageGap(
                    function_name=func.name,
                    file_path=func.file,
                    gap_type=GapType.UNTESTED,
                    description=f"Function '{func.name}' has no tests",
                    priority=1 if not func.is_private else 3,
                ))

        return gaps

    def analyze_branch_coverage(
        self,
        coverage_data: dict[str, dict[str, Any]],
        threshold: float = 0.7,
    ) -> list[CoverageGap]:
        """Find functions with low branch coverage."""
        gaps = []

        for func_key, data in coverage_data.items():
            branch_coverage = data.get("branch_coverage", 1.0)

            if branch_coverage < threshold:
                file_path, func_name = func_key.split("::")
                gaps.append(CoverageGap(
                    function_name=func_name,
                    file_path=file_path,
                    gap_type=GapType.LOW_BRANCH_COVERAGE,
                    description=(
                        f"Function '{func_name}' has {branch_coverage:.0%} "
                        f"branch coverage (threshold: {threshold:.0%})"
                    ),
                    priority=2,
                ))

        return gaps

    def suggest_edge_cases(
        self,
        func_info: FunctionInfo,
        existing_tests: list[dict[str, Any]],
    ) -> list[str]:
        """Suggest edge cases not covered by existing tests."""
        suggestions = []
        covered_patterns = set()

        # Analyze existing test inputs
        for test in existing_tests:
            inputs = test.get("inputs", [])
            for inp in inputs:
                if inp == 0:
                    covered_patterns.add("zero")
                elif isinstance(inp, (int, float)) and inp < 0:
                    covered_patterns.add("negative")
                elif inp == "":
                    covered_patterns.add("empty_string")
                elif inp is None:
                    covered_patterns.add("none_value")

        # Suggest missing edge cases based on parameter types
        for param in func_info.parameters:
            param_dict = param if isinstance(param, dict) else {
                "name": param.name,
                "type": getattr(param, 'type_hint', None),
            }

            param_type = param_dict.get("type", "")
            param_name = param_dict.get("name", "")

            for base_type, cases in self.EDGE_CASE_PATTERNS.items():
                if base_type.lower() in str(param_type).lower():
                    for case in cases:
                        if case not in covered_patterns:
                            suggestions.append(
                                f"Test {param_name} with {case} "
                                f"(boundary/edge case for {base_type})"
                            )

        # Add common edge cases
        if "zero" not in covered_patterns:
            suggestions.append("Test with zero value (boundary condition)")
        if "negative" not in covered_patterns:
            suggestions.append("Test with negative value (boundary condition)")
        if "large" not in covered_patterns:
            suggestions.append("Test with large value (stress/boundary test)")

        return suggestions

    def parse_coverage_xml(self, xml_content: str) -> dict[str, dict[str, Any]]:
        """Parse coverage.py XML output."""
        result = {}

        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError:
            return result

        for package in root.findall(".//package"):
            for cls in package.findall(".//class"):
                filename = cls.get("filename", "")
                line_rate = float(cls.get("line-rate", 0))

                result[filename] = {
                    "line_rate": line_rate,
                    "methods": {},
                }

                for method in cls.findall(".//method"):
                    method_name = method.get("name", "")
                    method_rate = float(method.get("line-rate", 0))
                    result[filename]["methods"][method_name] = {
                        "line_rate": method_rate,
                    }

        return result

    def identify_error_paths(
        self,
        func_info: FunctionInfo,
        existing_tests: list[dict[str, Any]],
    ) -> list[CoverageGap]:
        """Identify error handling paths not covered by tests."""
        gaps = []

        # Check for exception testing
        has_error_test = any(
            "error" in t.get("name", "").lower() or
            "exception" in t.get("name", "").lower() or
            "raise" in t.get("name", "").lower() or
            "invalid" in t.get("name", "").lower()
            for t in existing_tests
        )

        if not has_error_test and func_info.complexity > 1:
            gaps.append(CoverageGap(
                function_name=func_info.name,
                file_path=func_info.file,
                gap_type=GapType.MISSING_ERROR_CASE,
                description=f"No error case tests for '{func_info.name}'",
                priority=2,
                suggested_tests=[
                    "Test with invalid input types",
                    "Test with values that trigger exceptions",
                    "Test error handling and recovery",
                ],
            ))

        return gaps
