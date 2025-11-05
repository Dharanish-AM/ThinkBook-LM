from pathlib import Path
import shutil
import uuid

def safe_filename(filename: str) -> str:
    # minimal sanitization
    return "".join(c for c in filename if c.isalnum() or c in "._- ").rstrip()

def write_upload_bytes(upload_bytes: bytes, dest_dir: Path, original_filename: str) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    safe_name = safe_filename(original_filename)
    unique = f"{uuid.uuid4().hex}_{safe_name}"
    dest = dest_dir / unique
    dest.write_bytes(upload_bytes)
    return dest

def read_file_text(path: Path, encoding: str = "utf-8") -> str:
    try:
        return path.read_text(encoding=encoding, errors="ignore")
    except Exception:
        return ""