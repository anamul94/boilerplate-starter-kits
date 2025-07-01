import logging
import sys
import os
from typing import List, Optional
from pydantic import BaseModel
import json
from datetime import datetime

# Create logs directory if it doesn't exist
logs_dir = "/var/log/fastapi"
try:
    os.makedirs(logs_dir, exist_ok=True)
except PermissionError:
    # Fallback to /tmp if /var/log is not writable
    logs_dir = "/tmp/fastapi-logs"
    os.makedirs(logs_dir, exist_ok=True)

class LogConfig(BaseModel):
    """Logging configuration"""
    LOGGER_NAME: str = "fastapi_app"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = os.path.join(logs_dir, "app.log")
    
    # Class variables for logger instances
    loggers: List[str] = []

def setup_logger(name: str = "fastapi_app", level: str = "INFO") -> logging.Logger:
    """
    Set up and configure a logger
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    
    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level))
    
    # Create file handler
    file_handler = logging.FileHandler(os.path.join(logs_dir, "app.log"))
    file_handler.setLevel(getattr(logging, level))
    
    # Create formatters
    formatter = logging.Formatter(
        '%(levelname)s | %(asctime)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add formatter to handlers
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Avoid duplicate handlers
    logger.propagate = False
    
    return logger

# Create default application logger
logger = setup_logger()

class CustomJSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging
    """
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        # Add any extra attributes
        for key, value in record.__dict__.items():
            if key not in ["timestamp", "level", "message", "module", "function", "line", 
                          "exc_info", "exc_text", "args", "msg", "levelname", "levelno", 
                          "pathname", "filename", "name", "thread", "threadName", 
                          "processName", "process", "relativeCreated", "msecs", "created"]:
                log_record[key] = value
                
        return json.dumps(log_record)