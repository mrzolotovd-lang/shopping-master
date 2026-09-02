"""Item repository for database operations."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from ..models import Item
from .log_repo import OperationLogRepository


class ItemRepository:
    """Repository for Item operations."""

    def __init__(self, db_connection):
        """Initialize repository."""
        self.db = db_connection
        self.log_repo = OperationLogRepository(db_connection)

    def create(
        self,
        session: Session,
        name: str,
        category_id: Optional[int] = None,
        package_size: float = 1.0,
        unit: str = "шт",
        reorder_threshold: float = 10.0,
        consumption_rule_id: Optional[int] = None,
        auto_fill_mode: str = "ask",
        created_by: Optional[int] = None,
    ) -> Item:
        """Create a new item."""
        item = Item(
            name=name,
            category_id=category_id,
            current_stock=0,
            package_size=package_size,
            unit=unit,
            reorder_threshold=reorder_threshold,
            consumption_rule_id=consumption_rule_id,
            auto_fill_mode=auto_fill_mode,
            purchase_count=0,
            is_active=True,
            created_by=created_by,
        )
        session.add(item)
        session.flush()
        return item

    def get_by_id(self, session: Session, item_id: int) -> Optional[Item]:
        """Get item by ID."""
        return session.query(Item).filter(Item.id == item_id).first()

    def get_by_name(self, session: Session, name: str) -> Optional[Item]:
        """Get item by name (case-insensitive)."""
        return (
            session.query(Item)
            .filter(Item.name.ilike(name))
            .filter(Item.is_active == True)
            .first()
        )

    def get_all_active(self, session: Session) -> list[Item]:
        """Get all active items."""
        return (
            session.query(Item)
            .filter(Item.is_active == True)
            .order_by(Item.name)
            .all()
        )

    def get_all_items(self, session: Session) -> list[Item]:
        """Get all items with relationships."""
        return (
            session.query(Item)
            .filter(Item.is_active == True)
            .order_by(Item.name)
            .all()
        )

    def update_stock_level(
        self,
        session: Session,
        item_name: str,
        stock_level: float,
        user_id: Optional[int] = None,
    ) -> dict:
        """Update stock level for an item."""
        item = self.get_by_name(session, item_name)
        if not item:
            return {"success": False, "error": f"Item '{item_name}' not found"}

        old_stock = float(item.current_stock)
        item.current_stock = stock_level
        item.updated_at = datetime.now(timezone.utc)

        self.log_repo.create(
            session,
            item_id=item.id,
            user_id=user_id,
            operation_type="manual_update",
            old_value=old_stock,
            new_value=stock_level,
            comment=f"Manual stock update: {old_stock:.2f} -> {stock_level:.2f} {item.unit}",
        )

        return {
            "success": True,
            "item_id": item.id,
            "item_name": item.name,
            "old_stock": old_stock,
            "new_stock": stock_level,
        }

    def process_purchase(
        self,
        session: Session,
        item_name: str,
        amount: Optional[float] = None,
        unit: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> dict:
        """Process a purchase (add stock). Auto-creates item if not found."""
        item = self.get_by_name(session, item_name)
        if not item:
            # Auto-create item with defaults
            item = self.create(
                session=session,
                name=item_name,
                category_id=None,
                package_size=1.0,
                unit=unit or "шт",
                reorder_threshold=10.0,
                created_by=user_id,
            )
            session.flush()

        if amount is None:
            amount = float(item.package_size)

        old_stock = float(item.current_stock)
        new_stock = old_stock + amount

        item.current_stock = new_stock
        item.purchase_count += 1
        item.updated_at = datetime.now(timezone.utc)

        self.log_repo.create(
            session,
            item_id=item.id,
            user_id=user_id,
            operation_type="purchase",
            old_value=old_stock,
            new_value=new_stock,
            comment=f"Purchase: +{amount:.2f} {item.unit}",
        )

        if item.purchase_count >= 10 and item.auto_fill_mode == "ask":
            return {
                "success": True,
                "item_id": item.id,
                "item_name": item.name,
                "old_stock": old_stock,
                "new_stock": new_stock,
                "suggest_smart_mode": True,
                "purchase_count": item.purchase_count,
            }

        return {
            "success": True,
            "item_id": item.id,
            "item_name": item.name,
            "old_stock": old_stock,
            "new_stock": new_stock,
            "purchase_count": item.purchase_count,
        }

    def update(
        self,
        session: Session,
        item_id: int,
        **kwargs,
    ) -> Optional[Item]:
        """Update item attributes."""
        item = self.get_by_id(session, item_id)
        if not item:
            return None

        for key, value in kwargs.items():
            if hasattr(item, key):
                setattr(item, key, value)

        item.updated_at = datetime.now(timezone.utc)
        return item

    def delete(self, session: Session, item_id: int) -> bool:
        """Soft delete an item."""
        item = self.get_by_id(session, item_id)
        if not item:
            return False

        item.is_active = False
        item.updated_at = datetime.now(timezone.utc)
        return True
