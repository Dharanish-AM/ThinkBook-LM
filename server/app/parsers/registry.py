import logging
import mimetypes
from pathlib import Path
from typing import Dict, Type, Optional
from .base import BaseParser

logger = logging.getLogger(__name__)

class ParserRegistry:
    """Registry to manage and retrieve parsers based on file extensions/mimetypes."""
    
    _parsers: Dict[str, Type[BaseParser]] = {}

    @classmethod
    def register(cls, extension: str):
        """Decorator to register a parser for a specific file extension (e.g., '.pdf')."""
        def wrapper(parser_cls: Type[BaseParser]):
            cls._parsers[extension.lower()] = parser_cls
            return parser_cls
        return wrapper

    @classmethod
    def get_parser(cls, file_path: Path) -> Optional[BaseParser]:
        """
        Returns an instance of the appropriate parser for the given file.
        
        Args:
            file_path (Path): The file to find a parser for.
            
        Returns:
            Optional[BaseParser]: An instance of the matching parser, or None if not found.
        """
        ext = file_path.suffix.lower()
        parser_cls = cls._parsers.get(ext)
        
        if not parser_cls:
            logger.warning(f"No parser registered for extension: {ext}")
            return None
            
        return parser_cls()

    @classmethod
    def supported_extensions(cls):
        return list(cls._parsers.keys())
