from abc import ABC, abstractmethod
from pathlib import Path

class BaseParser(ABC):
    """Abstract base class for all file parsers."""

    @abstractmethod
    def parse(self, file_path: Path) -> str:
        """
        Parse the file at the given path and return the extracted text.
        
        Args:
            file_path (Path): Path to the file to parse.
            
        Returns:
            str: The extracted text content.
            
        Raises:
            Exception: If parsing fails.
        """
        pass
