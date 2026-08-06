"""Threshold checker for shopping list management."""

from loguru import logger
from sqlalchemy.orm import Session

from ..database.models import Item
from ..database.repositories.item_repo import ItemRepository
from ..database.repositories.shopping_repo import ShoppingListRepository


class ThresholdChecker:
    """Check item thresholds and manage shopping list."""

    def __init__(self, db_connection):
        """Initialize threshold checker."""
        self.db = db_connection
        self.item_repo = ItemRepository(db_connection)
        self.shopping_repo = ShoppingListRepository(db_connection)

    def check_all_items(self, session: Session) -> dict:
        """Check thresholds for all items."""
        items = self.item_repo.get_all_active(session)
        result = {"checked": 0, "added": 0, "removed": 0, "unchanged": 0}

        for item in items:
            try:
                needs_purchase = self._check_item_threshold(item)
                if needs_purchase:
                    added = self._add_to_shopping_list(session, item)
                    if added:
                        result["added"] += 1
                    else:
                        result["unchanged"] += 1
                else:
                    removed = self._remove_from_shopping_list(session, item)
                    if removed:
                        result["removed"] += 1
                    else:
                        result["unchanged"] += 1
                result["checked"] += 1
            except Exception as e:
                logger.error(f"Failed to check item {item.id}: {e}")

        return result

    def _check_item_threshold(self, item: Item) -> bool:
        """Check if item needs to be added to shopping list."""
        threshold_amount = float(item.package_size) * (float(item.reorder_threshold) / 100)
        return float(item.current_stock) <= threshold_amount

    def _add_to_shopping_list(self, session: Session, item: Item) -> bool:
        """Add item to shopping list if not already there."""
        existing = self.shopping_repo.get_pending_for_item(session, item.id)
        if existing:
            return False

        quantity = self._calculate_recommended_quantity(item)
        self.shopping_repo.create(
            session,
            item_id=item.id,
            quantity=quantity,
            reason="threshold",
        )
        logger.info(f"Added {item.name} to shopping list (qty: {quantity})")
        return True

    def _remove_from_shopping_list(self, session: Session, item: Item) -> bool:
        """Remove item from shopping list if stock is sufficient."""
        existing = self.shopping_repo.get_pending_for_item(session, item.id)
        if not existing:
            return False

        self.shopping_repo.mark_completed(session, existing.id)
        logger.info(f"Removed {item.name} from shopping list")
        return True

    def _calculate_recommended_quantity(self, item: Item) -> float:
        """Calculate recommended purchase quantity."""
        current = float(item.current_stock)
        package = float(item.package_size)
        target = package * 2

        if current >= target:
            return 1.0

        needed = target - current
        return max(1.0, needed / package)
