import logging
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router
from .core.config import ALLOWED_ORIGINS, LOG_LEVEL, OLLAMA_URL, OLLAMA_MODEL
from .core.logging_config import setup_logging
from .rag.embeddings import get_embedding_model

setup_logging(LOG_LEVEL)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ThinkBook LM API",
    version="0.2.0",
    description="""
    ## ThinkBook LM - Private Document Intelligence API
    
    A privacy-focused, offline-first AI research assistant for secure document analysis.
    
    ### Features
    
    * 🔒 **100% Private**: All processing happens locally
    * 📚 **Multi-Modal**: PDF, DOCX, TXT, Images, Audio, Video
    * 🤖 **RAG Pipeline**: Qdrant vector search + Ollama LLM
    * ⚡ **Streaming**: Real-time responses via Server-Sent Events
    
    ### Workflow
    
    1. **Upload** documents via `/api/upload_file`
    2. **Query** your knowledge base via `/api/query` or `/api/query_stream`
    3. **Manage** files via `/api/list_files` and `/api/delete_file`
    
    ### Security
    
    * File size validation (50MB max)
    * MIME type verification
    * Path traversal protection
    * Supported formats: PDF, DOCX, TXT, PNG, JPG, WAV, MP3, MP4
    """,
    contact={
        "name": "ThinkBook LM",
        "url": "https://github.com/Dharanish-AM/ThinkBook-LM",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.on_event("startup")
async def preload_models():
    logger.info("Preloading embedding model...")
    get_embedding_model()
    logger.info("Embedding model loaded successfully.")

    # 🔥 Preload Ollama model to avoid first-query timeout
    try:
        logger.info(f"Preloading Ollama model: {OLLAMA_MODEL}...")
        resp = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": "warmup", "stream": False},
            timeout=120,
        )
        logger.info(f"Ollama model {OLLAMA_MODEL} preloaded successfully.")
    except Exception as e:
        logger.warning(f"Ollama preload failed (will auto-load later): {e}")


@app.get("/health")
def health():
    return {"status": "ok"}
