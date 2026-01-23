"""Tests for exploitability analyzer."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestExploitabilityAnalyzer:
    """Test suite for ExploitabilityAnalyzer."""

    @pytest.mark.asyncio
    async def test_analyze_import_usage(self):
        """Should detect if vulnerable function is imported."""
        from src.agents.vuln_scanner.analyzer.exploitability import ExploitabilityAnalyzer

        # Sample JavaScript code that imports and uses lodash.merge
        code_content = '''
import { merge } from 'lodash';

function processConfig(userInput) {
    const config = { defaults: true };
    return merge(config, userInput);  // Vulnerable!
}
'''

        analyzer = ExploitabilityAnalyzer()
        result = await analyzer.analyze_code_usage(
            code_content=code_content,
            package_name="lodash",
            vulnerable_functions=["merge", "mergeWith"],
            language="javascript",
        )

        assert result.is_imported is True
        assert result.is_used is True
        assert "merge" in result.used_functions

    @pytest.mark.asyncio
    async def test_detect_user_input_flow(self):
        """Should detect if user input reaches vulnerable function."""
        from src.agents.vuln_scanner.analyzer.exploitability import ExploitabilityAnalyzer

        code_content = '''
const _ = require('lodash');

app.post('/api/config', (req, res) => {
    const userConfig = req.body;
    const merged = _.merge({}, userConfig);  // User input reaches merge!
    res.json(merged);
});
'''

        analyzer = ExploitabilityAnalyzer()
        result = await analyzer.analyze_code_usage(
            code_content=code_content,
            package_name="lodash",
            vulnerable_functions=["merge"],
            language="javascript",
        )

        assert result.is_used is True
        assert result.user_input_reachable is True

    @pytest.mark.asyncio
    async def test_safe_usage_detection(self):
        """Should detect when vulnerable function is not used."""
        from src.agents.vuln_scanner.analyzer.exploitability import ExploitabilityAnalyzer

        code_content = '''
import { map, filter } from 'lodash';

function processItems(items) {
    return map(items, x => x * 2);
}
'''

        analyzer = ExploitabilityAnalyzer()
        result = await analyzer.analyze_code_usage(
            code_content=code_content,
            package_name="lodash",
            vulnerable_functions=["merge", "mergeWith"],
            language="javascript",
        )

        assert result.is_imported is True
        assert result.is_used is False


class TestExploitabilityResult:
    """Test suite for ExploitabilityResult model."""

    def test_result_model_creation(self):
        """Should create result with all fields."""
        from src.agents.vuln_scanner.analyzer.exploitability import ExploitabilityResult

        result = ExploitabilityResult(
            is_imported=True,
            is_used=True,
            user_input_reachable=True,
            used_functions=["merge"],
            usage_locations=[{"file": "src/config.js", "line": 42}],
            confidence=0.95,
            analysis_notes="Direct usage of merge with user input.",
        )

        assert result.is_exploitable is True
        assert result.confidence == 0.95

    def test_not_exploitable_when_not_used(self):
        """Should not be exploitable if function not used."""
        from src.agents.vuln_scanner.analyzer.exploitability import ExploitabilityResult

        result = ExploitabilityResult(
            is_imported=True,
            is_used=False,
            user_input_reachable=False,
            used_functions=[],
            confidence=0.9,
        )

        assert result.is_exploitable is False
