"""Unit tests for embedding functionality."""

import pytest
import numpy as np
from app.rag.embeddings import get_embedding_model, embed_texts


class TestEmbeddings:
    """Tests for embedding functions."""
    
    def test_get_embedding_model(self):
        """Test getting the embedding model."""
        model = get_embedding_model()
        assert model is not None
    
    def test_get_embedding_model_singleton(self):
        """Test that embedding model is a singleton."""
        model1 = get_embedding_model()
        model2 = get_embedding_model()
        assert model1 is model2
    
    def test_embed_single_text(self):
        """Test embedding a single text."""
        texts = ["This is a test sentence."]
        embeddings = embed_texts(texts)
        
        assert len(embeddings) == 1
        assert isinstance(embeddings[0], np.ndarray)
        assert len(embeddings[0]) == 384  # all-MiniLM-L6-v2 dimension
    
    def test_embed_multiple_texts(self):
        """Test embedding multiple texts."""
        texts = [
            "First sentence.",
            "Second sentence.",
            "Third sentence."
        ]
        embeddings = embed_texts(texts)
        
        assert len(embeddings) == 3
        assert all(isinstance(emb, np.ndarray) for emb in embeddings)
        assert all(len(emb) == 384 for emb in embeddings)
    
    def test_embed_empty_list(self):
        """Test embedding empty list."""
        texts = []
        embeddings = embed_texts(texts)
        
        assert len(embeddings) == 0
    
    def test_embedding_similarity(self):
        """Test that similar texts have similar embeddings."""
        texts = [
            "The cat sat on the mat.",
            "A cat was sitting on a mat.",
            "Dogs are playing in the park."
        ]
        embeddings = embed_texts(texts)
        
        # Compute cosine similarity between first two (similar) and first and third (different)
        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        
        sim_similar = cosine_similarity(embeddings[0], embeddings[1])
        sim_different = cosine_similarity(embeddings[0], embeddings[2])
        
        # Similar sentences should have higher similarity
        assert sim_similar > sim_different
        assert sim_similar > 0.7  # High similarity threshold
    
    def test_embedding_deterministic(self):
        """Test that embeddings are deterministic."""
        text = "This should produce the same embedding every time."
        
        emb1 = embed_texts([text])[0]
        emb2 = embed_texts([text])[0]
        
        np.testing.assert_array_almost_equal(emb1, emb2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
