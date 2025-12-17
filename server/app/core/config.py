import os
from pathlib import Path
from dotenv import load_dotenv

# Load app-specific env vars from .env.app to avoid conflict with chromadb's strict validation of .env
env_path = Path(__file__).parent.parent.parent / ".env.app"
load_dotenv(dotenv_path=env_path)

HOST = os.getenv("THINKBOOK_HOST", "0.0.0.0")
PORT = int(os.getenv("THINKBOOK_PORT", "8000"))
UPLOAD_DIR = Path(os.getenv("THINKBOOK_UPLOAD_DIR", "./data/uploads")).resolve()
QDRANT_DIR = Path(os.getenv("THINKBOOK_QDRANT_DIR", "./data/qdrant")).resolve()
# Default to local persistent mode if no URL provided
QDRANT_URL = os.getenv("THINKBOOK_QDRANT_URL") 
QDRANT_API_KEY = os.getenv("THINKBOOK_QDRANT_API_KEY")

OLLAMA_URL = os.getenv("THINKBOOK_OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("THINKBOOK_OLLAMA_MODEL", "llama3.1:8b")
EMBEDDING_MODEL = os.getenv("THINKBOOK_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
CHUNK_SIZE_TOKENS = int(os.getenv("THINKBOOK_CHUNK_SIZE_TOKENS", "800"))
CHUNK_OVERLAP_TOKENS = int(os.getenv("THINKBOOK_CHUNK_OVERLAP_TOKENS", "150"))
LOG_LEVEL = os.getenv("THINKBOOK_LOG_LEVEL", "INFO")
ALLOWED_ORIGINS = os.getenv("THINKBOOK_ALLOWED_ORIGINS", "http://localhost:3000").split(",")


UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
QDRANT_DIR.mkdir(parents=True, exist_ok=True)

MAX_CHUNKS = int(os.getenv("THINKBOOK_MAX_CHUNKS", "5"))
MAX_TOKENS = int(os.getenv("THINKBOOK_MAX_TOKENS", "512"))
TEMPERATURE = float(os.getenv("THINKBOOK_TEMPERATURE", "0.0"))

