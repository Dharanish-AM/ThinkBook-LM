import logging
import os
from pathlib import Path
from moviepy.editor import VideoFileClip
from .base import BaseParser
from .registry import ParserRegistry
from .audio_parser import get_whisper_model

logger = logging.getLogger(__name__)

@ParserRegistry.register(".mp4")
@ParserRegistry.register(".mov")
@ParserRegistry.register(".avi")
@ParserRegistry.register(".mkv")
class VideoParser(BaseParser):
    def parse(self, file_path: Path) -> str:
        temp_audio_path = file_path.with_suffix(".temp.wav")
        try:
            # Extract audio
            video = VideoFileClip(str(file_path))
            if not video.audio:
                return "Video has no audio track."
            
            logger.info(f"Extracting audio from video {file_path}...")
            video.audio.write_audiofile(str(temp_audio_path), verbose=False, logger=None)
            video.close() # Close to release file handle

            # Transcribe using shared Whisper model
            model = get_whisper_model()
            result = model.transcribe(str(temp_audio_path))
            text = result.get("text", "")
            
            return text

        except Exception as e:
            logger.error(f"Error processing video {file_path}: {e}")
            return f"Error processing video: {str(e)}"
        finally:
            # Cleanup temp file
            if temp_audio_path.exists():
                temp_audio_path.unlink()
