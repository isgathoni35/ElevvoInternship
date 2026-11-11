"""Unit tests for Task 7: LLM-Powered Document Q&A Tool (RAG Basics)."""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from rag_tool import DocumentChunker, SimpleVectorStore, RAGTool

DOCS_DIR = Path(__file__).parent / "documents"


class TestRAGTool(unittest.TestCase):
    def test_chunker(self):
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
        text = "This is a sentence. " * 15  # ~300 chars
        chunks = chunker.chunk_text(text, "test_doc.txt")
        self.assertGreater(len(chunks), 1)
        self.assertEqual(chunks[0]["source"], "test_doc.txt")
        self.assertEqual(chunks[0]["chunk_id"], 1)

    def test_vector_store_retrieval(self):
        store = SimpleVectorStore()
        chunks = [
            {"chunk_id": 1, "source": "leave.txt", "text": "Annual leave policy allows 25 days paid vacation."},
            {"chunk_id": 2, "source": "network.txt", "text": "VPN tunnel is required when connecting to public WiFi."}
        ]
        store.index_documents(chunks)
        results = store.search("vacation days and leave")
        self.assertGreater(len(results), 0)
        top_chunk, score = results[0]
        self.assertEqual(top_chunk["chunk_id"], 1)
        self.assertGreater(score, 0.4)

    def test_answer_relevant_question_with_citation(self):
        rag = RAGTool(docs_directory=DOCS_DIR, similarity_threshold=0.35)
        result = rag.answer_question("How many days of paid annual leave do employees receive?")

        self.assertEqual(result["status"], "answered")
        self.assertGreaterEqual(result["confidence_score"], 0.35)
        self.assertIn("25 days", result["answer"])
        self.assertGreater(len(result["citations"]), 0)
        self.assertIn("doc2_vacation_policy.txt", result["citations"][0])

    def test_decline_out_of_domain_question(self):
        """Verify that out-of-domain queries return fallback answer."""
        rag = RAGTool(docs_directory=DOCS_DIR, similarity_threshold=0.35)
        # Completely unrelated question
        result = rag.answer_question("What is the recipe for chocolate lava cake on planet Mars?")

        self.assertEqual(result["status"], "declined_below_threshold")
        self.assertEqual(result["answer"], "I don't know.")
        self.assertLess(result["confidence_score"], 0.35)
        self.assertEqual(len(result["citations"]), 0)


if __name__ == "__main__":
    unittest.main()
