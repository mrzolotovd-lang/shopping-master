#!/usr/bin/env python3
"""Migrate SQLite database to PostgreSQL."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from database.connection import DatabaseConnection
from database.models import Base


def export_sqlite(sqlite_path: str) -> dict:
    """Export all data from SQLite."""
    print(f"Exporting from SQLite: {sqlite_path}")
    
    sqlite_url = DatabaseConnection.get_sqlite_url(sqlite_path)
    engine = create_engine(sqlite_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    data = {}
    
    # Export all tables
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
            data[table_name] = [dict(row._mapping) for row in rows]
            print(f"  ✓ {table_name}: {len(data[table_name])} rows")
        except Exception as e:
            print(f"  ⚠ {table_name}: {e}")
            data[table_name] = []
    
    session.close()
    return data


def import_postgresql(data: dict, pg_url: str):
    """Import data to PostgreSQL."""
    print(f"\nImporting to PostgreSQL...")
    
    engine = create_engine(pg_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Create tables
    Base.metadata.create_all(engine)
    print("  ✓ Tables created")
    
    # Import data (order matters for foreign keys)
    table_order = ["users", "categories", "items", "shopping_list", "consumption_logs", "purchase_logs"]
    
    for table_name in table_order:
        if table_name not in data or not data[table_name]:
            print(f"  ⚠ {table_name}: no data")
            continue
        
        try:
            table = Table(table_name, MetaData(), autoload_with=engine)
            for row in data[table_name]:
                # Remove id if exists (let DB auto-generate)
                row.pop("id", None)
                stmt = table.insert().values(**row)
                session.execute(stmt)
            print(f"  ✓ {table_name}: {len(data[table_name])} rows imported")
        except Exception as e:
            print(f"  ❌ {table_name}: {e}")
    
    session.commit()
    session.close()
    print("\n✅ Migration completed!")


def main():
    """Run migration."""
    sqlite_path = os.getenv("SQLITE_PATH", "./shopping_master.db")
    pg_url = os.getenv("DATABASE_URL")
    
    if not pg_url:
        print("ERROR: DATABASE_URL not set")
        print("Example: postgresql://user:password@host:5432/dbname")
        return 1
    
    # Export
    data = export_sqlite(sqlite_path)
    
    # Import
    import_postgresql(data, pg_url)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
