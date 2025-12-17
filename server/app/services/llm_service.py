import logging
import json
import requests
from typing import Optional, Dict, Any
from ..core.config import OLLAMA_URL, OLLAMA_MODEL, MAX_TOKENS, TEMPERATURE

logger = logging.getLogger(__name__)

class LLMService:
    """Service to interact with the LLM provider (Ollama)."""

    @staticmethod
    def generate(prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text from the LLM.
        
        Args:
            prompt: The user query or compiled prompt.
            system_prompt: Optional system instruction.
            
        Returns:
            str: The generated text.
        """
        full_prompt = prompt
        if system_prompt:
            # Simple concatenation for models that don't need specific chat template formatting here
            # or rely on Ollama's modelfile.
            full_prompt = f"{system_prompt}\n\n{prompt}"

        payload = {
            "model": OLLAMA_MODEL,
            "prompt": full_prompt,
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
            "stream": False
        }
        
        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=60)
            response.raise_for_status()
            return LLMService._parse_response(response.json())
        except requests.RequestException as e:
            logger.error(f"LLM request failed: {e}")
            raise Exception("Failed to generate response from LLM") from e

    @staticmethod
    def _parse_response(data: Dict[str, Any]) -> str:
        """Parse the Ollama response to extract the text."""
        # Handle various Ollama response formats/versions
        if "response" in data:
            return data["response"]
        if "message" in data and "content" in data["message"]:
            return data["message"]["content"]
        return str(data)  # Fallback
