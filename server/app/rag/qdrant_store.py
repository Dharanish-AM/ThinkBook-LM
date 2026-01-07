from typing import List, Dict, Any, Optional
import logging
import json
import os
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.http import models
import uuid
from ..core.config import QDRANT_DIR, QDRANT_URL, QDRANT_API_KEY

logger = logging.getLogger(__name__)

_COLLECTION_NAME = "thinkbook"
_VECTOR_SIZE = 384  # Dimension for all-MiniLM-L6-v2
_REGISTRY_PATH = Path(QDRANT_DIR) / "file_registry.json"

def get_client() -> QdrantClient:
    """
    Returns a QdrantClient instance.
    - If QDRANT_URL is set, connects to that (Docker/Cloud).
    - Otherwise, uses local disk mode at QDRANT_DIR.
    """
    if QDRANT_URL:
        logger.info(f"Connecting to Qdrant at {QDRANT_URL}")
        return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    
    logger.info(f"Using Qdrant Local Mode (SQLite) at {QDRANT_DIR}")
    return QdrantClient(path=str(QDRANT_DIR))

# Singleton client
_client = get_client()

def _ensure_collection():
    """Ensures the collection exists with correct config."""
    collections = _client.get_collections().collections
    exists = any(c.name == _COLLECTION_NAME for c in collections)
    
    if not exists:
        logger.info(f"Creating Qdrant collection '{_COLLECTION_NAME}'")
        _client.create_collection(
            collection_name=_COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=_VECTOR_SIZE,
                distance=models.Distance.COSINE
            )
        )
        # Create Payload Index for 'source' to speed up deletions/filtering
        _client.create_payload_index(
            collection_name=_COLLECTION_NAME,
            field_name="source",
            field_schema=models.PayloadSchemaType.KEYWORD
        )

# Initialize collection on module load (or lazily)
_ensure_collection()

# --- File Registry Helpers ---

def _load_registry() -> Dict[str, int]:
    if not _REGISTRY_PATH.exists():
        return {}
    try:
        with open(_REGISTRY_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load registry: {e}")
        return {}

def _save_registry(registry: Dict[str, int]):
    try:
        # Ensure parent dir exists
        _REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(_REGISTRY_PATH, "w") as f:
            json.dump(registry, f)
    except Exception as e:
        logger.error(f"Failed to save registry: {e}")

def _update_registry_add(filename: str, chunk_count: int):
    registry = _load_registry()
    registry[filename] = chunk_count
    _save_registry(registry)

def _remove_from_registry(filename: str):
    registry = _load_registry()
    if filename in registry:
        del registry[filename]
        _save_registry(registry)

# --- Main Store Functions ---

def add_documents(
    ids: List[str], documents: List[str], embeddings, metadatas: List[Dict[str, Any]]
):
    points = []
    # Assumes all docs in this batch belong to the same file for registry purposes
    # But strictly we should check.
    # In RagService, we process one file at a time, so taking the first metadata source is safe.
    current_file = metadatas[0].get("source") if metadatas else "unknown"

    for i, _id in enumerate(ids):
        # embeddings[i] might be numpy array
        vector = embeddings[i].tolist() if hasattr(embeddings[i], "tolist") else embeddings[i]
        
        # Combine document text into metadata ("page_content" is standard convention, or just keep "text")
        # Chroma kept document separate, Qdrant stores it in payload
        payload = metadatas[i].copy()
        payload["document"] = documents[i]
        
        # Convert string ID to deterministic UUID for Qdrant compatibility
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, _id))
        
        points.append(models.PointStruct(
            id=point_id, 
             vector=vector,
            payload=payload
        ))
    
    _client.upsert(
        collection_name=_COLLECTION_NAME,
        points=points
    )
    
    if current_file != "unknown":
        _update_registry_add(current_file, len(ids))
        
    logger.info("Added %d documents to Qdrant collection for %s", len(ids), current_file)

def query_embeddings(embedding, n_results: int = 4):
    query_vector = embedding.tolist() if hasattr(embedding, "tolist") else embedding
    
    search_result = _client.query_points(
        collection_name=_COLLECTION_NAME,
        query=query_vector,
        limit=n_results,
        with_payload=True
    ).points
    
    documents = []
    metadatas = []
    distances = []
    
    for hit in search_result:
        # Reconstruct format expected by service (Chroma-like)
        payload = hit.payload or {}
        doc = payload.get("document", "")
        # Remove document from metadata to avoid duplication in return if desired, 
        # but for now keep it consistent with what existing code expects (metadata separte)
        meta = {k: v for k, v in payload.items() if k != "document"}
        
        documents.append(doc)
        metadatas.append(meta)
        distances.append(hit.score)
    
    # Return structure matching what RagService expects (flat lists for single query)
    return {
        "documents": documents, 
        "metadatas": metadatas,
        "distances": distances
    }

def get_collection_count():
    return _client.count(collection_name=_COLLECTION_NAME).count

def delete_file(filename: str) -> int:
    """
    Deletes all points associated with a specific source file.
    Returns number of deleted points (not always exact in Qdrant delete-by-filter, but success implies it).
    """
    # First count how many for reporting (optional, extra query)
    # Using Filter
    file_filter = models.Filter(
        must=[
            models.FieldCondition(
                key="source",
                match=models.MatchValue(value=filename)
            )
        ]
    )
    
    # Count before delete
    count = _client.count(collection_name=_COLLECTION_NAME, count_filter=file_filter).count
    
    if count > 0:
        _client.delete(
            collection_name=_COLLECTION_NAME,
            points_selector=models.FilterSelector(filter=file_filter)
        )
        logger.info(f"Deleted {count} chunks for file {filename}")
        
    # Always try to remove from registry even if db count is 0 (cleanup)
    _remove_from_registry(filename)
        
    return count

def list_files_with_counts() -> List[Dict[str, Any]]:
    """
    Aggregates unique files and their chunk counts.
    Always validates against actual Qdrant database to ensure consistency.
    """
    # Always scan the actual database to ensure accuracy
    file_counts = {}
    
    offset = None
    while True:
        points, next_offset = _client.scroll(
            collection_name=_COLLECTION_NAME,
            scroll_filter=None,
            limit=1000,
            with_payload=["source"],
            with_vectors=False,
            offset=offset
        )
        
        for p in points:
            src = p.payload.get("source")
            if src:
                file_counts[src] = file_counts.get(src, 0) + 1
        
        offset = next_offset
        if offset is None:
            break
    
    # Sync registry with actual database state
    _save_registry(file_counts)
            
    return [{"name": k, "chunks": v} for k, v in file_counts.items()]
