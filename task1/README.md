# Task 1: CLI Expense Tracker with Persistent Storage

A clean, beginner-friendly command-line expense tracker built with Python and the built-in `json` module.

---

## Features
- **In-Memory Storage**: Uses a Python list of dictionaries to manage expenses during runtime.
- **Persistent Storage**: Automatically saves and reloads entries to/from a local `expenses.json` file.
- **Interactive CLI**: Menu-driven interface allowing users to add expenses, view all entries, and exit.
- **Bonus Feature (Monthly Summary)**: Aggregates total expenditure, item count, and category-level totals and averages for any given month using clean f-strings.

---

## Files
- `expense_tracker.py`: Main interactive CLI program and logic.
- `test_expense_tracker.py`: Automated tests verifying add, save, load, and summary logic.
- `expenses.json`: Local JSON persistence file (created on run).

---

## How to Run

### 1. Run the Application
```bash
python task1/expense_tracker.py
```

### 2. Run the Unit Tests
```bash
python -m unittest task1/test_expense_tracker.py
```
