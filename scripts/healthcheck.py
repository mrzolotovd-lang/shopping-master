#!/usr/bin/env python3
"""Health check script for monitoring."""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_database() -> tuple[bool, str]:
    """Check database connection."""
    try:
        from src.database.connection import DatabaseConnection
        from sqlalchemy import text
        
        db_type = os.getenv("DATABASE_TYPE", "sqlite")
        if db_type == "postgresql":
            db_url = os.getenv("DATABASE_URL")
            if not db_url:
                return False, "DATABASE_URL not set"
        else:
            db_path = os.getenv("DATABASE_PATH", "./shopping_master.db")
            db_url = DatabaseConnection.get_sqlite_url(db_path)
        
        from sqlalchemy import create_engine
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
        
        return True, "OK"
    except Exception as e:
        return False, str(e)


def check_telegram() -> tuple[bool, str]:
    """Check Telegram bot token."""
    try:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            return False, "TELEGRAM_BOT_TOKEN not set"
        
        # Basic format validation
        if ':' not in token:
            return False, "Invalid token format"
        
        return True, "OK"
    except Exception as e:
        return False, str(e)


def health_check() -> dict:
    """Perform full health check."""
    results = {
        "timestamp": datetime.now().isoformat(),
        "status": "ok",
        "checks": {}
    }
    
    # Database check
    db_ok, db_msg = check_database()
    results["checks"]["database"] = {
        "status": "ok" if db_ok else "error",
        "message": db_msg
    }
    
    # Telegram check
    tg_ok, tg_msg = check_telegram()
    results["checks"]["telegram"] = {
        "status": "ok" if tg_ok else "error",
        "message": tg_msg
    }
    
    # Overall status
    if not db_ok or not tg_ok:
        results["status"] = "degraded" if (db_ok or tg_ok) else "error"
    
    return results


def main():
    """Run health check and print result."""
    result = health_check()
    
    # Print as simple status
    status = result["status"]
    checks = result["checks"]
    
    print(f"Status: {status.upper()}")
    print(f"Database: {checks['database']['status']} - {checks['database']['message']}")
    print(f"Telegram: {checks['telegram']['status']} - {checks['telegram']['message']}")
    
    # Exit code for monitoring
    sys.exit(0 if status == "ok" else 1)


if __name__ == "__main__":
    main()
