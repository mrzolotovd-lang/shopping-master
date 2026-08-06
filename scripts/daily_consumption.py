#!/usr/bin/env python3
"""Run daily consumption for scheduled CI/CD job."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database.connection import DatabaseConnection
from core.agent import Agent


def main():
    """Run daily consumption."""
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        print("ERROR: DATABASE_URL not set")
        sys.exit(1)
    
    print(f"Connecting to database...")
    db = DatabaseConnection(database_url=db_url)
    
    print("Running daily consumption...")
    agent = Agent(db)
    result = agent.run_daily_consumption()
    
    print(f"✅ Daily consumption completed:")
    print(f"   Updated: {result['updated']} / {result['processed']} items")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
