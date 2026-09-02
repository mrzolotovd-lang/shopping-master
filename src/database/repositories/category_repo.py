"""Category repository for database operations."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from ..models import Category


class CategoryRepository:
    """Repository for Category operations."""

    def __init__(self, db_connection):
        """Initialize repository."""
        self.db = db_connection

    def create(
        self,
        session: Session,
        name: str,
        description: Optional[str] = None,
        default_consumption_rule_id: Optional[int] = None,
    ) -> Category:
        """Create a new category."""
        category = Category(
            name=name,
            description=description,
            default_consumption_rule_id=default_consumption_rule_id,
        )
        session.add(category)
        session.flush()
        return category

    def get_by_id(self, session: Session, category_id: int) -> Optional[Category]:
        """Get category by ID."""
        return session.query(Category).filter(Category.id == category_id).first()

    def get_by_name(self, session: Session, name: str) -> Optional[Category]:
        """Get category by name."""
        return session.query(Category).filter(Category.name == name).first()

    def get_all(self, session: Session) -> list[Category]:
        """Get all categories."""
        return session.query(Category).order_by(Category.name).all()

    def update(
        self,
        session: Session,
        category_id: int,
        **kwargs,
    ) -> Optional[Category]:
        """Update category attributes."""
        category = self.get_by_id(session, category_id)
        if not category:
            return None

        for key, value in kwargs.items():
            if hasattr(category, key):
                setattr(category, key, value)

        category.updated_at = datetime.now(timezone.utc)
        return category

    def delete(self, session: Session, category_id: int) -> bool:
        """Delete a category."""
        category = self.get_by_id(session, category_id)
        if not category:
            return False

        session.delete(category)
        return True
