import logging
import asyncio
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Form

from ..core.utils import write_upload_bytes
from ..parsers import extract_text_auto
from ..rag.qdrant_store import list_files_with_counts, delete_file as delete_file_qdrant
from ..core.config import UPLOAD_DIR
from ..services.rag_service import RagService
from .models import UploadResponse, QueryResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "thinkbook-server (Qdrant)"}


@router.post("/upload_file", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename
    saved_path = UPLOAD_DIR / filename
    
    try:
        content = await file.read()
        # Save to file system first
        write_upload_bytes(content, UPLOAD_DIR, filename)
        
        # Using the new Parser Registry indirectly via extract_text_auto
        text = extract_text_auto(saved_path)
        if not text or not text.strip():
            logger.warning("No text extracted from file %s", filename)
            # Cleanup invalid file
            if saved_path.exists():
                saved_path.unlink()
            raise HTTPException(status_code=400, detail="No text extracted from file. File type might not be supported or file is empty.")
        
        # Delegate processing to RagService
        result = await RagService.process_document(text, filename)
        return result
        
    except ValueError as ve:
         # Cleanup on error
         if saved_path.exists():
             saved_path.unlink()
         raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        # Cleanup on error
        if saved_path.exists():
            saved_path.unlink()
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
        raise HTTPException(status_code=502, detail="Query generation failed")


@router.get("/list_files")
async def list_files():
    try:
        return list_files_with_counts()
    except Exception as e:
        logger.error("Failed to list files: %s", e)
        raise HTTPException(status_code=500, detail="Failed to list files")


@router.delete("/delete_file")
async def delete_file(name: str):
    try:
        # Delete from Vector DB
        deleted_count = delete_file_qdrant(name)

        # File system delete
        file_path = UPLOAD_DIR / name
        if file_path.exists():
            file_path.unlink()

        if deleted_count == 0 and not file_path.exists():
            raise HTTPException(
                status_code=404, detail=f"No data found for file {name}"
            )

        return {"status": "ok", "deleted_file": name, "deleted_chunks": deleted_count}

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
