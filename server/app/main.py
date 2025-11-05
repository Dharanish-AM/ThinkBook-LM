import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router
from .config import ALLOWED_ORIGINS, LOG_LEVEL
from .logging_config import setup_logging

setup_logging(LOG_LEVEL)
logger = logging.getLogger(__name__)

app = FastAPI(title="ThinkBook LM API", version="0.1")

# CORS - allow frontend origins (comma-separated in env)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok"}