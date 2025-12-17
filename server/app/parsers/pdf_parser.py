from pathlib import Path
from PyPDF2 import PdfReader
from .base import BaseParser
from .registry import ParserRegistry

@ParserRegistry.register(".pdf")
class PDFParser(BaseParser):
    def parse(self, file_path: Path) -> str:
        texts = []
        try:
            reader = PdfReader(str(file_path))
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    texts.append(text)
        except Exception:
            return " ".join(texts)
        return "\n".join(texts)
