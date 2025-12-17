import logging
import sys
import json
from datetime import datetime

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logging(level: str = "INFO"):
    root = logging.getLogger()
    if root.handlers:
        return
    
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    handler = logging.StreamHandler(sys.stdout)
    # Check if we are in a production-like environment (optional, or just always use JSON)
    # For this task, "production-ready" implies structured logs.
    handler.setFormatter(JsonFormatter())
    
    root.addHandler(handler)
