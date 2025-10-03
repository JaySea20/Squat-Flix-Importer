#!/usr/bin/env python3
# modules/Jaylog.py

__version__ = "v0.1.0-beta"

import logging
from pathlib import Path
import colorama
init(autoreset=True)

class ColorFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT,
    }

    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelno, "")
        message = super().format(record)
        return f"{color}{message}{Style.RESET_ALL}"

def mklog(name: str, logfile: str = None, level: str = "INFO") -> logging.Logger:
    """
    Create and configure a logger with color for console and plain text for file.

    Args:
        name (str): Logger name (usually __name__).
        logfile (str): Optional path to a log file. If None, logs only to console.
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers if already initialized
    if logger.handlers:
        return logger

    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Console handler (colored)
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(ColorFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                                   datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(ch)

    # File handler (plain, no colors)
    if logfile:
        logfile_path = Path(logfile)
        logfile_path.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(logfile_path)
        fh.setLevel(log_level)
        fh.setFormatter(logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        logger.addHandler(fh)
        logger.debug(f"Logger '{name}' initialized with level {level.upper()}")
    return logger
