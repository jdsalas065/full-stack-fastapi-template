"""
Logging configuration for the application.

Provides structured logging with proper formatting and handlers.
"""

import logging
import sys

from app.core.config import settings


def setup_logging() -> None:
    """
    Configure application logging.

    Sets up formatters and handlers based on environment.
    """
    log_level = logging.DEBUG if settings.ENVIRONMENT == "local" else logging.INFO

    # Create formatter
    log_format = "%(levelname)s:     %(message)s"
    if settings.ENVIRONMENT != "local":
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(log_format)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Usually __name__ from the calling module

    Returns:
        Configured logger instance

    Example:
        logger = get_logger(__name__)
        logger.info("Starting process")
    """
    return logging.getLogger(name)
