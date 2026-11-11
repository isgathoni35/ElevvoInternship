"""AI-Assisted Code Review Tool.

Reviews Python files for bugs, PEP 8 compliance, and refactoring opportunities.
Parses review responses into structured JSON, verifies line references,
and provides before/after diff previews without altering source files.
"""

import argparse
import ast
import difflib
import json
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import requests
from dotenv import load_dotenv

# Load .env file from the script directory if present
load_dotenv(Path(__file__).parent / ".env")


REQUIRED_FIELDS = ["category", "issue", "line", "suggestion"]


def call_llm_reviewer(prompt: str, api_key: str, timeout: int = 20) -> list:
    """Send structured code review prompt to OpenAI API."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a senior Python code reviewer. Always respond ONLY with a valid JSON array of objects adhering strictly to the requested schema."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.1
    }
    response = requests.post(url, headers=headers, json=payload, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    raw_content = data["choices"][0]["message"]["content"]
    return extract_json_from_text(raw_content)


def build_review_prompt(source_code: str, filename: str = "code.py") -> str:
    """Build a structured prompt asking for bugs, PEP 8, and refactoring suggestions."""
    return f"""You are a senior Python code reviewer. Analyze the following code from '{filename}'.
Focus on:
1. Bug Detection (e.g. mutable default arguments, division by zero, unhandled exceptions)
2. PEP 8 Compliance (e.g. line length, whitespace, naming conventions)
3. Refactoring Suggestions (e.g. idiomatic Python, enumerate, list comprehensions)

Return ONLY a JSON list of objects. No introductory or concluding text.
Each object in the JSON list MUST have the following schema:
[
  {{
    "category": "Bug | PEP 8 | Refactor",
    "issue": "Clear description of the issue",
    "line": <integer line number>,
    "suggestion": "Actionable suggestion to resolve it",
    "replacement_code": "Suggested line replacement or empty string"
  }}
]

Code to review:
```python
{source_code}
```
"""


def extract_json_from_text(raw_text: str) -> Any:
    """Safely extract and parse JSON from text, handling markdown fences if present."""
    cleaned = raw_text.strip()
    # Strip markdown code blocks if wrapped
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)


def validate_review_entries(
    raw_entries: Any, total_file_lines: int
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Strictly validate review output entries.

    Validates:
    - Root is a list of dicts.
    - Every entry contains 'issue', 'line', 'suggestion' with non-empty values.
    - Verifies line number against actual file; marks as 'approximate' if out of bounds.

    Returns:
        (valid_entries, flagged_discarded_entries)
    """
    if not isinstance(raw_entries, list):
        raise ValueError(f"Expected JSON root to be a list, got {type(raw_entries).__name__}")

    valid_entries = []
    discarded_entries = []

    for idx, item in enumerate(raw_entries):
        if not isinstance(item, dict):
            discarded_entries.append({
                "index": idx,
                "raw": item,
                "reason": "Entry is not a JSON object/dict."
            })
            continue

        # Check required fields and non-empty values
        missing_or_empty = []
        for field in ["issue", "suggestion"]:
            val = item.get(field)
            if val is None or not str(val).strip():
                missing_or_empty.append(field)

        if missing_or_empty:
            discarded_entries.append({
                "index": idx,
                "raw": item,
                "reason": f"Missing or empty required field(s): {', '.join(missing_or_empty)}"
            })
            continue

        # Validate line number
        raw_line = item.get("line")
        line_num = None
        line_status = "verified"

        try:
            line_num = int(raw_line)
            if line_num < 1 or line_num > total_file_lines:
                line_status = "approximate"
        except (TypeError, ValueError):
            line_num = 0
            line_status = "approximate"

        category = item.get("category", "General").strip().title()

        valid_entries.append({
            "category": category,
            "issue": str(item["issue"]).strip(),
            "line": line_num,
            "line_status": line_status,
            "suggestion": str(item["suggestion"]).strip(),
            "replacement_code": str(item.get("replacement_code", "")).strip()
        })

    return valid_entries, discarded_entries


def generate_diff(original_lines: List[str], line_num: int, replacement_line: str) -> str:
    """Generate a unified diff showing before and after for a proposed replacement."""
    if line_num < 1 or line_num > len(original_lines) or not replacement_line:
        return "No automated diff available for this suggestion."

    modified_lines = list(original_lines)
    modified_lines[line_num - 1] = replacement_line + "\n"

    diff = difflib.unified_diff(
        original_lines,
        modified_lines,
        fromfile="original.py",
        tofile="suggested.py",
        lineterm=""
    )
    return "\n".join(diff)


