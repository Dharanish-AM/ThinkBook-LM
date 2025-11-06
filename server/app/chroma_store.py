from typing import List, Dict, Any
import chromadb
from .config import CHROMA_DIR
import logging

logger = logging.getLogger(__name__)


_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
_COLLECTION_NAME = "thinkbook"


def _get_or_create_collection():
    return _client.get_or_create_collection(
        name=_COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )


def add_documents(
    ids: List[str], documents: List[str], embeddings, metadatas: List[Dict[str, Any]]
):
    coll = _get_or_create_collection()
    
    emb_list = [e.tolist() if hasattr(e, "tolist") else e for e in embeddings]
    coll.add(ids=ids, documents=documents, embeddings=emb_list, metadatas=metadatas)
    logger.info("Added %d documents to chroma collection", len(ids))


def query_embeddings(embedding, n_results: int = 4):
    coll = _get_or_create_collection()
    res = coll.query(
        query_embeddings=[
            embedding.tolist() if hasattr(embedding, "tolist") else embedding
        ],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )
    
    if res and isinstance(res, dict):
        return {
            "documents": res.get("documents", [[]])[0] if res.get("documents") else [],
            "metadatas": res.get("metadatas", [[]])[0] if res.get("metadatas") else [],
            "distances": res.get("distances", [[]])[0] if res.get("distances") else [],
        }
    return {"documents": [], "metadatas": [], "distances": []}
