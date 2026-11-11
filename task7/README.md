# Task 7: LLM-Powered Document Q&A Tool (RAG Basics)

A minimal Retrieval-Augmented Generation (RAG) tool that indexes local documents, performs cosine-similarity vector retrieval, enforces a hard confidence threshold to decline irrelevant queries with *"I don't know"*, and provides explicit source citations.

---

## Features
- **Document Chunking**: Splits documents into overlapping fixed-size chunks with metadata (`source`, `chunk_id`).
- **Vector Store & Embeddings**: In-memory vector store computing normalized term embeddings and cosine similarity.
- **Confidence Threshold Cutoff**: If the highest similarity score falls below `similarity_threshold` (default: 0.35), the tool declines to guess and returns `"I don't know."`
- **Source Citations**: Cites the exact document filename and chunk number for verified answers.
- **Multi-Format Support**: Automatically indexes both `.txt` and `.md` files.

---

## Files
- `rag_tool.py`: Core RAG engine, vector store, and interactive CLI.
- `documents/`: Sample document repository (Overview, Vacation, Remote Work, Security).
- `test_rag_tool.py`: Unit tests verifying chunking, retrieval accuracy, citations, and the out-of-domain threshold cutoff.

---

## How to Run

### 1. Ask a Relevant Question
```bash
python task7/rag_tool.py "How many days of paid vacation do employees get?"
```

### 2. Test an Irrelevant Question (Confidence Threshold Cutoff)
```bash
python task7/rag_tool.py "What is the capital of Mars?"
```

### 3. Run Interactively
```bash
python task7/rag_tool.py
```

### 4. Run Unit Tests
```bash
python -m unittest task7/test_rag_tool.py
```
