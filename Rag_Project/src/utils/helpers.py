import os
import logging
import yaml
from typing import Any, Dict

# Default paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

def load_config() -> Dict[str, Any]:
    """Loads configuration parameters from config.yaml."""
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Configuration file not found at {CONFIG_PATH}")
        
    with open(CONFIG_PATH, "r") as f:
        try:
            config = yaml.safe_load(f)
            return config
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing configuration YAML: {e}")

def get_project_path(relative_path: str) -> str:
    """Returns the absolute path of a resource relative to the project root."""
    return os.path.normpath(os.path.join(BASE_DIR, relative_path))

def setup_logging() -> logging.Logger:
    """Initializes and configures the application logger."""
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR, exist_ok=True)
        
    log_file = os.path.join(LOGS_DIR, "app.log")
    
    logger = logging.getLogger("tech_fusion_rag")
    # Avoid adding multiple handlers if setup is called multiple times
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s - %(filename)s:%(lineno)d - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
    return logger

# Pre-initialized logger instance
logger = setup_logging()
