"""Unit tests for security validation functions."""

import pytest
from app.core.security import (
    validate_file_size,
    validate_file_extension,
    sanitize_filename,
    FileValidationError,
)
from app.core.config import MAX_FILE_SIZE_BYTES, ALLOWED_EXTENSIONS


class TestFileValidation:
    """Tests for file validation functions."""
    
    def test_validate_file_size_valid(self):
        """Test validation with file under size limit."""
        file_size = 1024 * 1024  # 1MB
        # Should not raise exception
        validate_file_size(file_size)
    
    def test_validate_file_size_at_limit(self):
        """Test validation with file at exact size limit."""
        file_size = MAX_FILE_SIZE_BYTES
        # Should not raise exception
        validate_file_size(file_size)
    
    def test_validate_file_size_over_limit(self):
        """Test validation with file over size limit."""
        file_size = MAX_FILE_SIZE_BYTES + 1
        with pytest.raises(FileValidationError) as exc_info:
            validate_file_size(file_size)
        assert "exceeds maximum allowed size" in str(exc_info.value)
    
    def test_validate_extension_valid_txt(self):
        """Test validation with valid .txt extension."""
        # Should not raise exception
        validate_file_extension("document.txt")
    
    def test_validate_extension_valid_pdf(self):
        """Test validation with valid .pdf extension."""
        # Should not raise exception
        validate_file_extension("document.pdf")
    
    def test_validate_extension_invalid(self):
        """Test validation with invalid extension."""
        with pytest.raises(FileValidationError) as exc_info:
            validate_file_extension("document.exe")
        assert "not supported" in str(exc_info.value)
    
    def test_validate_extension_case_insensitive(self):
        """Test that extension validation is case-insensitive."""
        # Should not raise exception for uppercase extensions
        validate_file_extension("document.PDF")
        validate_file_extension("document.TXT")
    
    def test_sanitize_filename_simple(self):
        """Test sanitizing a simple filename."""
        filename = "document.pdf"
        result = sanitize_filename(filename)
        assert result == "document.pdf"
    
    def test_sanitize_filename_with_path(self):
        """Test sanitizing filename with path (should extract just filename)."""
        filename = "/path/to/document.pdf"
        result = sanitize_filename(filename)
        assert result == "document.pdf"
    
    def test_sanitize_filename_path_traversal(self):
        """Test sanitizing filename with path traversal attempt."""
        filename = "../../../etc/passwd"
        result = sanitize_filename(filename)
        assert ".." not in result
        assert "/" not in result
    
    def test_sanitize_filename_backslashes(self):
        """Test sanitizing filename with backslashes (Windows paths)."""
        filename = "C:\\Users\\test\\document.pdf"
        result = sanitize_filename(filename)
        assert "\\" not in result
        assert result == "document.pdf"
    
    def test_sanitize_filename_empty(self):
        """Test sanitizing empty filename (should raise error)."""
        with pytest.raises(FileValidationError):
            sanitize_filename("")
    
    def test_sanitize_filename_only_dangerous_chars(self):
        """Test sanitizing filename with only dangerous characters."""
        with pytest.raises(FileValidationError):
            sanitize_filename("../../")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
