from pathlib import Path
import shutil
import uuid


def safe_filename(filename: str) -> str:
    
    return "".join(c for c in filename if c.isalnum() or c in "._- ").rstrip()


from pathlib import Path


def write_upload_bytes(data: bytes, upload_dir: Path, filename: str):
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / filename

    
    if file_path.exists():
        file_path.unlink()

    with open(file_path, "wb") as f:
        f.write(data)

    return file_path


def read_file_text(path: Path, encoding: str = "utf-8") -> str:
    try:
        return path.read_text(encoding=encoding, errors="ignore")
    except Exception:
        return ""
