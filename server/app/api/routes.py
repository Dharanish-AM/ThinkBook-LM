import logging
import asyncio
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import StreamingResponse

from typing import List

from ..core.utils import write_upload_bytes
from ..core.security import validate_upload_file, FileValidationError
from ..parsers import extract_text_auto
from ..rag.qdrant_store import list_files_with_counts, delete_file as delete_file_qdrant
from ..core.config import UPLOAD_DIR
from ..services.rag_service import RagService
from .models import UploadResponse, QueryResponse, FileInfo, DeleteResponse

router = APIRouter(tags=["ThinkBook LM"])
logger = logging.getLogger(__name__)

@router.get("/health", summary="Health check", description="Check if the API service is running")
async def health_check():
    """Check API health and service availability."""
    return {"status": "ok", "service": "thinkbook-server (Qdrant)"}


@router.post(
    "/upload_file", 
    response_model=UploadResponse,
    summary="Upload and index a document",
    description="""
    Upload a document file for indexing in the knowledge base.
    
    **Supported Formats:**
    - Documents: PDF, DOCX, TXT
    - Images: PNG, JPG (OCR)
    - Audio: WAV, MP3 (transcription)
    - Video: MP4 (transcription)
    
    **Validation:**
    - Max file size: 50MB
    - MIME type verification
    - Extension whitelist
    - Filename sanitization
    
    **Process:**
    1. Validates file size and type
    2. Extracts text content
    3. Chunks text into semantic segments
    4. Generates embeddings
    5. Stores in vector database
    """,
    responses={
        200: {
            "description": "File successfully uploaded and indexed",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ok",
                        "file": "research.pdf",
                        "chunks": 25
                    }
                }
            }
        },
        400: {"description": "Invalid file (wrong type, too large, or empty)"},
        409: {"description": "File already exists"},
        500: {"description": "Internal processing error"}
    }
)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and index a document file.
    
    Validates file size, MIME type, and extension before processing.
    Supports: PDF, DOCX, TXT, Images (PNG/JPG), Audio (WAV/MP3), Video (MP4)
    """
    original_filename = file.filename
    if not original_filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    saved_path = None
    
    try:
        # Read file content
        content = await file.read()
        
        # Validate file (size, MIME type, extension, sanitize filename)
        safe_filename, mime_type = validate_upload_file(content, original_filename)
        saved_path = UPLOAD_DIR / safe_filename
        
        # Check for duplicate filename
        if saved_path.exists():
            raise HTTPException(
                status_code=409, 
                detail=f"File '{safe_filename}' already exists. Please rename or delete the existing file first."
            )
        
        # Save to file system
        write_upload_bytes(content, UPLOAD_DIR, safe_filename)
        logger.info(f"File saved: {safe_filename} ({mime_type})")
        
        # Extract text using parser registry
        text = extract_text_auto(saved_path)
        if not text or not text.strip():
            logger.warning(f"No text extracted from file {safe_filename}")
            if saved_path.exists():
                saved_path.unlink()
            raise HTTPException(
                status_code=400, 
                detail="No text extracted from file. File might be empty or unsupported."
            )
        
        # Process and index document
        result = await RagService.process_document(text, safe_filename)
        return result
        
    except FileValidationError as fve:
        # File validation failed
        logger.warning(f"File validation failed for {original_filename}: {fve}")
        if saved_path and saved_path.exists():
            saved_path.unlink()
        raise HTTPException(status_code=400, detail=str(fve))
        
    except HTTPException:
        # Re-raise HTTP exceptions without wrapping
        if saved_path and saved_path.exists():
            saved_path.unlink()
        raise
        
    except ValueError as ve:
        # Processing error
        logger.error(f"Processing error for {original_filename}: {ve}")
        if saved_path and saved_path.exists():
            saved_path.unlink()
        raise HTTPException(status_code=500, detail=str(ve))
        
    except Exception as e:
        # Unexpected error
        logger.error(f"Upload failed for {original_filename}: {e}")
        if saved_path and saved_path.exists():
            saved_path.unlink()
        raise HTTPException(status_code=500, detail="Internal processing error")


@router.post(
    "/query", 
    response_model=QueryResponse,
    summary="Query documents (non-streaming)",
    description="""
    Query the indexed knowledge base and get a complete answer.
    
    Uses RAG (Retrieval-Augmented Generation):
    1. Embeds your query
    2. Retrieves top-k relevant chunks
    3. Generates comprehensive answer using LLM
    
    **Parameters:**
    - `q`: Your question or query
    - `k`: Number of document chunks to retrieve (default: 4)
    
    **Returns:** Complete answer with sources and metadata
    """,
    responses={
        200: {"description": "Query successful"},
        400: {"description": "Empty query"},
        502: {"description": "LLM generation failed"}
    }
)
async def query(q: str = Form(..., description="Query text"), k: int = Form(4, description="Number of chunks to retrieve")):
    """
    Query the document knowledge base (non-streaming).
    
    Returns complete response after generation finishes.
    """
    q_text = q.strip()
    if not q_text:
        raise HTTPException(status_code=400, detail="Query is empty")

    try:
        return await RagService.query(q_text, k)
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=502, detail="Query generation failed")


@router.post(
    "/query_stream",
    summary="Query documents (streaming)",
    description="""
    Query the knowledge base with real-time streaming response.
    
    Returns Server-Sent Events (SSE) for progressive answer display.
    
    **Event Types:**
    - `sources`: Document sources used
    - `answer`: Text chunks as they're generated
    - `done`: Completion signal with duration
    
    **Example Client:**
    ```javascript
    const formData = new FormData();
    formData.append('q', 'What is...?');
    
    const response = await fetch('/api/query_stream', {
        method: 'POST',
        body: formData
    });
    
    const reader = response.body.getReader();
    // Read stream...
    ```
    """,
    responses={
        200: {
            "description": "Streaming response",
            "content": {"text/event-stream": {}}
        },
        400: {"description": "Empty query"},
        502: {"description": "LLM generation failed"}
    }
)
async def query(q: str = Form(...), k: int = Form(4)):
    """
    Query the document knowledge base (non-streaming).
    
    Returns complete response after generation finishes.
    """
    q_text = q.strip()
    if not q_text:
        raise HTTPException(status_code=400, detail="Query is empty")

    try:
        return await RagService.query(q_text, k)
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=502, detail="Query generation failed")


@router.post("/query_stream")
async def query_stream(q: str = Form(...), k: int = Form(4)):
    """
    Query the document knowledge base with streaming response.
    
    Returns Server-Sent Events (SSE) for real-time token streaming.
    """
    q_text = q.strip()
    if not q_text:
        raise HTTPException(status_code=400, detail="Query is empty")

    try:
        async def generate():
            async for chunk in RagService.query_stream(q_text, k):
                yield f"data: {chunk}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    except Exception as e:
        logger.error(f"Streaming query failed: {e}")
        raise HTTPException(status_code=502, detail="Query generation failed")


@router.get(
    "/list_files",
    response_model=List[FileInfo],
    summary="List indexed files",
    description="Get a list of all files currently indexed in the knowledge base with chunk counts."
)
async def list_files():
    """List all indexed files with metadata."""
    try:
        return list_files_with_counts()
    except Exception as e:
        logger.error("Failed to list files: %s", e)
        raise HTTPException(status_code=500, detail="Failed to list files")


@router.delete(
    "/delete_file",
    response_model=DeleteResponse,
    summary="Delete a file",
    description="""
    Remove a file from both the vector database and filesystem.
    
    **Parameters:**
    - `name`: Exact filename to delete
    
    **Warning:** This operation is irreversible.
    """
)
async def delete_file(name: str = Form(..., description="Filename to delete")):
    """Delete a file from the knowledge base and filesystem."""
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
