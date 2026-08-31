import logging
from app.config import settings

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    
    # Only set up handlers if they haven't been added yet
    if not logger.handlers:
        level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
        logger.setLevel(level)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.propagate = False

    return logger
