import requests
import logging
from .config import OLLAMA_URL, OLLAMA_MODEL

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 120

def generate_from_prompt(prompt: str, max_tokens: int = 512, temperature: float = 0.0):
    """
    Calls Ollama HTTP generate endpoint.
    Adapt payload if Ollama API differs in your version.
    Returns text string (concatenated).
    """
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.post(OLLAMA_URL, json=payload, headers=headers, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        # Common shapes:
        # {"id": ..., "generated": [{"text": "..."}]}
        if isinstance(data, dict) and "generated" in data:
            texts = [g.get("text", "") for g in data["generated"]]
            return "".join(texts)
        # Fallback: check "text" top-level or raw string
        if isinstance(data, dict) and "text" in data:
            return data["text"]
        return str(data)
    except requests.RequestException as e:
        logger.error("Ollama request failed: %s", e)
        raise