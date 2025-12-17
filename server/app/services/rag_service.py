import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, Any, List

from ..rag.chunking import chunk_text
from ..rag.embeddings import embed_texts, get_embedding_model
from ..rag.qdrant_store import add_documents, query_embeddings, get_collection_count
from .llm_service import LLMService

logger = logging.getLogger(__name__)

class RagService:
    """Service to handle RAG operations: indexing and querying."""

    @staticmethod
    async def process_document(text: str, filename: str) -> Dict[str, Any]:
        """
        Processes a document text: chunks, embeds, and indexes it.
        
        Args:
            text: The full text of the document.
            filename: The name of the file (used for metadata/IDs).
            
        Returns:
            Dict: Status info.
        """
        # CPU-bound chunking
        chunks = chunk_text(text)
        if not chunks:
            raise ValueError("Chunking failed or produced zero chunks")

        base_name = Path(filename).stem
        ids = [f"{base_name}::chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]

        # Run embedding in thread pool as it might be CPU intensive (or GPU)
        # and we don't want to block the event loop
        embeddings = await asyncio.to_thread(embed_texts, chunks)

        # IO/DB bound
        await asyncio.to_thread(add_documents, ids, chunks, embeddings, metadatas)
        
        logger.info("File %s processed: %d chunks", filename, len(chunks))
        return {"status": "ok", "file": filename, "chunks": len(chunks)}

    @staticmethod
    async def query(query_text: str, k: int = 4) -> Dict[str, Any]:
        """
        Queries the knowledge base and generates an answer using the LLM.
        """
        start_time = time.time()
        logger.info(f"Processing query: {query_text}")

        # 0. Check available chunks and clamp k
        count = await asyncio.to_thread(get_collection_count)
        if count == 0:
            return {
                "answer": "I don't have any documents uploaded yet. Please upload some files first.",
                "sources": [],
                "raw_retrieval": [],
                "duration": time.time() - start_time
            }
        
        k = min(k, count)
        logger.info(f"Querying with k={k} (total docs: {count})")

        # 1. Embed query
        model = get_embedding_model() # This is fast access to cached obj
        # encode is blocking
        q_emb = await asyncio.to_thread(model.encode, [query_text], convert_to_numpy=True)
        q_emb = q_emb[0]

        # 2. Retrieve relevant docs from Chroma
        results = await asyncio.to_thread(query_embeddings, q_emb, n_results=k)
        retrieved = results.get("documents", [])
        metadatas = results.get("metadatas", [])

        # 3. Construct Context
        sources = []
        max_len = 500
        for i, chunk in enumerate(retrieved):
            md = metadatas[i] if i < len(metadatas) else {}
            src = md.get("source", "unknown")
            ci = md.get("chunk_index", i)
            # Safe truncation
            chunk_content = chunk[:max_len] if chunk else ""
            sources.append(f"[{src}::chunk{ci}] {chunk_content}")

        # 4. Construct Prompt
        context_block = "\n---\n".join(sources)
        prompt = (
            "You are an expert, intelligent research assistant. "
            "Your goal is to provide comprehensive, accurate, and satisfying answers based *only* on the provided documents. "
            "If the answer is not in the documents, say 'I couldn't find that information in the documents'.\n\n"
            "Guidelines for a great response:\n"
            "1. **Be Comprehensive**: Cover all relevant details found in the sources. Do not be overly brief unless asked.\n"
            "2. **Structure**: Use Markdown headers (##), bullet points, and bold text to make the answer easy to read.\n"
            "3. **Tone**: Maintain a professional, helpful, and engaging tone.\n"
            "4. **No Hallucinations**: Do not invent facts.\n\n"
            f"=== Document Sources ===\n{context_block}\n\n"
            f"=== User Query ===\n{query_text}\n\n"
            "Answer the query below in a well-structured format:"
        )

        # 5. Generate Answer via LLM
        answer = await asyncio.to_thread(LLMService.generate, prompt)

        end_time = time.time()
        logger.info(f"Query completed in {end_time - start_time:.2f}s")
        
        return {
            "answer": answer,
            "sources": metadatas,
            "raw_retrieval": retrieved,
            "duration": end_time - start_time
        }
