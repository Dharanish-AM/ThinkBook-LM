from pathlib import Path
from PIL import Image
import pytesseract
from .base import BaseParser
from .registry import ParserRegistry

@ParserRegistry.register(".jpg")
@ParserRegistry.register(".jpeg")
@ParserRegistry.register(".png")
class ImageParser(BaseParser):
    def parse(self, file_path: Path) -> str:
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text
        except ImportError:
            return "OCR library (pytesseract) or Tesseract binary not found."
        except Exception as e:
            return f"Error processing image: {str(e)}"
