"""Main entry point for Shopping Master agent."""

import sys
from pathlib import Path

from loguru import logger
from sqlalchemy.orm import joinedload

from .config import config_manager, get_config
from .core.agent import Agent
from .database.connection import DatabaseConnection
from .database.models import Item
from .nlp.processor import NLPProcessor


def setup_logging(config):
    """Setup logging configuration."""
    logger.remove()
    logger.add(
        sys.stdout,
        format=config.logging.format,
        level=config.logging.level,
    )
    log_path = Path(config.logging.file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger.add(
        str(log_path),
        format=config.logging.format,
        level=config.logging.level,
        rotation="10 MB",
        retention="7 days",
    )


def init_database(config):
    """Initialize database connection."""
    if config.database.type == "sqlite":
        db_url = DatabaseConnection.get_sqlite_url(config.database.sqlite_path)
    elif config.database.type == "postgresql":
        if not config.database.postgresql_url:
            raise ValueError("PostgreSQL URL not provided")
        db_url = config.database.postgresql_url
    else:
        raise ValueError(f"Unknown database type: {config.database.type}")

    db = DatabaseConnection(db_url)
    db.create_tables()
    return db


def cmd_run(args):
    """Run the agent."""
    config = config_manager.load(args.environment if hasattr(args, "environment") else "development")
    setup_logging(config)
    logger.info("Starting Shopping Master agent")

    db = init_database(config)
    agent = Agent(db)

    logger.info("Agent initialized successfully")

    if args.command == "consume":
        logger.info("Running daily consumption")
        result = agent.run_daily_consumption()
        print(f"Consumption result: {result}")

    elif args.command == "check-thresholds":
        logger.info("Checking thresholds")
        result = agent.run_threshold_check()
        print(f"Threshold check result: {result}")

    elif args.command == "status":
        items = agent.get_all_items_status()
        print(f"\n{'Item':<30} {'Stock':>10} {'Unit':<10} {'Category':<25}")
        print("-" * 80)
        for item in items:
            category_name = item.category.name if item.category else "N/A"
            print(f"{item.name:<30} {float(item.current_stock):>10.2f} {item.unit:<10} {category_name:<25}")

    elif args.command == "buy":
        shopping_list = agent.get_shopping_list("pending")
        if not shopping_list:
            print("\nShopping list is empty!")
        else:
            print(f"\n{'Item':<30} {'Qty':>10} {'Unit':<10} {'Reason':<15}")
            print("-" * 70)
            for entry in shopping_list:
                print(f"{entry.item.name:<30} {float(entry.quantity):>10.2f} {entry.item.unit:<10} {entry.reason:<15}")


def cmd_seed(args):
    """Seed database with test data."""
    from scripts.seed_data import seed_database

    config = config_manager.load("development")
    db = init_database(config)
    seed_database(db)
    print("Database seeded successfully!")


def cmd_export(args):
    """Export database to JSON."""
    from scripts.export import export_database

    config = config_manager.load("development")
    db = init_database(config)
    output_path = args.output if hasattr(args, "output") else "data/export.json"
    export_database(db, output_path)
    print(f"Database exported to {output_path}")


def cmd_import(args):
    """Import database from JSON."""
    from scripts.import_data import import_database

    config = config_manager.load("development")
    db = init_database(config)
    input_path = args.input if hasattr(args, "input") else "data/export.json"
    import_database(db, input_path)
    print(f"Database imported from {input_path}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Shopping Master Agent")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    run_parser = subparsers.add_parser("run", help="Run the agent")
    run_parser.add_argument("--environment", default="development", help="Environment")

    subparsers.add_parser("consume", help="Run daily consumption")
    subparsers.add_parser("check-thresholds", help="Check thresholds")
    subparsers.add_parser("status", help="Show all items status")
    subparsers.add_parser("buy", help="Show shopping list")

    seed_parser = subparsers.add_parser("seed", help="Seed database with test data")

    export_parser = subparsers.add_parser("export", help="Export database to JSON")
    export_parser.add_argument("--output", default="data/export.json", help="Output file path")

    import_parser = subparsers.add_parser("import", help="Import database from JSON")
    import_parser.add_argument("--input", default="data/export.json", help="Input file path")

    args = parser.parse_args()

    if args.command in ["run", "consume", "check-thresholds", "status", "buy"]:
        cmd_run(args)
    elif args.command == "seed":
        cmd_seed(args)
    elif args.command == "export":
        cmd_export(args)
    elif args.command == "import":
        cmd_import(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
