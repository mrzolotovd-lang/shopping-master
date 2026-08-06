"""Logging configuration for Shopping Master."""

import os
import sys
from pathlib import Path

from loguru import logger


def setup_logging(
    level: str = "INFO",
    log_file: str = None,
    rotation: str = "10 MB",
    retention: str = "30 days",
) -> None:
    """
    Setup logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        rotation: When to rotate log file (e.g., "10 MB", "1 day")
        retention: How long to keep old logs (e.g., "30 days")
    """
    # Remove default handler
    logger.remove()
    
    # Format string
    format_str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Add stdout handler (always)
    logger.add(
        sys.stdout,
        format=format_str,
        level=level,
        colorize=True,
    )
    
    # Add file handler (if configured)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_path,
            format=format_str,
            level=level,
            rotation=rotation,
            retention=retention,
            compression="zip",
            enqueue=True,  # Thread-safe
        )
        
        logger.info(f"Logging to file: {log_path}")


def setup_from_env() -> None:
    """Setup logging from environment variables."""
    level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE")  # e.g., "/var/log/shopping-bot/bot.log"
    rotation = os.getenv("LOG_ROTATION", "10 MB")
    retention = os.getenv("LOG_RETENTION", "30 days")
    
    setup_logging(
        level=level,
        log_file=log_file,
        rotation=rotation,
        retention=retention,
    )


# Auto-setup on import
if os.getenv("LOGGING_AUTO_SETUP", "true").lower() == "true":
    setup_from_env()
