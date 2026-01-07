from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class UploadResponse(BaseModel):
    """Response model for file upload endpoint."""
    status: str = Field(..., description="Status of the upload operation", example="ok")
    file: str = Field(..., description="Name of the uploaded file", example="document.pdf")
    chunks: int = Field(..., description="Number of text chunks created", example=42)
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "file": "research_paper.pdf",
                "chunks": 15
            }
        }


class QueryResponse(BaseModel):
    """Response model for non-streaming query endpoint."""
    answer: str = Field(..., description="Generated answer based on retrieved documents")
    sources: List[Dict[str, Any]] = Field(..., description="Metadata of source documents used")
    raw_retrieval: List[str] = Field(..., description="Raw text chunks retrieved from vector DB")
    duration: Optional[float] = Field(None, description="Query processing time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Based on the documents, the main topic is...",
                "sources": [
                    {"source": "document.pdf", "chunk_index": 0},
                    {"source": "document.pdf", "chunk_index": 3}
                ],
                "raw_retrieval": ["First relevant chunk...", "Second relevant chunk..."],
                "duration": 2.45
            }
        }


class FileInfo(BaseModel):
    """Information about an indexed file."""
    name: str = Field(..., description="Filename", example="document.pdf")
    chunks: int = Field(..., description="Number of chunks indexed", example=10)


class DeleteResponse(BaseModel):
    """Response model for file deletion endpoint."""
    status: str = Field(..., example="ok")
    deleted_file: str = Field(..., description="Name of deleted file")
    deleted_chunks: int = Field(..., description="Number of chunks removed from index")
