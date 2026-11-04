"""Unit tests for Task 8: AI-Assisted Code Review Tool."""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from code_reviewer import (
    build_review_prompt,
    extract_json_from_text,
    validate_review_entries,
    generate_diff,
    analyze_code_locally,
)


class TestCodeReviewer(unittest.TestCase):
    def test_build_review_prompt(self):
        prompt = build_review_prompt("x = 1", "test.py")
        self.assertIn("Bug Detection", prompt)
        self.assertIn("PEP 8 Compliance", prompt)
        self.assertIn("Refactor", prompt)
        self.assertIn("JSON list", prompt)

    def test_extract_json_with_fences(self):
        raw = """```json
        [{"category": "Bug", "issue": "Missing colon", "line": 5, "suggestion": "Add colon"}]
        ```"""
        parsed = extract_json_from_text(raw)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["category"], "Bug")

    def test_strict_validation_required_fields(self):
        sample_entries = [
            # Valid entry
            {"category": "Bug", "issue": "Syntax error", "line": 2, "suggestion": "Fix syntax"},
            # Missing 'issue' field
            {"category": "PEP 8", "line": 5, "suggestion": "Trim line"},
            # Empty 'suggestion' field
            {"category": "Refactor", "issue": "Loop inefficient", "line": 7, "suggestion": ""},
            # Non-dict item
            "Invalid string item instead of dict",
        ]

        valid, discarded = validate_review_entries(sample_entries, total_file_lines=10)
        self.assertEqual(len(valid), 1)
        self.assertEqual(valid[0]["issue"], "Syntax error")
        self.assertEqual(len(discarded), 3)

    def test_line_number_approximate_marking(self):
        entries = [
            # In-bounds line
            {"category": "Bug", "issue": "Issue 1", "line": 3, "suggestion": "Fix 1"},
            # Out-of-bounds line (file only has 5 lines)
            {"category": "Bug", "issue": "Issue 2", "line": 99, "suggestion": "Fix 2"},
            # Negative line
            {"category": "Bug", "issue": "Issue 3", "line": -2, "suggestion": "Fix 3"},
        ]

        valid, discarded = validate_review_entries(entries, total_file_lines=5)
        self.assertEqual(len(valid), 3)
        self.assertEqual(valid[0]["line_status"], "verified")
        self.assertEqual(valid[1]["line_status"], "approximate")
        self.assertEqual(valid[2]["line_status"], "approximate")

    def test_diff_generation(self):
        original = ["def foo():\n", "    pass\n"]
        diff = generate_diff(original, line_num=2, replacement_line="    return True")
        self.assertIn("-    pass", diff)
        self.assertIn("+    return True", diff)

    def test_target_file_not_modified_safety(self):
        target_code = "def sample():\n    pass\n"
        findings = analyze_code_locally(target_code, "temp.py")
        # Code inspection produces suggestions without mutating target_code
        self.assertEqual(target_code, "def sample():\n    pass\n")


if __name__ == "__main__":
    unittest.main()
