# Task 8: AI-Assisted Code Review Tool

A Python code review tool that analyzes scripts for bugs, PEP 8 compliance, and refactoring opportunities, strictly validates structured JSON output, flags unverifiable line numbers as "approximate", and safely presents before/after diffs without executing changes.

---

## Features
- **Structured Review Prompting**: Generates structured review prompts targeting Bug Detection, PEP 8 Compliance, and Refactoring.
- **Strict Output Validation**: Validates that all findings contain required non-empty fields (`issue`, `line`, `suggestion`). Malformed or incomplete items are flagged and discarded.
- **Line Verification**: Cross-references reported line numbers against the actual target file length. Out-of-bounds line numbers are marked as `"approximate"`.
- **Read-Only Safety**: Strictly reviews and reports suggestions — never automatically executes or applies code changes.
- **Diff Preview (Bonus)**: Generates unified before/after diffs for suggested line replacements.

---

## Files
- `code_reviewer.py`: Main review pipeline, validation engine, line checker, and diff generator.
- `sample_target.py`: Sample Python file with deliberate PEP 8, bug, and refactoring issues.
- `test_code_reviewer.py`: Unit tests verifying prompt generation, JSON extraction, field validation, line approximation, and diff generation.

---

## How to Run

### 1. Run Review on Sample File
```bash
python task8/code_reviewer.py task8/sample_target.py
```

### 2. Run Review with Before/After Diff Preview
```bash
python task8/code_reviewer.py task8/sample_target.py --diff
```

### 3. Run Unit Tests
```bash
python -m unittest task8/test_code_reviewer.py
```