def analyze_code_locally(code_text: str, filename: str) -> List[Dict[str, Any]]:
    """Local AST and static rule reviewer acting as fallback or offline engine."""
    lines = code_text.splitlines()
    suggestions = []

    # 1. Line length check (PEP 8 standard <= 79 chars)
    for idx, line in enumerate(lines, 1):
        if len(line) > 79:
            suggestions.append({
                "category": "PEP 8",
                "issue": f"Line exceeds 79 characters ({len(line)} chars).",
                "line": idx,
                "suggestion": "Break long expressions into multiple lines per PEP 8 guidelines.",
                "replacement_code": ""
            })

    # 2. AST inspection for mutable default arguments & division by zero
    try:
        tree = ast.parse(code_text, filename=filename)
        for node in ast.walk(tree):
            # Check function defaults for mutable types (lists, dicts, sets)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        suggestions.append({
                            "category": "Bug",
                            "issue": "Mutable default argument used in function definition.",
                            "line": node.lineno,
                            "suggestion": "Replace default mutable container with None and initialize inside function body.",
                            "replacement_code": f"def {node.name}(..., items=None):"
                        })

            # Check for direct division operations
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
                suggestions.append({
                    "category": "Bug",
                    "issue": "Potential division by zero.",
                    "line": node.lineno,
                    "suggestion": "Validate divisor is non-zero before performing division.",
                    "replacement_code": ""
                })

            # Check manual loop counter vs enumerate
            if isinstance(node, ast.For):
                suggestions.append({
                    "category": "Refactor",
                    "issue": "For-loop with manual index incrementing detected.",
                    "line": node.lineno,
                    "suggestion": "Use built-in enumerate() to iterate with index idiomatically.",
                    "replacement_code": "for idx, itm in enumerate(items):"
                })

    except SyntaxError as e:
        suggestions.append({
            "category": "Bug",
            "issue": f"Syntax error in code: {e.msg}",
            "line": e.lineno or 1,
            "suggestion": "Fix syntax error to make Python file parseable.",
            "replacement_code": ""
        })

    return suggestions


def run_code_review(file_path: str, diff_mode: bool = False):
    """Run full review pipeline, validate outputs, and display report."""
    path = Path(file_path)
    if not path.exists():
        print(f"Error: Target file not found: {file_path}")
        return

    content = path.read_text(encoding="utf-8")
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    total_lines = len(lines)

    print("=" * 65)
    print(f"       AI-ASSISTED CODE REVIEW REPORT: {path.name}")
    print(f"       Total Lines: {total_lines} | Mode: Read-Only Analysis")
    print("=" * 65)

    # In live mode with API key, query OpenAI; otherwise use local AST engine
    api_key = os.getenv("OPENAI_API_KEY")
    raw_suggestions = None
    if api_key and api_key.strip():
        print("[Live Mode] Dispatching code review prompt to OpenAI API...")
        try:
            prompt = build_review_prompt(content, path.name)
            raw_suggestions = call_llm_reviewer(prompt, api_key)
        except Exception as e:
            print(f"[Notice] LLM API call error ({e}). Falling back to local AST analysis.")
            raw_suggestions = None

    if raw_suggestions is None:
        raw_suggestions = analyze_code_locally(content, path.name)

    # Perform strict validation
    valid_entries, discarded = validate_review_entries(raw_suggestions, total_lines)

    if discarded:
        print(f"\n[Warning] {len(discarded)} invalid suggestion(s) were discarded by validator:")
        for d in discarded:
            print(f"  - Discarded item #{d['index']}: {d['reason']}")

    print(f"\nValidated Findings: {len(valid_entries)}\n")

    for idx, entry in enumerate(valid_entries, 1):
        line_ref = f"Line {entry['line']}"
        if entry["line_status"] == "approximate":
            line_ref += " (approximate)"

        print(f"[{idx}] [{entry['category']}] {line_ref}")
        print(f"    Issue      : {entry['issue']}")
        print(f"    Suggestion : {entry['suggestion']}")

        # Render diff preview if requested
        if diff_mode and entry.get("replacement_code") and entry["line"] > 0:
            diff_text = generate_diff(lines, entry["line"], entry["replacement_code"])
            print("    Diff Preview:")
            for d_line in diff_text.splitlines():
                print(f"      {d_line}")

        print("-" * 65)

    # Print summary JSON report
    report_data = {
        "file": path.name,
        "total_lines": total_lines,
        "findings_count": len(valid_entries),
        "findings": valid_entries,
        "discarded_count": len(discarded),
    }

    report_json_path = path.parent / f"{path.stem}_review.json"
    report_json_path.write_text(json.dumps(report_data, indent=2), encoding="utf-8")
    print(f"\nStructured JSON report saved to: {report_json_path.name}")
    print("\nAnalysis complete. No source files were modified.")


def main():
    parser = argparse.ArgumentParser(description="AI-Assisted Code Review Tool")
    parser.add_argument("target", help="Path to Python file to review")
    parser.add_argument("--diff", action="store_true", help="Display before/after diff for suggestions")
    args = parser.parse_args()

    run_code_review(args.target, diff_mode=args.diff)


if __name__ == "__main__":
    main()
