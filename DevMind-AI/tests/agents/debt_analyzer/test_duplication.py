# tests/agents/debt_analyzer/test_duplication.py
"""Tests for code duplication detection."""
import pytest
from src.agents.debt_analyzer.duplication import (
    DuplicationDetector,
    DuplicationReport,
    DuplicateBlock,
)


class TestDuplicationDetector:
    """Test DuplicationDetector."""

    @pytest.fixture
    def detector(self):
        return DuplicationDetector(min_lines=3, min_tokens=10)

    def test_detect_exact_duplicates(self, detector):
        """Detect exact duplicate code blocks."""
        detector.min_tokens = 1
        code = '''
def common_logic():
    print("start")
    x = 1
    y = 2
    return x + y
'''.strip()
        files = {
            "file1.py": code,
            "file2.py": code,
        }

        report = detector.detect(files)
        assert len(report.duplicate_blocks) >= 1
        assert len(report.duplicate_blocks[0].occurrences) == 2

    def test_ignore_whitespace_variations(self, detector):
        """Ignore whitespace differences."""
        detector.min_tokens = 1
        code1 = '''
def func():
    x=1
    y=2
'''.strip()
        code2 = '''
def func():
    x = 1
    y = 2
'''.strip()
        files = {
            "f1.py": code1,
            "f2.py": code2,
        }

        report = detector.detect(files)
        # Should match despite whitespace
        assert len(report.duplicate_blocks) == 1

    def test_ignore_small_blocks(self, detector):
        """Ignore blocks smaller than threshold."""
        code = "x = 1\ny = 2"
        files = {
            "f1.py": code,
            "f2.py": code,
        }

        # Detector configured with min_lines=3
        report = detector.detect(files)
        assert len(report.duplicate_blocks) == 0

    def test_calculate_duplication_percentage(self, detector):
        """Calculate overall duplication percentage."""
        # 4 lines total, 2 duplicated in each file
        # Total lines = 4 + 4 = 8
        # Duplicated lines = 3 (block size) * (2 occurrences - 1) = 3?
        # Wait, the formula in implementation is:
        # duplicated_lines = sum(d.total_duplicated_lines for d in duplicates)
        # total_duplicated_lines = self.lines * (len(self.occurrences) - 1)
        # If I have 2 files with identical 4 lines.
        # Block size 4. Occurrences 2.
        # Duplicated lines = 4 * (2 - 1) = 4.
        # Total lines = 8.
        # Percentage = 4/8 = 50%.

        code = '''
line1
line2
line3
line4
'''
        files = {
            "f1.py": code.strip(),
            "f2.py": code.strip(),
        }

        # min_lines=3.
        # Block is 4 lines.
        detector = DuplicationDetector(min_lines=4, min_tokens=0)
        report = detector.detect(files)

        assert report.duplication_percentage == 50.0
