"""
MarketAI Suite — Application Logger
=====================================
Centralised logging configuration used across all modules.
"""

import os
import logging
import logging.handlers
from pathlib import Path


def setup_logger(name: str = "marketai", log_level: str = "INFO", log_file: str | None = None) -> logging.Logger:
    """
    Configure and return the root application logger.

    Parameters
    ----------
    name      : Logger name (default "marketai")
    log_level : Logging level string (DEBUG / INFO / WARNING / ERROR)
    log_file  : Optional path to a log file.  Stdout handler always added.

    Returns
    -------
    logging.Logger
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers when called multiple times
    if logger.handlers:
        return logger

    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(module)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ── Console handler (always active) ───────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ── File handler (optional) ────────────────────────────────
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent log records from propagating to the root logger
    logger.propagate = False

    return logger


# ──────────────────────────────────────────────────────────────
# Module-level convenience: other modules do `from utils.logger import get_logger`
# ──────────────────────────────────────────────────────────────
def get_logger(module_name: str) -> logging.Logger:
    """
    Return a child logger named ``marketai.<module_name>``.
    The parent logger must have been configured via :func:`setup_logger` first.
    """
    return logging.getLogger(f"marketai.{module_name}")
