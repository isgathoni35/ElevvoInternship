"""Unit tests for Task 1: CLI Expense Tracker."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from expense_tracker import add_expense, load_expenses, save_expenses, monthly_summary


class TestExpenseTracker(unittest.TestCase):
    """Test core functionality of expense tracker."""

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.filename = self.temp_file.name

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_add_expense(self):
        expenses = []
        entry = add_expense(expenses, "45.50", "food", "2026-11-01")
        self.assertEqual(len(expenses), 1)
        self.assertEqual(entry["amount"], 45.50)
        self.assertEqual(entry["category"], "Food")
        self.assertEqual(entry["date"], "2026-11-01")

    def test_save_and_load_expenses(self):
        expenses = [
            {"amount": 10.0, "category": "Food", "date": "2026-11-01"},
            {"amount": 25.0, "category": "Travel", "date": "2026-11-02"},
        ]
        save_expenses(expenses, self.filename)
        loaded = load_expenses(self.filename)
        self.assertEqual(loaded, expenses)

    def test_load_nonexistent_file(self):
        loaded = load_expenses("non_existent_file_xyz.json")
        self.assertEqual(loaded, [])

    def test_monthly_summary_runs_cleanly(self):
        expenses = [
            {"amount": 20.0, "category": "Food", "date": "2026-11-01"},
            {"amount": 30.0, "category": "Food", "date": "2026-11-05"},
            {"amount": 50.0, "category": "Utilities", "date": "2026-11-10"},
            {"amount": 100.0, "category": "Travel", "date": "2026-10-15"},
        ]
        # Should execute without errors
        monthly_summary(expenses, "2026-11")


if __name__ == "__main__":
    unittest.main()
