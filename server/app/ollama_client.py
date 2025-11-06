import requests
import logging
import json
from .config import OLLAMA_URL, OLLAMA_MODEL

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 120


def generate_from_prompt(prompt: str, max_tokens: int = 512, temperature: float = 0.0):
    """
    Supports both /api/generate (stream JSON) and /api/chat (stream chunks).
    Concatenates streamed text safely.
    """
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": True,
    }
    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.post(
            OLLAMA_URL,
            json=payload,
            headers=headers,
            stream=True,
            timeout=DEFAULT_TIMEOUT,
        )
        resp.raise_for_status()

        response_text = ""
        for line in resp.iter_lines():
            if not line:
                continue
            try:
                chunk = line.decode("utf-8")
                try:
                    j = json.loads(chunk)
                    if isinstance(j, dict):
                        if (
                            "message" in j
                            and isinstance(j["message"], dict)
                            and "content" in j["message"]
                        ):
                            response_text += j["message"]["content"]
                        elif "response" in j:
                            response_text += j["response"]
                        elif "text" in j:
                            response_text += j["text"]
                        elif "content" in j:
                            response_text += j["content"]
                    else:
                        response_text += chunk
                except Exception:
                    response_text += chunk
            except Exception:
                continue

        return response_text.strip()
    except requests.RequestException as e:
        logger.error("Ollama request failed: %s", e)
        raise
