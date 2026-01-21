import pytest
from src.agents.code_migrator.scanner import MigrationScanner, MigrationType, MigrationTarget

class TestMigrationScanner:

    @pytest.fixture
    def scanner(self):
        return MigrationScanner()

    def test_scan_react_class_component(self, scanner):
        files = {
            "src/components/Button.js": """
import React, { Component } from 'react';

class Button extends Component {
  render() {
    return <button>Click me</button>;
  }
}
export default Button;
"""
        }

        analysis = scanner.scan(
            files=files,
            migration_type="react_class_to_hooks",
            source_version="16.0",
            target_version="18.0"
        )

        assert analysis.migration_type == MigrationType.FRAMEWORK
        assert len(analysis.targets) == 1
        assert analysis.targets[0].file_path == "src/components/Button.js"
        assert "class Button extends Component" in analysis.targets[0].current_code

    def test_scan_moment_usage(self, scanner):
        files = {
            "src/utils/date.js": """
import moment from 'moment';
import { other } from 'other-lib';

const now = moment();
"""
        }

        analysis = scanner.scan(
            files=files,
            migration_type="moment_to_datefns",
            source_version="2.0",
            target_version="3.0"
        )

        assert analysis.migration_type == MigrationType.LIBRARY
        assert len(analysis.targets) == 1
        assert analysis.targets[0].file_path == "src/utils/date.js"
        assert "import moment from 'moment'" in analysis.targets[0].current_code

    def test_scan_file_extension(self, scanner):
        files = {
            "src/utils/helper.js": "const x = 1;",
            "src/utils/types.ts": "const y: number = 2;"
        }

        analysis = scanner.scan(
            files=files,
            migration_type="js_to_ts",
            source_version="ES6",
            target_version="TS5"
        )

        assert analysis.migration_type == MigrationType.LANGUAGE
        assert len(analysis.targets) == 1
        assert analysis.targets[0].file_path == "src/utils/helper.js"
        assert analysis.targets[0].current_code == "[WHOLE FILE]"

    def test_estimate_effort(self, scanner):
        targets = [
            MigrationTarget(
                file_path="a.js", line_start=1, line_end=10,
                pattern_type="test", current_code="", complexity="simple"
            ),
            MigrationTarget(
                file_path="b.js", line_start=1, line_end=10,
                pattern_type="test", current_code="", complexity="moderate"
            ),
            MigrationTarget(
                file_path="c.js", line_start=1, line_end=10,
                pattern_type="test", current_code="", complexity="complex"
            ),
        ]

        effort = scanner._estimate_effort(targets)
        assert effort == 0.25 + 1.0 + 3.0
