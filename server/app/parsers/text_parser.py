from pathlib import Path
from .base import BaseParser
from .registry import ParserRegistry
from ..core.utils import read_file_text

@ParserRegistry.register(".txt")
@ParserRegistry.register(".md")
class TextParser(BaseParser):
    def parse(self, file_path: Path) -> str:
        return read_file_text(file_path)
