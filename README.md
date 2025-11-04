# ThinkBook LM

A private, offline-first AI research assistant designed for secure document analysis and grounded question answering. ThinkBook LM uses local LLM inference and a local vector database to extract insights from uploaded documents without sending any data to the cloud.

## Key Features
- Local LLM inference (Ollama + Llama 3.1 8B)
- Secure offline Retrieval-Augmented Generation (RAG)
- PDF/DOCX/TXT ingestion and chunking
- Semantic search over local vector DB (ChromaDB)
- Citation-based grounded answers
- React-based web UI with file upload and chat
- FastAPI backend with local model execution

## Tech Stack
- FastAPI
- React + Tailwind
- Ollama + Llama 3.1
- ChromaDB
- SentenceTransformers MiniLM

## Goal
A secure alternative to NotebookLM powered entirely on your own machine.

---

**Status:** MVP in active development 🚧

PRs and contributions welcome.
