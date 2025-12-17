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

app = FastAPI(title="ThinkBook LM API", version="0.1")


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
