from sentence_transformers import SentenceTransformer
import numpy as np
from .config import EMBEDDING_MODEL
import threading
import torch

_model = None
_model_lock = threading.Lock()

def get_embedding_model():
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                # Select device: MPS for Mac GPU, fallback to CPU
                device = "mps" if torch.backends.mps.is_available() else "cpu"
                _model = SentenceTransformer(EMBEDDING_MODEL, device=device)
    return _model

def embed_texts(texts):
    """
    Returns numpy array embeddings (n, dim)
    """
    model = get_embedding_model()
    embs = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return embs