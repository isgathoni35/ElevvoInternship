"""Unit tests for Task 9: AI Agent for a Two-Tool Task."""

import logging
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from agent import (
    AIAgent,
    tool_calculator,
    tool_file_writer,
    tool_search_knowledge_base,
)


class TestAIAgent(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.orig_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self.orig_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_calculator_tool(self):
        self.assertEqual(tool_calculator("240 * 0.15"), "36.0")
        self.assertEqual(tool_calculator("100 / 4"), "25.0")
        self.assertEqual(tool_calculator("2 ^ 3"), "8")
        # Unsafe syntax rejection
        result = tool_calculator("__import__('os').system('ls')")
        self.assertIn("Error", result)

    def test_file_writer_tool(self):
        out_file = "test_output.txt"
        msg = tool_file_writer(out_file, "Sample Content")
        self.assertIn("Successfully saved", msg)
        self.assertTrue(Path(out_file).exists())
        self.assertEqual(Path(out_file).read_text(encoding="utf-8"), "Sample Content")

    def test_reference_workflow(self):
        """Test the exact workflow specified in the assignment PDF."""
        # Create dedicated logger capturing output in memory
        log_records = []
        logger = logging.getLogger("TestAgentRef")
        logger.setLevel(logging.INFO)
        logger.handlers.clear()

        class RecordHandler(logging.Handler):
            def emit(self, record):
                log_records.append(record.getMessage())

        logger.addHandler(RecordHandler())

        agent = AIAgent(max_steps=5, logger=logger)
        goal = "What's 15% of 240, and save the answer to a file called result.txt?"
        result = agent.run(goal)

        # 1. Assert status and steps
        self.assertEqual(result["status"], "success")
        self.assertLessEqual(result["steps_taken"], 5)
        self.assertEqual(result["final_report"], "Calculated 36.0 and saved it to result.txt.")

        # 2. Assert file was created and contains result
        res_file = Path("result.txt")
        self.assertTrue(res_file.exists())
        self.assertEqual(res_file.read_text(encoding="utf-8"), "36.0")

        # 3. Assert tool calls and action-only logging
        full_logs = "\n".join(log_records)
        self.assertIn("Tool Used: 'calculator'", full_logs)
        self.assertIn("Output: '36.0'", full_logs)
        self.assertIn("Tool Used: 'file_writer'", full_logs)

        # Confirm NO chain of thought / hidden reasoning logged
        self.assertNotIn("chain-of-thought", full_logs)
        self.assertNotIn("<thinking>", full_logs)

        # 4. Assert LLM calls were tracked (Bonus)
        self.assertGreaterEqual(result["llm_calls"], 2)

    def test_execution_loop_limit(self):
        """Verify the agent cannot loop indefinitely and stops at max_steps."""
        logger = logging.getLogger("TestLimit")
        logger.setLevel(logging.CRITICAL)

        # Initialize with a low limit of 2 steps
        agent = AIAgent(max_steps=2, logger=logger)

        class StuckAgent(AIAgent):
            def _call_llm_planner(self, goal, history):
                self.llm_call_count += 1
                return {"action": "call_tool", "tool": "search", "args": {"query": "something"}}

        stuck = StuckAgent(max_steps=2, logger=logger)
        res = stuck.run("Do an impossible repeating task")

        self.assertEqual(res["status"], "loop_limit_exceeded")
        self.assertEqual(res["steps_taken"], 2)
        self.assertIn("maximum limit", res["final_report"])


if __name__ == "__main__":
    unittest.main()
