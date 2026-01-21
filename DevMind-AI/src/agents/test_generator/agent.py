"""TestGenerator agent orchestrating test generation pipeline."""
from __future__ import annotations

from typing import Any, Optional

from src.agents.base import BaseAgent, AgentContext, AgentResult, TaskComplexity

from .analyzer import CodeAnalyzer, ModuleAnalysis
from .coverage import CoverageAnalyzer
from .strategist import TestStrategist, TestStrategy
from .generator import TestGenerator, GeneratedTest, TestFramework
from .validator import TestValidator


class TestGeneratorAgent(BaseAgent):
    """Agent that generates comprehensive test suites."""

    name = "test_generator"
    description = "Generates unit tests, integration tests, and edge cases"
    complexity = TaskComplexity.MODERATE

    def __init__(self, llm_client: Any):
        """Initialize with LLM client."""
        super().__init__(llm_client)
        self.analyzer = CodeAnalyzer()
        self.coverage_analyzer = CoverageAnalyzer()
        self.strategist = TestStrategist(llm_client)
        self.generator = TestGenerator(llm_client)
        self.validator = TestValidator()

    async def execute(
        self,
        context: AgentContext,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate tests for code.

        Args:
            context: Agent execution context
            code: Source code to generate tests for
            file_path: Path to the source file
            framework: Test framework to use (default: pytest)
            coverage_data: Optional existing coverage data

        Returns:
            Dict with generated tests and metadata
        """
        code = kwargs.get("code", "")
        file_path = kwargs.get("file_path", "unknown.py")
        framework_str = kwargs.get("framework", "pytest")
        coverage_data = kwargs.get("coverage_data")

        # Detect language from file extension
        language = self._detect_language(file_path)

        # Map framework string to enum
        try:
            framework = TestFramework(framework_str)
        except ValueError:
            framework = TestFramework.PYTEST

        # Analyze the code
        analysis = self.analyzer.analyze(code, language, file_path)

        # Find coverage gaps if coverage data provided
        gaps = []
        if coverage_data:
            gaps = self.coverage_analyzer.find_gaps(
                analysis.functions,
                coverage_data,
            )

        # Plan test strategy
        strategy = await self.strategist.plan_tests(
            analysis.functions,
            analysis.classes,
        )

        # Generate tests
        all_tests = []

        for func in analysis.functions:
            func_tests = await self.generator.generate_tests(
                func,
                framework=framework,
            )
            all_tests.extend(func_tests)

        for cls in analysis.classes:
            class_tests = await self.generator.generate_class_tests(
                cls,
                framework=framework,
            )
            all_tests.extend(class_tests)

        # Validate and filter
        valid_tests = self._filter_valid_tests(all_tests, language)

        # Prepare imports
        module_name = file_path.replace("/", ".").replace(".py", "")
        if module_name.startswith("src."):
            module_name = module_name[4:]  # Remove src. prefix if commonly used in imports relative to root

        # Actually, keep it simple. Assuming imports are relative to pythonpath.
        # But let's generate the import string for functions and classes.
        func_names = [f.name for f in analysis.functions]
        class_names = [c.name for c in analysis.classes]
        all_names = func_names + class_names

        imports_to_add = []
        if all_names:
             # This assumes file_path is relative to project root, e.g. "src/utils/math.py"
             # Convert to module: "src.utils.math"
             mod = file_path.replace("/", ".").replace(".py", "")
             imports_to_add.append(f"from {mod} import {', '.join(all_names)}")

        # Format as test file
        test_file_content = self.generator.format_test_file(
            valid_tests,
            source_module=file_path,
            framework=framework,
            imports_to_add=imports_to_add,
        )

        return {
            "tests": [
                {
                    "name": t.name,
                    "code": t.code,
                    "description": t.description,
                }
                for t in valid_tests
            ],
            "test_file_content": test_file_content,
            "test_file_path": self._generate_test_path(file_path),
            "functions_analyzed": len(analysis.functions),
            "classes_analyzed": len(analysis.classes),
            "tests_generated": len(valid_tests),
            "coverage_gaps": [
                {"function": g.function_name, "type": g.gap_type.value}
                for g in gaps
            ],
        }

    async def generate_for_function(
        self,
        context: AgentContext,
        function_code: str,
        function_name: str,
        framework: str = "pytest",
    ) -> dict[str, Any]:
        """Generate tests for a single function."""
        # Parse the function
        analysis = self.analyzer.analyze(
            function_code,
            language="python",
            file_path="inline.py",
        )

        if not analysis.functions:
            return {"error": "Could not parse function", "tests": []}

        func = analysis.functions[0]

        # Generate tests
        try:
            fw = TestFramework(framework)
        except ValueError:
            fw = TestFramework.PYTEST

        tests = await self.generator.generate_tests(func, framework=fw)
        valid_tests = self._filter_valid_tests(tests)

        return {
            "tests": [
                {"name": t.name, "code": t.code, "description": t.description}
                for t in valid_tests
            ],
            "function_name": function_name,
        }

    def _filter_valid_tests(
        self,
        tests: list[GeneratedTest],
        language: str = "python",
    ) -> list[GeneratedTest]:
        """Filter out invalid tests."""
        valid = []
        for test in tests:
            validation = self.validator.validate_all(test, language)
            if validation.is_valid:
                valid.append(test)
        return valid

    def _detect_language(self, file_path: str) -> str:
        """Detect language from file extension."""
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".jsx": "javascript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
        }
        for ext, lang in ext_map.items():
            if file_path.endswith(ext):
                return lang
        return "python"

    def _generate_test_path(self, source_path: str) -> str:
        """Generate test file path from source path."""
        # src/services/payment.py -> tests/services/test_payment.py
        parts = source_path.split("/")

        if parts[0] == "src":
            parts[0] = "tests"
        elif not parts[0].startswith("test"):
            parts.insert(0, "tests")

        filename = parts[-1]
        if not filename.startswith("test_"):
            name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "py")
            parts[-1] = f"test_{name}.{ext}"

        return "/".join(parts)
