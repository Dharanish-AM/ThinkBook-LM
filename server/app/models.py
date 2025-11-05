from pydantic import BaseModel
from typing import List, Dict, Any

class UploadResponse(BaseModel):
    status: str
    file: str
    chunks: int

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    raw_retrieval: List[str]