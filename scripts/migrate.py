#!/usr/bin/env python3
"""Apply database migrations in CI/CD pipeline."""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def mask_url(url: str) -> str:
    """Mask database URL credentials for logging."""
    if not url:
        return "***"
    import re
    return re.sub(r'(postgresql://)[^:]+:[^@]+@', r'\1***:***@', url)


def run_migrations():
    """Run Alembic migrations."""
    from alembic.config import Config
    from alembic import command
    from sqlalchemy import create_engine, text
    
    # Get database URL
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not set")
        return 1
    
    print(f"🔗 Connecting to: {mask_url(db_url)}")
    
    # Test connection
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed")  # Don't log URL in error
        return 1
    
    # Run migrations
    alembic_cfg = Config(project_root / "alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    
    try:
        print("📦 Running migrations...")
        command.upgrade(alembic_cfg, "head")
        print("✅ Migrations applied successfully")
        return 0
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(run_migrations())
