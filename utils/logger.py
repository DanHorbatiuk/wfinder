# utils/logger.py
import logging

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO
)

def get_logger(name: str):
    logger = logging.getLogger(name)
    return logger