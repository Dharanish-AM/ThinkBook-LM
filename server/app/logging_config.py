import logging
import os
from logging import StreamHandler, Formatter

def setup_logging(level: str = "INFO"):
    root = logging.getLogger()
    if root.handlers:
        return  # already configured
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    handler = StreamHandler()
    fmt = "%(asctime)s — %(name)s — %(levelname)s — %(message)s"
    handler.setFormatter(Formatter(fmt))
    root.addHandler(handler)