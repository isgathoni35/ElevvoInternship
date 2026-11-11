"""Document Q&A Tool (RAG Basics).

Implements document chunking, vector embedding, cosine similarity search,
confidence threshold cutoff ('I don't know' for low similarity),
and answer synthesis with source chunk citations.
"""

import argparse
import math
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
import requests
from dotenv import load_dotenv

# Load .env file from the script directory if present
load_dotenv(Path(__file__).parent / ".env")


def call_llm_synthesis(context: str, question: str, api_key: str, timeout: int = 15) -> str:
    """Synthesize natural answer using OpenAI API based strictly on retrieved context."""
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
                "content": "You are a helpful assistant. Answer the user question based strictly on the provided documentation context. Do not invent facts."
            },
            {
                "role": "user",
                "content": f"Documentation Context:\n{context}\n\nQuestion: {question}"
            }
        ],
        "temperature": 0.2
    }
    response = requests.post(url, headers=headers, json=payload, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


class DocumentChunker:
    """Splits raw text documents into fixed-size chunks with metadata."""

    def __init__(self, chunk_size: int = 250, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str, source_name: str) -> List[Dict[str, Any]]:
        cleaned = " ".join(text.split())
        if not cleaned:
            return []

        step = max(1, self.chunk_size - self.chunk_overlap)
        chunks = []
        chunk_id = 1

        for start in range(0, len(cleaned), step):
            end = min(len(cleaned), start + self.chunk_size)
            chunk_slice = cleaned[start:end].strip()
            if chunk_slice:
                chunks.append({
                    "chunk_id": chunk_id,
                    "source": source_name,
                    "text": chunk_slice
                })
                chunk_id += 1
            if end >= len(cleaned):
                break

        return chunks


class SimpleVectorStore:
    """In-memory vector store using TF-IDF embedding and cosine similarity."""

    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []
        self.vocabulary: Dict[str, int] = {}
        self.idf: np.ndarray = np.array([])
        self.vectors: np.ndarray = np.array([])

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\b[a-zA-Z0-9_-]{2,}\b", text.lower())

    def index_documents(self, documents: List[Dict[str, Any]]):
        """Build vocabulary, calculate IDF, and store normalized chunk embeddings."""
        self.chunks = documents
        if not self.chunks:
            return

        # Build vocabulary
        doc_tokens = [self._tokenize(c["text"]) for c in self.chunks]
        all_words = sorted(list({w for tokens in doc_tokens for w in tokens}))
        self.vocabulary = {w: i for i, w in enumerate(all_words)}
        vocab_size = len(self.vocabulary)

        if vocab_size == 0:
            return

        # Calculate Document Frequency (DF)
        num_chunks = len(self.chunks)
        df = np.zeros(vocab_size)
        for tokens in doc_tokens:
            unique_tokens = set(tokens)
            for w in unique_tokens:
                if w in self.vocabulary:
                    df[self.vocabulary[w]] += 1

        # Smooth IDF
        self.idf = np.log((1 + num_chunks) / (1 + df)) + 1.0

        # Vectorize all chunks
        vectors = np.zeros((num_chunks, vocab_size))
        for row_idx, tokens in enumerate(doc_tokens):
            for w in tokens:
                col_idx = self.vocabulary[w]
                vectors[row_idx, col_idx] += 1
            # Apply IDF
            vectors[row_idx] *= self.idf
            # L2 normalize
            norm = np.linalg.norm(vectors[row_idx])
            if norm > 0:
                vectors[row_idx] /= norm

        self.vectors = vectors

    def embed_query(self, query: str) -> np.ndarray:
        """Convert a query string into a normalized TF-IDF vector."""
        vocab_size = len(self.vocabulary)
        if vocab_size == 0:
            return np.zeros(0)

        vec = np.zeros(vocab_size)
        for w in self._tokenize(query):
            if w in self.vocabulary:
                vec[self.vocabulary[w]] += 1

        vec *= self.idf
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec

    def search(self, query: str, top_k: int = 2) -> List[Tuple[Dict[str, Any], float]]:
        """Find most similar chunks using cosine similarity."""
        if len(self.chunks) == 0 or len(self.vocabulary) == 0:
            return []

        q_vec = self.embed_query(query)
        if np.linalg.norm(q_vec) == 0:
            return []

        # Cosine similarity (since both vectors are unit normalized)
        similarities = np.dot(self.vectors, q_vec)

        # Get top indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            results.append((self.chunks[idx], score))
        return results


class RAGTool:
    """Coordinates retrieval, confidence score threshold checking, and synthesis."""

    def __init__(self, docs_directory: str | Path, similarity_threshold: float = 0.35):
        self.docs_directory = Path(docs_directory)
        self.similarity_threshold = similarity_threshold
        self.chunker = DocumentChunker()
        self.vector_store = SimpleVectorStore()
        self._load_and_index()

    def _load_and_index(self):
        """Scan documents directory and index all text chunks."""
        all_chunks = []
        if self.docs_directory.exists():
            for file_path in sorted(self.docs_directory.glob("*")):
                if file_path.suffix.lower() in [".txt", ".md"]:
                    content = file_path.read_text(encoding="utf-8")
                    chunks = self.chunker.chunk_text(content, file_path.name)
                    all_chunks.extend(chunks)

        self.vector_store.index_documents(all_chunks)

    def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer a query using retrieved context, strictly observing similarity threshold."""
        matches = self.vector_store.search(question, top_k=2)

        if not matches:
            return {
                "answer": "I don't know.",
                "reason": "No relevant document matches found.",
                "citations": [],
                "confidence_score": 0.0,
                "status": "declined_below_threshold"
            }

        best_chunk, best_score = matches[0]

        # Return fallback if top match is below similarity threshold
        if best_score < self.similarity_threshold:
            return {
                "answer": "I don't know.",
                "reason": (
                    f"Top similarity score ({best_score:.2f}) is below confidence "
                    f"threshold ({self.similarity_threshold:.2f}). Declining to guess."
                ),
                "citations": [],
                "confidence_score": round(best_score, 2),
                "status": "declined_below_threshold"
            }

        # Synthesize answer (via live LLM if key present, else local synthesis)
        citations = []
        context_snippets = []
        for chunk, score in matches:
            if score >= self.similarity_threshold:
                citations.append(f"{chunk['source']} (Chunk #{chunk['chunk_id']}, Score: {score:.2f})")
                context_snippets.append(chunk["text"])

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key.strip():
            combined_context = "\n\n".join(context_snippets)
            try:
                answer_text = call_llm_synthesis(combined_context, question, api_key)
            except Exception as e:
                # Graceful fallback to local synthesis if network or API key fails
                answer_text = (
                    f"Based on internal documentation (API notice: {e}):\n"
                    f"\"{best_chunk['text']}\""
                )
        else:
            answer_text = (
                f"Based on the internal documentation:\n"
                f"\"{best_chunk['text']}\""
            )

        return {
            "answer": answer_text,
            "citations": citations,
            "confidence_score": round(best_score, 2),
            "status": "answered"
        }


def main():
    parser = argparse.ArgumentParser(description="LLM-Powered Document Q&A Tool (RAG Basics)")
    parser.add_argument("query", nargs="?", help="Question to ask the document repository")
    parser.add_argument("--docs", default=str(Path(__file__).parent / "documents"),
                        help="Path to folder containing documents")
    parser.add_argument("--threshold", type=float, default=0.35,
                        help="Confidence score threshold for 'I don't know' cutoff (default: 0.35)")
    args = parser.parse_args()

    rag = RAGTool(docs_directory=args.docs, similarity_threshold=args.threshold)
    print(f"Loaded {len(rag.vector_store.chunks)} chunks from {args.docs}.")
    print(f"Similarity confidence threshold: {args.threshold}\n")

    if args.query:
        run_query(rag, args.query)
    else:
        # Interactive loop
        print("Type your questions below (or 'exit' to quit):")
        while True:
            try:
                user_q = input("\nQuestion: ").strip()
                if not user_q:
                    continue
                if user_q.lower() in ["exit", "quit", "q"]:
                    break
                run_query(rag, user_q)
            except (KeyboardInterrupt, EOFError):
                break


def run_query(rag: RAGTool, question: str):
    print(f"User Question : {question}")
    result = rag.answer_question(question)
    print(f"Status        : {result['status']}")
    print(f"Confidence    : {result['confidence_score']}")
    print(f"Answer        : {result['answer']}")
    if result.get("reason"):
        print(f"Reason        : {result['reason']}")
    if result["citations"]:
        print("Citations     :")
        for c in result["citations"]:
            print(f"  - {c}")


if __name__ == "__main__":
    main()
