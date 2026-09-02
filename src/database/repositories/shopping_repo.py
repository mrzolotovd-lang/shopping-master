"""Shopping list repository for database operations."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from ..models import ShoppingListItem


class ShoppingListRepository:
    """Repository for ShoppingListItem operations."""

    def __init__(self, db_connection):
        """Initialize repository."""
        self.db = db_connection

    def create(
        self,
        session: Session,
        item_id: int,
        user_id: Optional[int] = None,
        quantity: float = 1.0,
        reason: str = "threshold",
    ) -> ShoppingListItem:
        """Add item to shopping list."""
        entry = ShoppingListItem(
            item_id=item_id,
            user_id=user_id,
            quantity=quantity,
            reason=reason,
            status="pending",
        )
        session.add(entry)
        session.flush()
        return entry

    def get_by_id(self, session: Session, entry_id: int) -> Optional[ShoppingListItem]:
        """Get shopping list entry by ID."""
        return session.query(ShoppingListItem).filter(ShoppingListItem.id == entry_id).first()

    def get_pending_for_item(self, session: Session, item_id: int) -> Optional[ShoppingListItem]:
        """Get pending shopping list entry for an item."""
        return (
            session.query(ShoppingListItem)
            .filter(ShoppingListItem.item_id == item_id)
            .filter(ShoppingListItem.status == "pending")
            .first()
        )

    def get_by_status(
        self, session: Session, status: str = "pending"
    ) -> list[ShoppingListItem]:
        """Get shopping list entries by status."""
        return (
            session.query(ShoppingListItem)
            .filter(ShoppingListItem.status == status)
            .order_by(ShoppingListItem.created_at)
            .all()
        )

    def get_all_with_items(self, session: Session, status: Optional[str] = None) -> list:
        """Get all shopping list entries with item details."""
        query = session.query(ShoppingListItem).join(ShoppingListItem.item)

        if status:
            query = query.filter(ShoppingListItem.status == status)

        return query.order_by(ShoppingListItem.created_at).all()

    def mark_completed(self, session: Session, entry_id: int) -> bool:
        """Mark shopping list entry as completed."""
        entry = self.get_by_id(session, entry_id)
        if not entry:
            return False

        entry.status = "completed"
        entry.completed_at = datetime.now(timezone.utc)
        entry.updated_at = datetime.now(timezone.utc)
        return True

    def mark_cancelled(self, session: Session, entry_id: int) -> bool:
        """Mark shopping list entry as cancelled."""
        entry = self.get_by_id(session, entry_id)
        if not entry:
            return False

        entry.status = "cancelled"
        entry.updated_at = datetime.now(timezone.utc)
        return True

    def remove(self, session: Session, entry_id: int) -> bool:
        """Remove shopping list entry."""
        entry = self.get_by_id(session, entry_id)
        if not entry:
            return False

        session.delete(entry)
        return True
