import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pathlib import Path
from .utils import write_upload_bytes
from .parsers import extract_text_auto
from .chunking import chunk_text
from .embeddings import embed_texts, get_embedding_model
from .chroma_store import add_documents, query_embeddings
from .ollama_client import generate_from_prompt
from .models import UploadResponse, QueryResponse
from .config import UPLOAD_DIR
import uuid

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload_file", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename
    content = await file.read()
    saved = write_upload_bytes(content, UPLOAD_DIR, filename)
    # extract text
    text = extract_text_auto(saved)
    if not text or not text.strip():
        logger.warning("No text extracted from file %s", filename)
        raise HTTPException(status_code=400, detail="No text extracted from file")
    # chunk
    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(status_code=500, detail="Chunking failed or produced zero chunks")
    # create ids and metadata
    ids = [f"{saved.stem}::chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]
    # embeddings
    embeddings = embed_texts(chunks)
    add_documents(ids, chunks, embeddings, metadatas)
    logger.info("File %s processed: %d chunks", filename, len(chunks))
    return {"status": "ok", "file": filename, "chunks": len(chunks)}

@router.post("/query", response_model=QueryResponse)
async def query(q: str = Form(...), k: int = Form(4)):
    q_text = q.strip()
    if not q_text:
        raise HTTPException(status_code=400, detail="Query is empty")
    # embed
    model = get_embedding_model()
    q_emb = model.encode([q_text], convert_to_numpy=True)[0]
    # retrieval
    results = query_embeddings(q_emb, n_results=k)
    retrieved = results.get("documents", [])
    metadatas = results.get("metadatas", [])
    # prepare sources for prompt
    sources = []
    for i, chunk in enumerate(retrieved):
        md = metadatas[i] if i < len(metadatas) else {}
        src = md.get("source", "unknown")
        ci = md.get("chunk_index", i)
        sources.append(f"[{src}::chunk{ci}] {chunk}")
    # prompt template
    prompt = (
        "Grounded QA Only. Use only the provided source texts below. "
        "If the answer cannot be found in these sources, respond exactly: \"No information in documents\".\n\n"
        "Sources:\n"
    )
    for s in sources:
        prompt += "\n---\n" + s + "\n"
    prompt += f"\nQuestion: {q_text}\n\nAnswer succinctly and include explicit citations like [filename::chunkIndex]."
    try:
        answer = generate_from_prompt(prompt, max_tokens=512, temperature=0.0)
    except Exception as e:
        logger.error("LLM generation failed: %s", e)
        raise HTTPException(status_code=502, detail="LLM generation failed")
    return {"answer": answer, "sources": metadatas, "raw_retrieval": retrieved}