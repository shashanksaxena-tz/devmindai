"""Pattern definitions for code migration."""

from enum import Enum

class MigrationType(Enum):
    """Types of migrations supported."""
    FRAMEWORK = "framework"
    LANGUAGE = "language"
    LIBRARY = "library"
    API_VERSION = "api_version"

# Common patterns
PATTERNS = {
    "react_class_to_hooks": {
        "pattern": r"class\s+\w+\s+extends\s+(React\.)?Component",
        "type": MigrationType.FRAMEWORK,
        "description": "Convert React Class Components to Functional Components with Hooks",
    },
    "vue2_to_vue3": {
        "pattern": r"new Vue\({",
        "type": MigrationType.FRAMEWORK,
        "description": "Convert Vue 2 instantiation to Vue 3 createApp",
    },
    "moment_to_datefns": {
        "pattern": r"import.*from\s+['\"]moment['\"]",
        "type": MigrationType.LIBRARY,
        "description": "Replace Moment.js with date-fns",
    },
    "js_to_ts": {
        "pattern": r"\.js$",
        "type": MigrationType.LANGUAGE,
        "description": "Rename .js files to .ts and add types",
    },
    "pytest_unittest_to_pytest": {
        "pattern": r"class\s+\w+\(unittest\.TestCase\):",
        "type": MigrationType.FRAMEWORK,
        "description": "Convert unittest.TestCase to pytest functions",
    },
}
