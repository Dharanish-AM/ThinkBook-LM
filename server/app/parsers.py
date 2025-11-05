from pathlib import Path
from PyPDF2 import PdfReader
import docx
from .utils import read_file_text

def extract_text_pdf(path: Path) -> str:
    texts = []
    try:
        reader = PdfReader(str(path))
        for page in reader.pages:
            text = page.extract_text()
            if text:
                texts.append(text)
    except Exception as e:
        # Return any text fallback or empty
        return " ".join(texts)
    return "\n".join(texts)

def extract_text_docx(path: Path) -> str:
    try:
        doc = docx.Document(str(path))
        paragraphs = [p.text for p in doc.paragraphs if p.text]
        return "\n".join(paragraphs)
    except Exception:
        return ""

def extract_text_txt(path: Path) -> str:
    return read_file_text(path)

def extract_text_auto(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return extract_text_pdf(path)
    if ext in [".docx", ".doc"]:
        return extract_text_docx(path)
    # fallback to raw text
    return extract_text_txt(path)