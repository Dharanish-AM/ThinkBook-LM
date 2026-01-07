import logging
import json
import requests
from typing import Optional, Dict, Any, Iterator
from ..core.config import OLLAMA_URL, OLLAMA_MODEL, MAX_TOKENS, TEMPERATURE

logger = logging.getLogger(__name__)

class LLMService:
    """Service to interact with the LLM provider (Ollama)."""

    @staticmethod
    def generate(prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text from the LLM (non-streaming).
        
        Args:
            prompt: The user query or compiled prompt.
            system_prompt: Optional system instruction.
            
        Returns:
            str: The generated text.
        """
        full_prompt = prompt
        if system_prompt:
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
    def generate_stream(prompt: str, system_prompt: Optional[str] = None) -> Iterator[str]:
        """
        Generate text from the LLM with streaming response.
        
        Args:
            prompt: The user query or compiled prompt.
            system_prompt: Optional system instruction.
            
        Yields:
            str: Chunks of generated text.
        """
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        payload = {
            "model": OLLAMA_MODEL,
            "prompt": full_prompt,
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
            "stream": True
        }
        
        try:
            response = requests.post(
                OLLAMA_URL, 
                json=payload, 
                timeout=120, 
                stream=True
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        
                        # Extract response chunk
                        if "response" in data:
                            chunk = data["response"]
                            if chunk:
                                yield chunk
                        
                        # Check if done
                        if data.get("done", False):
                            break
                            
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse streaming response: {line}")
                        continue
                        
        except requests.RequestException as e:
            logger.error(f"LLM streaming request failed: {e}")
            raise Exception("Failed to generate streaming response from LLM") from e

    @staticmethod
    def _parse_response(data: Dict[str, Any]) -> str:
        """Parse the Ollama response to extract the text."""
        # Handle various Ollama response formats/versions
        if "response" in data:
            return data["response"]
        if "message" in data and "content" in data["message"]:
            return data["message"]["content"]
        return str(data)  # Fallback
