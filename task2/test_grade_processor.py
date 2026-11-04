"""Unit tests for Task 2: Student Grade Processor."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from grade_processor import (
    InvalidScoreError,
    assign_pass_fail,
    calculate_average,
    get_highest_score,
    get_lowest_score,
    validate_score,
)


class TestGradeProcessor(unittest.TestCase):
    def setUp(self):
        self.students = [
            {"name": "Alice", "score": 90.0},
            {"name": "Bob", "score": 60.0},
            {"name": "Charlie", "score": 40.0},
        ]

    def test_validate_score_valid(self):
        self.assertEqual(validate_score(0), 0.0)
        self.assertEqual(validate_score(100), 100.0)
        self.assertEqual(validate_score(75.5), 75.5)

    def test_validate_score_invalid(self):
        with self.assertRaises(InvalidScoreError):
            validate_score(-5)
        with self.assertRaises(InvalidScoreError):
            validate_score(105)

    def test_calculate_average(self):
        avg = calculate_average(self.students)
        # (90 + 60 + 40) / 3 = 63.33
        self.assertEqual(avg, 63.33)

    def test_get_highest_and_lowest(self):
        highest = get_highest_score(self.students)
        lowest = get_lowest_score(self.students)
        self.assertEqual(highest["name"], "Alice")
        self.assertEqual(lowest["name"], "Charlie")

    def test_assign_pass_fail(self):
        results = assign_pass_fail(self.students, passing_score=50.0)
        statuses = {s["name"]: s["status"] for s in results}
        self.assertEqual(statuses["Alice"], "Pass")
        self.assertEqual(statuses["Bob"], "Pass")
        self.assertEqual(statuses["Charlie"], "Fail")


if __name__ == "__main__":
    unittest.main()
