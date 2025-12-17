from typing import List
from ..core.config import CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS
import logging

logger = logging.getLogger(__name__)

try:
    import tiktoken

    _TIKTOKEN_AVAILABLE = True
except Exception:
    _TIKTOKEN_AVAILABLE = False
    logger.info("tiktoken not available; falling back to character-based chunking.")


def chunk_text_tokenwise(text: str, chunk_size: int, overlap: int) -> List[str]:
    
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    chunks = []
    start = 0
    n = len(tokens)
    while start < n:
        end = min(start + chunk_size, n)
        chunk_tokens = tokens[start:end]
        chunk_text = enc.decode(chunk_tokens)
        chunks.append(chunk_text)
        if end >= n:
            break
        start = max(end - overlap, end - overlap)
    return chunks


def chunk_text_charwise(
    text: str, chunk_size_chars: int = 3000, overlap_chars: int = 500
) -> List[str]:
    chunks = []
    n = len(text)
    start = 0
    while start < n:
        end = min(start + chunk_size_chars, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:
            break
        start = max(end - overlap_chars, end - overlap_chars)
    return chunks


def chunk_text(text: str):
    """
    Attempts token-aware chunking, defaults to character chunking.
    Sizes come from config.
    """
    if _TIKTOKEN_AVAILABLE:
        try:
            return chunk_text_tokenwise(text, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS)
        except Exception as e:
            logger.warning("Tokenwise chunking failed, fallback: %s", e)
    
    chunk_chars = int(CHUNK_SIZE_TOKENS * 4)
    overlap_chars = int(CHUNK_OVERLAP_TOKENS * 4)
    return chunk_text_charwise(text, chunk_chars, overlap_chars)
