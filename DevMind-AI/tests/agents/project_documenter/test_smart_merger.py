"""Tests for SmartMerger."""

import pytest
from src.agents.project_documenter.smart_merger import SmartMerger, Section, SectionType


def test_smart_merger_preserves_custom_sections():
    """Test that custom sections are preserved during merge."""
    existing = """
# Module

<!-- AUTO-GENERATED: Purpose - DO NOT EDIT -->
## Purpose
Old purpose text
<!-- END AUTO-GENERATED -->

<!-- CUSTOM SECTION: My notes -->
## My Custom Notes
User-added content here
<!-- END CUSTOM SECTION -->
"""

    new_content = """
# Module

<!-- AUTO-GENERATED: Purpose - DO NOT EDIT -->
## Purpose
New updated purpose text
<!-- END AUTO-GENERATED -->

<!-- CUSTOM SECTION: My notes -->
## My Custom Notes
<!-- END CUSTOM SECTION -->
"""

    merger = SmartMerger()
    result = merger.merge(existing, new_content)

    assert "New updated purpose text" in result
    assert "User-added content here" in result
    assert "Old purpose text" not in result


def test_smart_merger_handles_new_sections():
    """Test that new auto-generated sections are added."""
    existing = """
# Module

<!-- AUTO-GENERATED: Purpose - DO NOT EDIT -->
## Purpose
Old purpose
<!-- END AUTO-GENERATED -->
"""

    new_content = """
# Module

<!-- AUTO-GENERATED: Purpose - DO NOT EDIT -->
## Purpose
Updated purpose
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: New Section - DO NOT EDIT -->
## New Section
This is new
<!-- END AUTO-GENERATED -->
"""

    merger = SmartMerger()
    result = merger.merge(existing, new_content)

    assert "Updated purpose" in result
    assert "This is new" in result


def test_smart_merger_no_markers_generates_fresh():
    """Test that files without markers are generated fresh."""
    existing = """
# Manual File
No markers here
"""

    new_content = """
<!-- AUTO-GENERATED: Purpose - DO NOT EDIT -->
## Purpose
Fresh content with markers
<!-- END AUTO-GENERATED -->
"""

    merger = SmartMerger()
    result = merger.merge(existing, new_content)

    assert "Fresh content with markers" in result


def test_smart_merger_parses_sections():
    """Test section parsing."""
    content = """
# Header

<!-- AUTO-GENERATED: Purpose - DO NOT EDIT -->
## Purpose
Purpose content
<!-- END AUTO-GENERATED -->

Some text

<!-- CUSTOM SECTION: Notes -->
## Notes
User notes
<!-- END CUSTOM SECTION -->
"""

    merger = SmartMerger()
    sections = merger._parse_sections(content)

    auto_sections = [s for s in sections if s.section_type == SectionType.AUTO_GENERATED]
    custom_sections = [s for s in sections if s.section_type == SectionType.CUSTOM]
    
    assert len(auto_sections) == 1
    assert auto_sections[0].name == "Purpose"
    assert "Purpose content" in auto_sections[0].content
    
    assert len(custom_sections) == 1
    assert custom_sections[0].name == "Notes"
    assert "User notes" in custom_sections[0].content


def test_smart_merger_has_markers():
    """Test marker detection."""
    merger = SmartMerger()
    
    content_with_markers = """
<!-- AUTO-GENERATED: Test - DO NOT EDIT -->
content
<!-- END AUTO-GENERATED -->
"""
    
    content_without_markers = """
# Just a regular markdown file
No special markers here
"""
    
    assert merger.has_markers(content_with_markers) is True
    assert merger.has_markers(content_without_markers) is False


def test_smart_merger_extract_custom_sections():
    """Test extracting custom sections."""
    content = """
<!-- CUSTOM SECTION: Team Guidelines -->
## Team Guidelines
Use type hints
Write tests
<!-- END CUSTOM SECTION -->

<!-- CUSTOM SECTION: Notes -->
## Notes
Additional notes here
<!-- END CUSTOM SECTION -->
"""

    merger = SmartMerger()
    custom = merger.extract_custom_sections(content)

    assert "Team Guidelines" in custom
    assert "Use type hints" in custom["Team Guidelines"]
    assert "Notes" in custom
    assert "Additional notes here" in custom["Notes"]


def test_smart_merger_multiple_auto_sections():
    """Test merging with multiple auto-generated sections."""
    existing = """
<!-- AUTO-GENERATED: Purpose - DO NOT EDIT -->
## Purpose
Old purpose
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Files - DO NOT EDIT -->
## Files
- old_file.py
<!-- END AUTO-GENERATED -->

<!-- CUSTOM SECTION: Notes -->
## Notes
My notes
<!-- END CUSTOM SECTION -->
"""

    new_content = """
<!-- AUTO-GENERATED: Purpose - DO NOT EDIT -->
## Purpose
New purpose
<!-- END AUTO-GENERATED -->

<!-- AUTO-GENERATED: Files - DO NOT EDIT -->
## Files
- new_file.py
<!-- END AUTO-GENERATED -->

<!-- CUSTOM SECTION: Notes -->
## Notes
<!-- END CUSTOM SECTION -->
"""

    merger = SmartMerger()
    result = merger.merge(existing, new_content)

    # Auto sections should be updated
    assert "New purpose" in result
    assert "new_file.py" in result
    assert "Old purpose" not in result
    
    # Custom section should be preserved
    assert "My notes" in result


def test_section_dataclass():
    """Test Section dataclass."""
    section = Section(
        section_type=SectionType.AUTO_GENERATED,
        name="Purpose",
        content="This is the purpose",
        raw="<!-- AUTO-GENERATED: Purpose -->...",
    )
    
    assert section.section_type == SectionType.AUTO_GENERATED
    assert section.name == "Purpose"
    assert section.content == "This is the purpose"


def test_section_type_enum():
    """Test SectionType enum values."""
    assert SectionType.AUTO_GENERATED.value == "AUTO-GENERATED"
    assert SectionType.CUSTOM.value == "CUSTOM"
    assert SectionType.UNTAGGED.value == "UNTAGGED"
