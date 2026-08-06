#!/usr/bin/env python3
"""Export database to JSON."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from database.connection import DatabaseConnection


def export_to_json(db_url: str, output_path: str):
    """Export database to JSON file."""
    print(f"Exporting from: {db_url}")
    
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    data = {
        "exported_at": datetime.now().isoformat(),
        "tables": {}
    }
    
    tables = [
        "categories",
        "items",
        "shopping_list",
        "consumption_logs",
        "purchase_logs",
        "users"
    ]
    
    for table_name in tables:
        try:
            table = Table(table_name, MetaData(), autoload_with=engine)
            rows = session.query(table).all()
            data["tables"][table_name] = [dict(row._mapping) for row in rows]
            print(f"  ✓ {table_name}: {len(data['tables'][table_name])} rows")
        except Exception as e:
            print(f"  ⚠ {table_name}: {e}")
            data["tables"][table_name] = []
    
    session.close()
    
    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n✅ Exported to: {output_path}")
    return 0


def main():
    """Run export."""
    db_type = os.getenv("DATABASE_TYPE", "sqlite")
    
    if db_type == "sqlite":
        db_path = os.getenv("DATABASE_PATH", "./shopping_master.db")
        db_url = DatabaseConnection.get_sqlite_url(db_path)
    else:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("ERROR: DATABASE_URL not set")
            return 1
    
    output = os.getenv("EXPORT_PATH", f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    return export_to_json(db_url, output)


if __name__ == "__main__":
    sys.exit(main())
