# app/core/logging.py
import logging
import sys

LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s"

def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
