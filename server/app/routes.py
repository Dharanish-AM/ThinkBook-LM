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


from fastapi import HTTPException
from .config import CHROMA_DIR
from .chroma_store import _client

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload_file", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename
    content = await file.read()
    saved = write_upload_bytes(content, UPLOAD_DIR, filename)
    
    text = extract_text_auto(saved)
    if not text or not text.strip():
        logger.warning("No text extracted from file %s", filename)
        raise HTTPException(status_code=400, detail="No text extracted from file")
    
    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(
            status_code=500, detail="Chunking failed or produced zero chunks"
        )
    
    base_name = Path(filename).stem
    ids = [f"{base_name}::chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]
    
    embeddings = embed_texts(chunks)
    add_documents(ids, chunks, embeddings, metadatas)
    logger.info("File %s processed: %d chunks", filename, len(chunks))
    return {"status": "ok", "file": filename, "chunks": len(chunks)}


@router.post("/query", response_model=QueryResponse)
async def query(q: str = Form(...), k: int = Form(4)):
    q_text = q.strip()
    if not q_text:
        raise HTTPException(status_code=400, detail="Query is empty")
    
    model = get_embedding_model()
    q_emb = model.encode([q_text], convert_to_numpy=True)[0]
    
    results = query_embeddings(q_emb, n_results=k)
    retrieved = results.get("documents", [])
    metadatas = results.get("metadatas", [])
    
    sources = []
    for i, chunk in enumerate(retrieved):
        md = metadatas[i] if i < len(metadatas) else {}
        src = md.get("source", "unknown")
        ci = md.get("chunk_index", i)
        sources.append(f"[{src}::chunk{ci}] {chunk}")
    
    prompt = (
        "Grounded QA Only. Use only the provided source texts below. "
        'If the answer cannot be found in these sources, respond exactly: "No information in documents".\n\n'
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



@router.get("/list_files")
async def list_files():
    try:
        collections = _client.list_collections()
        files = {}

        for col in collections:
            collection = _client.get_collection(col.name)
            data = collection.get(include=["metadatas"])

            for md in data.get("metadatas", []):
                src = md.get("source")
                if not src:
                    continue
                files.setdefault(src, 0)
                files[src] += 1

        return [{"name": k, "chunks": v} for k, v in files.items()]
    except Exception as e:
        logger.error("Failed to list files: %s", e)
        raise HTTPException(status_code=500, detail="Failed to list files")


@router.delete("/delete_file")
async def delete_file(name: str):
    try:
        total_deleted = 0
        collections = _client.list_collections()

        for col in collections:
            collection = _client.get_collection(col.name)

            
            data = collection.get(where={"source": name}, include=["metadatas"])
            metadatas = data.get("metadatas", [])

            
            ids = []
            for i, md in enumerate(metadatas):
                if md.get("source") == name:
                    ids.append(f"{Path(name).stem}::chunk_{md.get('chunk_index')}")

            
            if ids:
                collection.delete(ids=ids)
                total_deleted += len(ids)

        
        file_path = UPLOAD_DIR / name
        if file_path.exists():
            file_path.unlink()

        
        if total_deleted == 0 and not file_path.exists():
            raise HTTPException(
                status_code=404, detail=f"No data found for file {name}"
            )

        return {"status": "ok", "deleted_file": name, "deleted_chunks": total_deleted}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete file {name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete file")



@router.get("/get_file_text")
async def get_file_text(name: str):
    try:
        file_path = UPLOAD_DIR / name
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        text = extract_text_auto(file_path)
        if not text:
            raise HTTPException(status_code=500, detail="Failed to extract text")

        return {"name": name, "text": text[:50000]}  
    except Exception as e:
        logger.error(f"Failed to load text for {name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to load file text")
