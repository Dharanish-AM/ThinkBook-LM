"""Unit tests for file parsers."""

import pytest
from pathlib import Path
from app.parsers.text_parser import TextParser
from app.parsers.pdf_parser import PDFParser
from app.parsers.docx_parser import DocxParser
from app.parsers.registry import ParserRegistry


class TestTextParser:
    """Tests for TextParser."""
    
    def test_parse_valid_text_file(self, tmp_path):
        """Test parsing a valid text file."""
        test_file = tmp_path / "test.txt"
        test_content = "Hello, this is a test file.\nWith multiple lines."
        test_file.write_text(test_content)
        
        parser = TextParser()
        result = parser.parse(test_file)
        
        assert result == test_content
    
    def test_parse_empty_text_file(self, tmp_path):
        """Test parsing an empty text file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")
        
        parser = TextParser()
        result = parser.parse(test_file)
        
        assert result == ""
    
    def test_parse_unicode_text_file(self, tmp_path):
        """Test parsing text file with unicode characters."""
        test_file = tmp_path / "unicode.txt"
        test_content = "Hello 世界 🌍"
        test_file.write_text(test_content, encoding='utf-8')
        
        parser = TextParser()
        result = parser.parse(test_file)
        
        assert result == test_content


class TestParserRegistry:
    """Tests for ParserRegistry."""
    
    def test_get_parser_for_txt(self):
        """Test getting parser for .txt extension."""
        parser = ParserRegistry.get_parser(Path("test.txt"))
        assert parser is not None
        assert isinstance(parser, TextParser)
    
    def test_get_parser_for_pdf(self):
        """Test getting parser for .pdf extension."""
        parser = ParserRegistry.get_parser(Path("test.pdf"))
        assert parser is not None
        assert isinstance(parser, PDFParser)
    
    def test_get_parser_for_docx(self):
        """Test getting parser for .docx extension."""
        parser = ParserRegistry.get_parser(Path("test.docx"))
        assert parser is not None
        assert isinstance(parser, DocxParser)
    
    def test_get_parser_for_unsupported_extension(self):
        """Test getting parser for unsupported extension."""
        parser = ParserRegistry.get_parser(Path("test.xyz"))
        assert parser is None
    
    def test_supported_extensions(self):
        """Test getting list of supported extensions."""
        extensions = ParserRegistry.supported_extensions()
        assert isinstance(extensions, list)
        assert ".txt" in extensions
        assert ".pdf" in extensions
        assert ".docx" in extensions


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
