"""Logging configuration module."""

import logging


def setup_logger(
    name: str = "lambda_logger",
    level: int = logging.INFO,
) -> logging.Logger:
    """Set up and return a standardized logger.

    Parameters
    ----------
    name: str
        The name of the logger.
    level: int
        Logging level (e.g., logging.INFO, logging.DEBUG).

    Returns
    -------
    logging.Logger
        Configured logger instance.

    """
    logger = logging.getLogger(name)
    if not logger.hasHandlers():  # Avoid duplicate handlers
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger
