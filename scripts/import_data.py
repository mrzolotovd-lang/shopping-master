#!/usr/bin/env python3
"""Import database from JSON."""

import json
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from database.connection import DatabaseConnection
from database.models import Base


def import_from_json(json_path: str, db_url: str):
    """Import database from JSON file."""
    print(f"Importing from: {json_path}")
    print(f"Target database: {db_url}")
    
    # Load JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"Exported at: {data.get('exported_at', 'unknown')}")
    
    # Connect to DB
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Create tables
    Base.metadata.create_all(engine)
    print("\n✓ Tables created")
    
    # Import data (order matters for foreign keys)
    table_order = ["users", "categories", "items", "shopping_list", "consumption_logs", "purchase_logs"]
    
    for table_name in table_order:
        if table_name not in data["tables"] or not data["tables"][table_name]:
            print(f"  ⚠ {table_name}: no data")
            continue
        
        try:
            table = Table(table_name, MetaData(), autoload_with=engine)
            for row in data["tables"][table_name]:
                # Remove id if exists (let DB auto-generate)
                row.pop("id", None)
                stmt = table.insert().values(**row)
                session.execute(stmt)
            print(f"  ✓ {table_name}: {len(data['tables'][table_name])} rows imported")
        except Exception as e:
            print(f"  ❌ {table_name}: {e}")
    
    session.commit()
    session.close()
    
    print("\n✅ Import completed!")
    return 0


def main():
    """Run import."""
    json_path = os.getenv("IMPORT_PATH")
    
    if not json_path:
        print("ERROR: IMPORT_PATH not set")
        print("Usage: IMPORT_PATH=backup.json python import_data.py")
        return 1
    
    db_type = os.getenv("DATABASE_TYPE", "sqlite")
    
    if db_type == "sqlite":
        db_path = os.getenv("DATABASE_PATH", "./shopping_master.db")
        db_url = DatabaseConnection.get_sqlite_url(db_path)
    else:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("ERROR: DATABASE_URL not set")
            return 1
    
    return import_from_json(json_path, db_url)


if __name__ == "__main__":
    sys.exit(main())
