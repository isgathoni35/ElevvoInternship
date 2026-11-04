# Task 2: Student Grade Processor with Custom Functions

A modular Python module and runner script that processes student records, calculates averages, finds highest and lowest scores, assigns pass/fail status, and validates scores.

---

## Features
- **Modular Design**: Core functions are organized in an importable `grade_processor.py` module.
- **Input Validation**: Ensures scores are within $0 \le \text{score} \le 100$.
- **Custom Exception & Type Hints (Bonus)**: Uses `InvalidScoreError` to handle out-of-range scores and includes Python type hints on all function signatures.

---

## Files
- `grade_processor.py`: Importable module with grade processing and validation functions.
- `main.py`: Entry point demonstrating module usage and error handling.
- `test_grade_processor.py`: Unit tests for all calculations and validation rules.

---

## How to Run

### 1. Run the Main Script
```bash
python task2/main.py
```

### 2. Run the Unit Tests
```bash
python -m unittest task2/test_grade_processor.py
```
