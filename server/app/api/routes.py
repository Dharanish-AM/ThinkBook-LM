import logging
import asyncio
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Form

from ..core.utils import write_upload_bytes
from ..parsers import extract_text_auto
from ..rag.chroma_store import _client
from ..core.config import UPLOAD_DIR
from ..services.rag_service import RagService
from .models import UploadResponse, QueryResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload_file", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename
    try:
        content = await file.read()
        saved_path = write_upload_bytes(content, UPLOAD_DIR, filename)
        
        # Using the new Parser Registry indirectly via extract_text_auto
        text = extract_text_auto(saved_path)
        if not text or not text.strip():
            logger.warning("No text extracted from file %s", filename)
            raise HTTPException(status_code=400, detail="No text extracted from file. File type might not be supported or file is empty.")
        
        # Delegate processing to RagService
        result = await RagService.process_document(text, filename)
        return result
        
    except ValueError as ve:
         raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Internal processing error")


@router.post("/query", response_model=QueryResponse)
async def query(q: str = Form(...), k: int = Form(4)):
    q_text = q.strip()
    if not q_text:
        raise HTTPException(status_code=400, detail="Query is empty")

    try:
        return await RagService.query(q_text, k)
    except Exception as e:
        logger.error(f"Query failed: {e}")
        # Return a polite error or re-raise
        raise HTTPException(status_code=502, detail="Query generation failed")


@router.get("/list_files")
async def list_files():
    try:
        # This logic remains largely the same, but could be moved to ChromaStore/RagService if needed.
        # Keeping it here for now as it's a simple DB read.
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
            for md in metadatas:
                # Assuming id structure or just relying on metadata filter if delete supports it
                # Logic from original file relied on reconstructing IDs which is brittle but...
                # let's try to find IDs from data directly if possible?
                # The original code reconstructed IDs: f"{Path(name).stem}::chunk_{md.get('chunk_index')}"
                # Let's stick to original logic for safety, but wrapped in try/except
                if md.get("source") == name:
                     ids.append(f"{Path(name).stem}::chunk_{md.get('chunk_index')}")

            if ids:
                collection.delete(ids=ids)
                total_deleted += len(ids)

        # File system delete
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
