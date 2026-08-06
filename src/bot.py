"""Telegram bot entry point."""

import asyncio
import os
import re
import signal

from dotenv import load_dotenv
from loguru import logger

from .database.connection import DatabaseConnection
from .interfaces.telegram import TelegramBot


def validate_telegram_token(token: str) -> bool:
    """
    Validate Telegram bot token format.
    Format: {api_id}:{api_hash}
    api_id: 9-10 digits
    api_hash: 25-50 characters (letters, numbers, underscores, hyphens)
    """
    if not token or ':' not in token:
        return False
    
    parts = token.split(':')
    if len(parts) != 2:
        return False
    
    api_id, api_hash = parts
    
    # Validate API ID (9-10 digits)
    if not api_id.isdigit() or len(api_id) not in range(9, 11):
        return False
    
    # Validate API Hash (25-50 chars)
    if len(api_hash) < 25 or len(api_hash) > 50:
        return False
    
    # Check allowed characters
    if not re.match(r'^[A-Za-z0-9_-]+$', api_hash):
        return False
    
    return True


def validate_env() -> bool:
    """Validate all required environment variables."""
    errors = []
    
    # Validate Telegram token
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        errors.append("TELEGRAM_BOT_TOKEN is not set")
    elif not validate_telegram_token(token):
        errors.append(f"TELEGRAM_BOT_TOKEN has invalid format")
        logger.error(f"Token format should be: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
    
    # Validate admin chat ID (required for alerts)
    admin_chat_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID")
    if not admin_chat_id:
        errors.append("TELEGRAM_ADMIN_CHAT_ID is not set (alerts will not work)")
    elif not admin_chat_id.isdigit():
        errors.append("TELEGRAM_ADMIN_CHAT_ID must be numeric (Telegram chat ID)")
    
    # Validate database config
    db_type = os.getenv("DATABASE_TYPE", "sqlite")
    if db_type == "postgresql":
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            errors.append("DATABASE_URL is required for PostgreSQL")
        elif not db_url.startswith("postgresql://"):
            errors.append("DATABASE_URL must start with postgresql://")
    
    if errors:
        for error in errors:
            logger.error(f"Configuration error: {error}")
        return False
    
    logger.info("Environment validation passed")
    return True


async def main():
    """Run Telegram bot with graceful shutdown."""
    load_dotenv()
    
    logger.info("Starting Shopping Master Bot...")
    
    # Validate environment
    if not validate_env():
        raise ValueError("Environment validation failed")
    
    # Initialize database
    db_type = os.getenv("DATABASE_TYPE", "sqlite")
    
    if db_type == "postgresql":
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL not set")
    else:
        db_path = os.getenv("DATABASE_PATH", "./shopping_master.db")
        db_url = DatabaseConnection.get_sqlite_url(db_path)
    
    db = DatabaseConnection(database_url=db_url)
    logger.info(f"Database initialized: {db_type}")
    
    # Initialize bot
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not set")
    
    # Validate token format: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
    token_pattern = r'^\d{9,10}:[A-Za-z0-9_-]{35}$'
    if not re.match(token_pattern, token):
        logger.warning(f"Telegram token format may be invalid (length: {len(token)})")
    
    bot = TelegramBot(token, db)
    
    logger.info("Bot started successfully")
    
    # Setup graceful shutdown
    loop = asyncio.get_event_loop()
    stop_requested = False
    
    def signal_handler():
        nonlocal stop_requested
        logger.info("Shutdown signal received, stopping gracefully...")
        stop_requested = True
    
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)
    
    # Start polling
    try:
        await bot.run_polling(retry_limit=5, retry_delay=5)
    except Exception:
        pass  # Already logged in run_polling
    finally:
        if stop_requested:
            await bot.stop()
        logger.info("Bot stopped gracefully")


if __name__ == "__main__":
    asyncio.run(main())
