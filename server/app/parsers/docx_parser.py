from pathlib import Path
import docx
from .base import BaseParser
from .registry import ParserRegistry

@ParserRegistry.register(".docx")
@ParserRegistry.register(".doc")
class DocxParser(BaseParser):
    def parse(self, file_path: Path) -> str:
        try:
            doc = docx.Document(str(file_path))
            paragraphs = [p.text for p in doc.paragraphs if p.text]
            return "\n".join(paragraphs)
        except Exception:
            return ""
