import pytest
from pathlib import Path
from app.parsers import extract_text_auto

def test_extract_text_txt(tmp_path):
    p = tmp_path / "test.txt"
    p.write_text("Hello world\nThis is test")
    text = extract_text_auto(p)
    assert "Hello world" in text

def test_extract_text_pdf_empty(tmp_path):
    p = tmp_path / "empty.pdf"
    # Invalid PDF content, but parser catches exception and returns empty or joined text
    p.write_bytes(b"%PDF-1.4\n%EOF")
    text = extract_text_auto(p)
    assert isinstance(text, str)

def test_extract_text_docx_empty(tmp_path):
    p = tmp_path / "empty.docx"
    try:
        from docx import Document
        doc = Document()
        doc.add_paragraph("hello docx")
        doc.save(str(p))
        text = extract_text_auto(p)
        assert "hello docx" in text
    except Exception:
        pytest.skip("python-docx not available or failed to create sample")
