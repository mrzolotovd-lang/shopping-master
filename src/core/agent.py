"""Main agent logic."""

from datetime import datetime
from typing import Optional

from loguru import logger
from sqlalchemy.orm import joinedload

from ..database.connection import DatabaseConnection
from ..database.models import Item, ShoppingListItem
from ..database.repositories.item_repo import ItemRepository
from ..database.repositories.shopping_repo import ShoppingListRepository
from .consumption import ConsumptionEngine
from .threshold import ThresholdChecker


class Agent:
    """Main shopping agent."""

    def __init__(self, db_connection):
        """Initialize agent."""
        self.db = db_connection
        self.item_repo = ItemRepository(db_connection)
        self.shopping_repo = ShoppingListRepository(db_connection)
        self.consumption_engine = ConsumptionEngine(db_connection)
        self.threshold_checker = ThresholdChecker(db_connection)

    def run_daily_consumption(self) -> dict:
        """Run daily consumption for all items."""
        logger.info("Starting daily consumption run")

        session = self.db.get_session()
        try:
            result = self.consumption_engine.apply_consumption(session)
            session.commit()
            logger.info(f"Daily consumption completed: {result}")
            return result
        except Exception as e:
            session.rollback()
            logger.error(f"Daily consumption failed: {e}")
            raise
        finally:
            session.close()

    def run_threshold_check(self) -> dict:
        """Check thresholds and update shopping list."""
        logger.info("Starting threshold check")

        session = self.db.get_session()
        try:
            result = self.threshold_checker.check_all_items(session)
            session.commit()
            logger.info(f"Threshold check completed: {result}")
            return result
        except Exception as e:
            session.rollback()
            logger.error(f"Threshold check failed: {e}")
            raise
        finally:
            session.close()

    def process_purchase(
        self,
        item_name: str,
        amount: Optional[float] = None,
        unit: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> dict:
        """Process a purchase."""
        logger.info(f"Processing purchase: {item_name}, amount={amount}, unit={unit}")

        session = self.db.get_session()
        try:
            result = self.item_repo.process_purchase(
                session, item_name, amount, unit, user_id
            )
            session.commit()
            logger.info(f"Purchase processed: {result}")
            return result
        except Exception as e:
            session.rollback()
            logger.error(f"Purchase processing failed: {e}")
            raise
        finally:
            session.close()

    def process_stock_update(
        self,
        item_name: str,
        stock_level: float,
        user_id: Optional[int] = None,
    ) -> dict:
        """Process a stock level update."""
        logger.info(f"Processing stock update: {item_name}, level={stock_level}")

        session = self.db.get_session()
        try:
            result = self.item_repo.update_stock_level(
                session, item_name, stock_level, user_id
            )
            session.commit()
            logger.info(f"Stock update processed: {result}")
            return result
        except Exception as e:
            session.rollback()
            logger.error(f"Stock update processing failed: {e}")
            raise
        finally:
            session.close()

    def get_shopping_list(self, status: str = "pending") -> list:
        """Get shopping list with items loaded."""
        session = self.db.get_session()
        try:
            return (
                session.query(ShoppingListItem)
                .options(joinedload(ShoppingListItem.item))
                .filter(ShoppingListItem.status == status)
                .order_by(ShoppingListItem.created_at)
                .all()
            )
        finally:
            session.close()

    def get_all_items_status(self) -> list:
        """Get status of all items."""
        session = self.db.get_session()
        try:
            return (
                session.query(Item)
                .options(joinedload(Item.category))
                .filter(Item.is_active == True)
                .order_by(Item.name)
                .all()
            )
        finally:
            session.close()
