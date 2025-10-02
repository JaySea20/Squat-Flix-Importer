# web/logger.py

import logging
import os
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
#LOG_PATH = os.getenv("SQUATFLIX_LOG", os.path.join(SCRIPT_DIR, "..", "logs", "squatflix.log"))

class LogColors:
    RESET   = "\033[0m"
    DEBUG   = "\033[36m"
    INFO    = "\033[32m"
    WARNING = "\033[33m"
    ERROR   = "\033[31m"

class ColorFormatter(logging.Formatter):
    def format(self, record):
        color = getattr(LogColors, record.levelname, LogColors.RESET)
        message = super().format(record)
        return f"{color}{message}{LogColors.RESET}"

def setup_logger(level="DEBUG", log_path=None):
    if log_path is None:
        log_path = "./DEFAULT.LOG"

    if level is None:
        level = "DEBUG"

    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logger = logging.getLogger()

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if logger.hasHandlers():
        logger.handlers.clear()

    FORMAT = "[%(asctime)s] [%(levelname)s] %(message)s"

    plain_fmt = logging.Formatter(FORMAT)
    color_fmt = ColorFormatter(FORMAT)

    ch = logging.StreamHandler()
    ch.setLevel(getattr(logging, level.upper(), logging.DEBUG))
    ch.setFormatter(color_fmt)
    logger.addHandler(ch)

    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(plain_fmt)
    logger.addHandler(fh)

    return logger
