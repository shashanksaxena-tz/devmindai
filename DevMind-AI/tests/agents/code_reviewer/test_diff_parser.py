# tests/agents/code_reviewer/test_diff_parser.py
"""Tests for PR diff parsing functionality."""
import pytest
from src.agents.code_reviewer.diff_parser import (
    DiffParser,
    FileDiff,
    HunkChange,
    ChangeType,
    parse_unified_diff,
)


class TestDiffParser:
    """Test suite for DiffParser."""

    def test_parse_single_file_addition(self):
        """Parse diff with single file addition."""
        diff_text = '''diff --git a/src/utils/helper.py b/src/utils/helper.py
new file mode 100644
index 0000000..abc1234
--- /dev/null
+++ b/src/utils/helper.py
@@ -0,0 +1,10 @@
+def calculate_total(items):
+    """Calculate total price of items."""
+    total = 0
+    for item in items:
+        total += item.price
+    return total
'''
        parser = DiffParser()
        result = parser.parse(diff_text)

        assert len(result.files) == 1
        assert result.files[0].path == "src/utils/helper.py"
        assert result.files[0].change_type == ChangeType.ADDED
        assert result.files[0].additions == 6
        assert result.files[0].deletions == 0

    def test_parse_file_modification(self):
        """Parse diff with file modifications."""
        diff_text = '''diff --git a/src/api/users.py b/src/api/users.py
index abc1234..def5678 100644
--- a/src/api/users.py
+++ b/src/api/users.py
@@ -10,7 +10,9 @@ def get_user(user_id: int):
     """Get user by ID."""
-    user = db.query(f"SELECT * FROM users WHERE id = {user_id}")
+    query = "SELECT * FROM users WHERE id = %s"
+    user = db.query(query, [user_id])
+    if not user:
+        raise NotFoundError(f"User {user_id} not found")
     return user
'''
        parser = DiffParser()
        result = parser.parse(diff_text)

        assert len(result.files) == 1
        assert result.files[0].change_type == ChangeType.MODIFIED
        assert result.files[0].additions == 4
        assert result.files[0].deletions == 1

    def test_parse_file_deletion(self):
        """Parse diff with file deletion."""
        diff_text = '''diff --git a/old_file.py b/old_file.py
deleted file mode 100644
index abc1234..0000000
--- a/old_file.py
+++ /dev/null
@@ -1,5 +0,0 @@
-def deprecated_function():
-    pass
'''
        parser = DiffParser()
        result = parser.parse(diff_text)

        assert len(result.files) == 1
        assert result.files[0].change_type == ChangeType.DELETED

    def test_parse_multiple_files(self):
        """Parse diff with multiple files."""
        diff_text = '''diff --git a/file1.py b/file1.py
index abc..def 100644
--- a/file1.py
+++ b/file1.py
@@ -1,3 +1,4 @@
 def func1():
+    print("added")
     pass
diff --git a/file2.py b/file2.py
index ghi..jkl 100644
--- a/file2.py
+++ b/file2.py
@@ -1,2 +1,2 @@
-old_line
+new_line
'''
        parser = DiffParser()
        result = parser.parse(diff_text)

        assert len(result.files) == 2
        assert result.total_additions == 2
        assert result.total_deletions == 1

    def test_extract_line_numbers(self):
        """Extract correct line numbers from hunks."""
        diff_text = '''diff --git a/src/api.py b/src/api.py
index abc..def 100644
--- a/src/api.py
+++ b/src/api.py
@@ -45,6 +45,8 @@ def endpoint():
     # existing code
+    new_line_1 = "test"
+    new_line_2 = "test2"
     more_existing()
'''
        parser = DiffParser()
        result = parser.parse(diff_text)

        hunks = result.files[0].hunks
        assert len(hunks) == 1
        assert hunks[0].new_start == 45
        assert hunks[0].new_lines == 8

    def test_parse_binary_file(self):
        """Handle binary file changes."""
        diff_text = '''diff --git a/image.png b/image.png
new file mode 100644
index 0000000..abc1234
Binary files /dev/null and b/image.png differ
'''
        parser = DiffParser()
        result = parser.parse(diff_text)

        assert len(result.files) == 1
        assert result.files[0].is_binary is True

    def test_parse_rename(self):
        """Handle file rename."""
        diff_text = '''diff --git a/old_name.py b/new_name.py
similarity index 95%
rename from old_name.py
rename to new_name.py
index abc..def 100644
--- a/old_name.py
+++ b/new_name.py
'''
        parser = DiffParser()
        result = parser.parse(diff_text)

        assert result.files[0].change_type == ChangeType.RENAMED
        assert result.files[0].old_path == "old_name.py"
        assert result.files[0].path == "new_name.py"
