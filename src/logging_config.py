"""
Centralized logging configuration for all ETL modules.
Ensures consistent log format, level, and output destination across scripts.

How it fits the pipeline
- Used by every module (extract, transform, validate, load, pipeline).
- Keeps all logs in stdout (terminal) with timestamps and module names.
"""

import logging
import sys


def setup_logging(name: str = None, level: str = "INFO") -> logging.Logger:
    """Configure and return a logger with standard format."""
    logger = logging.getLogger(name)
    if logger.handlers:  # Prevent duplicate handlers
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    logger.addHandler(handler)
    return logger