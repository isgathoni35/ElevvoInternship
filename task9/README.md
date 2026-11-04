# Task 9: AI Agent for a Two-Tool Task

A lightweight, autonomous AI agent capable of breaking down natural language goals, invoking dedicated tools (`calculator` and `file_writer`), strictly enforcing a maximum step execution loop, logging actions only (omitting hidden chain-of-thought), and tracking LLM calls.

---

## Features
- **Two Core Tools**:
  - `calculator`: Safely evaluates arithmetic expressions using AST parsing (no unsafe `eval`).
  - `file_writer`: Writes generated results to specified local files.
  - `search` (Bonus): Quick lookup tool for internal knowledge snippets.
- **Limited Execution Loop (Core Constraint)**: Enforces a strict step cap (`max_steps = 5`) to prevent infinite looping.
- **Action-Only Logging (Core Constraint)**: Uses Python's standard `logging` library to record tool name, input arguments, and output results. Never logs hidden reasoning or chain-of-thought tokens.
- **Call Counting (Bonus)**: Tracks `llm_call_count` to record the exact number of planner/LLM calls made to fulfill the goal.

---

## Files
- `agent.py`: Agent execution loop, tools, action logger, and planner.
- `test_agent.py`: Unit tests verifying the reference workflow, loop limit enforcement, action-only logging compliance, and tool safety.
- `agent_execution.log`: Generated action log file.

---

## How to Run

### 1. Run the Reference Workflow
```bash
python task9/agent.py --goal "What's 15% of 240, and save the answer to a file called result.txt?"
```

### 2. Run with Custom Goal or Max Steps
```bash
python task9/agent.py --goal "Calculate 450 * 0.20 and save in discount.txt" --max-steps 4
```

### 3. Run Unit Tests
```bash
python -m unittest task9/test_agent.py
```
