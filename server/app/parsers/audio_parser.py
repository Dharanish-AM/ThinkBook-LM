import logging
from pathlib import Path
import whisper
from .base import BaseParser
from .registry import ParserRegistry

logger = logging.getLogger(__name__)

# Global model cache to avoid reloading
_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        logger.info("Loading Whisper model (base)...")
        # 'base' is a good trade-off for CPU inference; 'tiny' is faster but less accurate.
        _whisper_model = whisper.load_model("base")
    return _whisper_model

@ParserRegistry.register(".mp3")
@ParserRegistry.register(".wav")
@ParserRegistry.register(".m4a")
class AudioParser(BaseParser):
    def parse(self, file_path: Path) -> str:
        try:
            model = get_whisper_model()
            result = model.transcribe(str(file_path))
            return result.get("text", "")
        except Exception as e:
            logger.error(f"Error transcribing audio {file_path}: {e}")
            return f"Error transcribing audio: {str(e)}"
