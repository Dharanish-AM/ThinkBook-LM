"""Security utilities for file validation and sanitization."""

import logging
from pathlib import Path
from typing import Optional

from .config import MAX_FILE_SIZE_BYTES, ALLOWED_MIME_TYPES, ALLOWED_EXTENSIONS

logger = logging.getLogger(__name__)

# Try to import python-magic, but gracefully degrade if not available
try:
    import magic
    MAGIC_AVAILABLE = True
    logger.info("python-magic loaded successfully - MIME validation enabled")
except (ImportError, OSError) as e:
    MAGIC_AVAILABLE = False
    logger.warning(f"python-magic not available ({e}). MIME validation will be skipped. Install with: brew install libmagic")


class FileValidationError(Exception):
    """Custom exception for file validation errors."""
    pass


def validate_file_size(file_size: int) -> None:
    """
    Validate file size against maximum allowed size.
    
    Args:
        file_size: Size of file in bytes
        
    Raises:
        FileValidationError: If file exceeds maximum size
    """
    if file_size > MAX_FILE_SIZE_BYTES:
        max_mb = MAX_FILE_SIZE_BYTES / (1024 * 1024)
        actual_mb = file_size / (1024 * 1024)
        raise FileValidationError(
            f"File size ({actual_mb:.2f}MB) exceeds maximum allowed size ({max_mb:.0f}MB)"
        )


def validate_file_extension(filename: str) -> None:
    """
    Validate file extension against allowed extensions.
    
    Args:
        filename: Name of the file
        
    Raises:
        FileValidationError: If extension is not allowed
    """
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise FileValidationError(
            f"File type '{ext}' not supported. Allowed types: {allowed}"
        )


def validate_mime_type(file_content: bytes, filename: str) -> str:
    """
    Validate MIME type of file content using python-magic.
    
    Falls back to extension-based validation if python-magic is not available.
    
    Args:
        file_content: Raw bytes of the file
        filename: Name of the file (for logging)
        
    Returns:
        str: Detected MIME type (or 'application/octet-stream' if magic unavailable)
        
    Raises:
        FileValidationError: If MIME type is not allowed
    """
    if not MAGIC_AVAILABLE:
        # Fallback: Skip MIME validation, rely on extension check
        logger.debug(f"MIME validation skipped for {filename} (libmagic not installed)")
        return "application/octet-stream"
    
    try:
        # Detect MIME type from content
        mime = magic.from_buffer(file_content, mime=True)
        
        if mime not in ALLOWED_MIME_TYPES:
            logger.warning(f"Detected MIME type '{mime}' for file '{filename}'")
            allowed = ", ".join(sorted(ALLOWED_MIME_TYPES))
            raise FileValidationError(
                f"File MIME type '{mime}' not allowed. Allowed types: {allowed}"
            )
        
        return mime
        
    except FileValidationError:
        raise
    except Exception as e:
        logger.error(f"MIME type detection failed for {filename}: {e}")
        raise FileValidationError("Failed to validate file type")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Get just the filename, strip any path components
    safe_name = Path(filename).name
    
    # Remove any potentially dangerous characters
    safe_name = safe_name.replace("..", "").replace("/", "").replace("\\", "")
    
    # Ensure it's not empty after sanitization
    if not safe_name:
        raise FileValidationError("Invalid filename")
    
    return safe_name


def validate_upload_file(
    file_content: bytes, 
    filename: str
) -> tuple[str, str]:
    """
    Comprehensive validation for uploaded files.
    
    Args:
        file_content: Raw bytes of the file
        filename: Original filename
        
    Returns:
        tuple[str, str]: (sanitized_filename, mime_type)
        
    Raises:
        FileValidationError: If any validation fails
    """
    # 1. Sanitize filename
    safe_filename = sanitize_filename(filename)
    
    # 2. Validate file size
    validate_file_size(len(file_content))
    
    # 3. Validate extension
    validate_file_extension(safe_filename)
    
    # 4. Validate MIME type
    mime_type = validate_mime_type(file_content, safe_filename)
    
    logger.info(
        f"File validation passed: {safe_filename} "
        f"({len(file_content) / 1024:.2f}KB, {mime_type})"
    )
    
    return safe_filename, mime_type
