from .registry import ParserRegistry
# Import parsers to ensure registration
from .pdf_parser import PDFParser
from .docx_parser import DocxParser
from .text_parser import TextParser
from .image_parser import ImageParser
from .audio_parser import AudioParser
from .video_parser import VideoParser

def extract_text_auto(file_path):
    parser = ParserRegistry.get_parser(file_path)
    if parser:
        return parser.parse(file_path)
    # Fallback to text parser if no specific match, or raise error?
    # For now, let's try text parser as generic fallback or return empty
    return ""
