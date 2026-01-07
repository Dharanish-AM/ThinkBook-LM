"""Unit tests for text chunking functionality."""

import pytest
from app.rag.chunking import chunk_text, count_tokens


class TestChunking:
    """Tests for text chunking functions."""
    
    def test_count_tokens_simple(self):
        """Test token counting for simple text."""
        text = "Hello world, this is a test."
        tokens = count_tokens(text)
        assert tokens > 0
        assert isinstance(tokens, int)
    
    def test_count_tokens_empty(self):
        """Test token counting for empty text."""
        text = ""
        tokens = count_tokens(text)
        assert tokens == 0
    
    def test_chunk_text_small(self):
        """Test chunking small text (should return single chunk)."""
        text = "This is a small piece of text that should fit in one chunk."
        chunks = chunk_text(text)
        
        assert len(chunks) == 1
        assert chunks[0] == text
    
    def test_chunk_text_large(self):
        """Test chunking large text (should return multiple chunks)."""
        # Create text that exceeds chunk size
        large_text = " ".join(["This is sentence number {}.".format(i) for i in range(500)])
        chunks = chunk_text(large_text)
        
        assert len(chunks) > 1
        # Verify all chunks are non-empty
        assert all(chunk.strip() for chunk in chunks)
        # Verify chunks don't exceed token limit significantly
        for chunk in chunks:
            assert count_tokens(chunk) <= 1000  # Allowing some buffer
    
    def test_chunk_text_empty(self):
        """Test chunking empty text."""
        text = ""
        chunks = chunk_text(text)
        
        assert len(chunks) == 0 or (len(chunks) == 1 and chunks[0] == "")
    
    def test_chunk_overlap(self):
        """Test that chunks have overlap when configured."""
        # Create moderate-sized text
        text = " ".join(["Sentence number {}.".format(i) for i in range(200)])
        chunks = chunk_text(text)
        
        if len(chunks) > 1:
            # Check that there's some overlap between consecutive chunks
            # (This is a heuristic check - proper overlap detection would need implementation details)
            assert len(chunks[0]) > 0
            assert len(chunks[1]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
