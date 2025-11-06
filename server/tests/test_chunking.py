from app.chunking import chunk_text, chunk_text_charwise


def test_chunk_charwise():
    text = "x" * 10000
    chunks = chunk_text_charwise(text, chunk_size_chars=2000, overlap_chars=200)
    
    assert len(chunks) >= 4
    assert all(len(c) <= 2000 for c in chunks)


def test_chunk_text_token_fallback():
    text = "This is a test. " * 1000
    chunks = chunk_text(text)
    
    assert isinstance(chunks, list)
    assert len(chunks) >= 1
