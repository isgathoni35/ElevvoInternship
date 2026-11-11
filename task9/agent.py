"""AI Agent for a Two-Tool Task (Task 9).

Implements an autonomous agent with a limited execution loop (max 5 steps),
tool dispatch (calculator, file-writer, and search), action-only execution logging
(strictly omitting internal reasoning), and LLM call tracking.
"""

import argparse
import ast
import json
import logging
import operator
import os
import re
from pathlib import Path
from typing import Dict, Any, Tuple
import requests
from dotenv import load_dotenv

# Load .env file from the script directory if present
load_dotenv(Path(__file__).parent / ".env")


def call_llm_agent_planner(goal: str, history: list, api_key: str, timeout: int = 15) -> dict:
    """Send goal and tool history to OpenAI to decide next tool action."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json"
    }
    history_desc = "\n".join([f"Step {h['step']}: Tool '{h['tool']}' with args {h['args']} -> Output: {h['output']}" for h in history]) or "None (starting first step)"
    prompt = f"""Goal: {goal}
Available Tools:
1. calculator(expression: str) -> evaluates math expressions
2. file_writer(filename: str, content: str) -> writes text to a file
3. search(query: str) -> searches knowledge base

History of previous steps:
{history_desc}

Decide the immediate next step. Return ONLY a JSON object:
If calling a tool:
{{"action": "call_tool", "tool": "calculator|file_writer|search", "args": {{"arg_name": "value"}}}}
If goal is finished:
{{"action": "finish", "report": "Summary of what was achieved"}}
"""
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are an autonomous AI Agent planner. Return only valid JSON for the next tool action."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0
    }
    response = requests.post(url, headers=headers, json=payload, timeout=timeout)
    response.raise_for_status()
    raw = response.json()["choices"][0]["message"]["content"].strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


# Setup action-only logging
def setup_agent_logger(log_filename: str = "agent_execution.log") -> logging.Logger:
    logger = logging.getLogger("AIAgent")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s - [ACTION LOG] - %(message)s")

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler
    fh = logging.FileHandler(log_filename, encoding="utf-8")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger


# ---------------------------------------------------------
# Tool Definitions
# ---------------------------------------------------------

# Safe math operators for calculator
ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def _eval_ast_math(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    elif isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPERATORS:
        left = _eval_ast_math(node.left)
        right = _eval_ast_math(node.right)
        return ALLOWED_OPERATORS[type(node.op)](left, right)
    elif isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_OPERATORS:
        operand = _eval_ast_math(node.operand)
        return ALLOWED_OPERATORS[type(node.op)](operand)
    else:
        raise ValueError(f"Unsupported math syntax: {ast.dump(node)}")


def tool_calculator(expression: str) -> str:
    """Tool 1: Safely evaluates an arithmetic expression."""
    clean_expr = expression.strip().replace("^", "**")
    try:
        tree = ast.parse(clean_expr, mode="eval")
        result = _eval_ast_math(tree.body)
        return str(round(result, 4))
    except Exception as e:
        return f"Error evaluating expression: {e}"


def tool_file_writer(filename: str, content: str) -> str:
    """Tool 2: Writes content to a destination file on disk."""
    try:
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Successfully saved {len(content)} characters to '{filename}'."
    except Exception as e:
        return f"Error writing file '{filename}': {e}"


def tool_search_knowledge_base(query: str) -> str:
    """Tool 3 (Bonus): Quick lookup in a local knowledge repository."""
    kb = {
        "elevo": "Elevo is a technology consultancy specializing in AI systems and backend engineering.",
        "python": "Python is a high-level interpreted programming language designed for readability.",
        "internship": "The Elevo internship covers core Python, OOP, APIs, web scraping, and AI engineering.",
    }
    q_lower = query.lower().strip()
    for key, text in kb.items():
        if key in q_lower:
            return text
    return f"No direct knowledge base entry found for '{query}'."


TOOLS = {
    "calculator": tool_calculator,
    "file_writer": tool_file_writer,
    "search": tool_search_knowledge_base,
}


# ---------------------------------------------------------
# Agent Execution Loop
# ---------------------------------------------------------

class AIAgent:
    """Agent execution harness with loop limit and action-only logging."""

    def __init__(self, max_steps: int = 5, logger: logging.Logger = None):
        self.max_steps = max_steps
        self.logger = logger or setup_agent_logger()
        self.llm_call_count = 0  # Bonus: track LLM calls

    def _call_llm_planner(self, goal: str, history: list) -> Dict[str, Any]:
        """Simulate or invoke LLM reasoning.

        Crucial Rule: Internal reasoning is NOT logged to the action log.
        """
        self.llm_call_count += 1

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key.strip():
            try:
                return call_llm_agent_planner(goal, history, api_key)
            except Exception:
                # Seamless fallback to deterministic planner on API/network error
                pass

        # Check if goal involves percentage / math and file writing
        # Example goal: "What's 15% of 240, and save the answer to a file called result.txt?"
        has_calc_done = any(h["tool"] == "calculator" for h in history)
        has_write_done = any(h["tool"] == "file_writer" for h in history)

        # Plan step 1: calculation
        if not has_calc_done:
            # Extract math expressions like '15% of 240' -> 240 * 0.15
            pct_match = re.search(r"(\d+(?:\.\d+)?)\s*%\s*of\s*(\d+(?:\.\d+)?)", goal, re.IGNORECASE)
            if pct_match:
                pct = float(pct_match.group(1)) / 100.0
                val = float(pct_match.group(2))
                return {
                    "action": "call_tool",
                    "tool": "calculator",
                    "args": {"expression": f"{val} * {pct}"}
                }

            # Check direct math expressions
            math_match = re.search(r"(\d+[\s\+\-\*\/\%]+\d+)", goal)
            if math_match:
                return {
                    "action": "call_tool",
                    "tool": "calculator",
                    "args": {"expression": math_match.group(1)}
                }

        # Plan step 2: file writing
        if has_calc_done and not has_write_done:
            calc_result = next(h["output"] for h in history if h["tool"] == "calculator")
            file_match = re.search(r"(?:save|write).*?(?:to|in)\s+(?:a\s+file\s+called\s+)?([a-zA-Z0-9_\-\.]+)", goal, re.IGNORECASE)
            filename = file_match.group(1) if file_match else "result.txt"
            return {
                "action": "call_tool",
                "tool": "file_writer",
                "args": {"filename": filename, "content": str(calc_result)}
            }

        # Completed
        if has_calc_done and has_write_done:
            calc_val = next(h["output"] for h in history if h["tool"] == "calculator")
            filename = next(h["args"]["filename"] for h in history if h["tool"] == "file_writer")
            return {
                "action": "finish",
                "report": f"Calculated {calc_val} and saved it to {filename}."
            }

        return {"action": "finish", "report": f"Goal completed with history: {len(history)} action(s)."}

    def run(self, goal: str) -> Dict[str, Any]:
        """Execute the agent loop for the specified goal."""
        self.logger.info(f"Agent received goal: '{goal}'")
        history = []
        step = 0

        while step < self.max_steps:
            step += 1
            # Step planner
            decision = self._call_llm_planner(goal, history)

            if decision.get("action") == "finish":
                final_report = decision.get("report", "Goal achieved.")
                self.logger.info(f"Goal Completed. Final Report: {final_report}")
                return {
                    "status": "success",
                    "steps_taken": step,
                    "llm_calls": self.llm_call_count,
                    "final_report": final_report,
                    "history": history
                }

            if decision.get("action") == "call_tool":
                tool_name = decision["tool"]
                tool_args = decision["args"]

                if tool_name not in TOOLS:
                    error_msg = f"Unknown tool: '{tool_name}'"
                    self.logger.error(error_msg)
                    break

                # Execute tool
                tool_func = TOOLS[tool_name]
                tool_output = tool_func(**tool_args)

                # MANDATORY REQUIREMENT: Log tool calls and outputs ONLY (no internal reasoning)
                self.logger.info(
                    f"Step {step} | Tool Used: '{tool_name}' | Inputs: {tool_args} | Output: '{tool_output}'"
                )

                history.append({
                    "step": step,
                    "tool": tool_name,
                    "args": tool_args,
                    "output": tool_output
                })

        # Loop limit exceeded guard
        self.logger.warning(f"Execution stopped: reached maximum step limit ({self.max_steps} steps).")
        return {
            "status": "loop_limit_exceeded",
            "steps_taken": step,
            "llm_calls": self.llm_call_count,
            "final_report": f"Agent halted after reaching maximum limit of {self.max_steps} steps.",
            "history": history
        }


def main():
    parser = argparse.ArgumentParser(description="AI Agent for Two-Tool Tasks")
    parser.add_argument(
        "--goal",
        default="What's 15% of 240, and save the answer to a file called result.txt?",
        help="Natural language goal for the agent"
    )
    parser.add_argument("--max-steps", type=int, default=5, help="Maximum execution steps (default: 5)")
    args = parser.parse_args()

    agent = AIAgent(max_steps=args.max_steps)
    result = agent.run(args.goal)

    print("\n" + "=" * 50)
    print("           AGENT RUN RESULT")
    print("=" * 50)
    print(f" Status     : {result['status']}")
    print(f" Steps Taken: {result['steps_taken']} (Max: {args.max_steps})")
    print(f" LLM Calls  : {result['llm_calls']}")
    print(f" Report     : {result['final_report']}")
    print("=" * 50)


if __name__ == "__main__":
    main()
