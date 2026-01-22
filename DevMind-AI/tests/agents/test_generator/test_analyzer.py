"""Tests for code analyzer and coverage detection."""
import pytest
from src.agents.test_generator.analyzer import (
    CodeAnalyzer,
    FunctionInfo,
    ClassInfo,
    ModuleAnalysis,
)
from src.agents.test_generator.coverage import (
    CoverageAnalyzer,
    CoverageGap,
    GapType,
)


class TestCodeAnalyzer:
    """Test CodeAnalyzer functionality."""

    @pytest.fixture
    def analyzer(self):
        """Create CodeAnalyzer instance."""
        return CodeAnalyzer()

    def test_extract_functions(self, analyzer):
        """Extract function definitions from Python code."""
        code = '''
def calculate_total(items: list[Item]) -> float:
    """Calculate total price."""
    return sum(item.price for item in items)

def apply_discount(total: float, discount: float) -> float:
    """Apply discount to total."""
    if discount < 0 or discount > 1:
        raise ValueError("Invalid discount")
    return total * (1 - discount)

async def fetch_prices(item_ids: list[int]) -> list[float]:
    """Fetch prices from API."""
    return await api.get_prices(item_ids)
'''
        result = analyzer.analyze(code, language="python")

        assert len(result.functions) == 3
        assert result.functions[0].name == "calculate_total"
        assert result.functions[0].is_async is False
        assert result.functions[1].name == "apply_discount"
        assert result.functions[2].name == "fetch_prices"
        assert result.functions[2].is_async is True

    def test_extract_classes(self, analyzer):
        """Extract class definitions with methods."""
        code = '''
class PaymentProcessor:
    """Process payments."""

    def __init__(self, gateway: Gateway):
        self.gateway = gateway

    def process(self, amount: float) -> Receipt:
        """Process a payment."""
        return self.gateway.charge(amount)

    async def refund(self, receipt_id: str) -> bool:
        """Refund a payment."""
        return await self.gateway.refund(receipt_id)
'''
        result = analyzer.analyze(code, language="python")

        assert len(result.classes) == 1
        cls = result.classes[0]
        assert cls.name == "PaymentProcessor"
        assert len(cls.methods) == 3  # __init__, process, refund
        assert cls.methods[1].name == "process"

    def test_extract_parameters(self, analyzer):
        """Extract function parameters with types."""
        code = '''
def create_user(
    email: str,
    name: str,
    age: int = 0,
    roles: list[str] | None = None,
) -> User:
    pass
'''
        result = analyzer.analyze(code, language="python")

        func = result.functions[0]
        assert len(func.parameters) == 4
        assert func.parameters[0].name == "email"
        assert func.parameters[0].type_hint == "str"
        assert func.parameters[2].name == "age"
        assert func.parameters[2].default == "0"
        assert func.return_type == "User"

    def test_detect_branches(self, analyzer):
        """Detect conditional branches for coverage."""
        code = '''
def categorize(value: int) -> str:
    if value < 0:
        return "negative"
    elif value == 0:
        return "zero"
    elif value < 100:
        return "small"
    else:
        return "large"
'''
        result = analyzer.analyze(code, language="python")

        func = result.functions[0]
        assert func.branch_count == 4
        assert func.complexity >= 4

    def test_analyze_javascript(self, analyzer):
        """Analyze JavaScript/TypeScript code."""
        code = '''
export function validateEmail(email: string): boolean {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

export async function sendEmail(to: string, subject: string): Promise<void> {
    await mailer.send({ to, subject });
}
'''
        result = analyzer.analyze(code, language="typescript")

        assert len(result.functions) == 2
        assert result.functions[0].name == "validateEmail"
        assert result.functions[1].is_async is True


class TestCoverageAnalyzer:
    """Test CoverageAnalyzer functionality."""

    @pytest.fixture
    def coverage_analyzer(self):
        """Create CoverageAnalyzer instance."""
        return CoverageAnalyzer()

    def test_identify_untested_functions(self, coverage_analyzer):
        """Find functions without any tests."""
        source_functions = [
            FunctionInfo(name="process_payment", file="payment.py", line=10),
            FunctionInfo(name="refund_payment", file="payment.py", line=30),
            FunctionInfo(name="validate_card", file="payment.py", line=50),
        ]
        test_coverage = {
            "payment.py::process_payment": True,
            "payment.py::validate_card": True,
        }

        gaps = coverage_analyzer.find_gaps(source_functions, test_coverage)

        assert len(gaps) == 1
        assert gaps[0].function_name == "refund_payment"
        assert gaps[0].gap_type == GapType.UNTESTED

    def test_identify_low_coverage(self, coverage_analyzer):
        """Find functions with low branch coverage."""
        coverage_data = {
            "payment.py::process_payment": {
                "line_coverage": 0.9,
                "branch_coverage": 0.3,
                "branches_covered": [1, 2],
                "branches_total": 6,
            },
        }

        gaps = coverage_analyzer.analyze_branch_coverage(coverage_data)

        assert len(gaps) >= 1
        assert gaps[0].gap_type == GapType.LOW_BRANCH_COVERAGE

    def test_identify_missing_edge_cases(self, coverage_analyzer):
        """Identify edge cases not covered by tests."""
        func_info = FunctionInfo(
            name="divide",
            parameters=[
                {"name": "a", "type": "float"},
                {"name": "b", "type": "float"},
            ],
            file="math_utils.py",
            line=5,
        )
        existing_tests = [
            {"name": "test_divide_positive", "inputs": [10, 2]},
            {"name": "test_divide_negative", "inputs": [-10, 2]},
        ]

        edge_cases = coverage_analyzer.suggest_edge_cases(func_info, existing_tests)

        assert any("zero" in ec.lower() for ec in edge_cases)  # Division by zero
        assert any("boundary" in ec.lower() or "large" in ec.lower() for ec in edge_cases)

    def test_parse_coverage_xml(self, coverage_analyzer):
        """Parse coverage.py XML output."""
        xml_content = '''<?xml version="1.0" ?>
<coverage version="7.0" timestamp="1234567890">
    <packages>
        <package name="src">
            <classes>
                <class name="payment.py" filename="src/payment.py" line-rate="0.85">
                    <methods>
                        <method name="process" line-rate="0.9"/>
                        <method name="refund" line-rate="0.5"/>
                    </methods>
                </class>
            </classes>
        </package>
    </packages>
</coverage>'''

        result = coverage_analyzer.parse_coverage_xml(xml_content)

        assert "src/payment.py" in result
        assert result["src/payment.py"]["line_rate"] == 0.85
