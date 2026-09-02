"""Consumption engine for automatic stock reduction."""

from datetime import datetime, timezone
from typing import Optional

from loguru import logger
from sqlalchemy.orm import Session

from ..database.models import ConsumptionRule, Item, OperationLog
from ..database.repositories.item_repo import ItemRepository
from ..database.repositories.log_repo import OperationLogRepository


class ConsumptionEngine:
    """Engine for applying consumption rules to items."""

    def __init__(self, db_connection):
        """Initialize consumption engine."""
        self.db = db_connection
        self.item_repo = ItemRepository(db_connection)
        self.log_repo = OperationLogRepository(db_connection)

    def apply_consumption(self, session: Session) -> dict:
        """Apply consumption to all active items."""
        items = self.item_repo.get_all_active(session)
        result = {"processed": 0, "updated": 0, "skipped": 0}

        for item in items:
            try:
                consumption = self._calculate_consumption(item)
                if consumption > 0:
                    self._apply_item_consumption(session, item, consumption)
                    result["updated"] += 1
                else:
                    result["skipped"] += 1
                result["processed"] += 1
            except Exception as e:
                logger.error(f"Failed to process item {item.id}: {e}")
                result["skipped"] += 1

        return result

    def _calculate_consumption(self, item: Item) -> float:
        """Calculate consumption amount for an item."""
        rule = self._get_consumption_rule(item)
        if not rule or rule.rule_type == "manual":
            return 0.0

        if rule.rule_type == "percentage_daily":
            percentage = float(rule.value) / 100
            return float(item.current_stock) * percentage
        elif rule.rule_type == "absolute_daily":
            return float(rule.value)

        return 0.0

    def _get_consumption_rule(self, item: Item) -> Optional[ConsumptionRule]:
        """Get consumption rule for item (item-level or category-level)."""
        if item.consumption_rule:
            return item.consumption_rule
        elif item.category and item.category.default_consumption_rule:
            return item.category.default_consumption_rule
        return None

    def _apply_item_consumption(
        self, session: Session, item: Item, consumption: float
    ) -> None:
        """Apply consumption to a single item."""
        old_stock = float(item.current_stock)
        new_stock = max(0, old_stock - consumption)

        item.current_stock = new_stock
        item.updated_at = datetime.now(timezone.utc)

        self.log_repo.create(
            session,
            item_id=item.id,
            operation_type="auto_consumption",
            old_value=old_stock,
            new_value=new_stock,
            comment=f"Daily consumption: -{consumption:.2f} {item.unit}",
        )

        logger.debug(f"Item {item.name}: {old_stock:.2f} -> {new_stock:.2f} (-{consumption:.2f})")
