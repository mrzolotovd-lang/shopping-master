"""User repository for database operations."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from ..models import User


class UserRepository:
    """Repository for User operations."""

    def __init__(self, db_connection):
        """Initialize repository."""
        self.db = db_connection

    def create(
        self,
        session: Session,
        name: str,
        telegram_id: Optional[int] = None,
        priority: int = 5,
    ) -> User:
        """Create a new user."""
        user = User(
            telegram_id=telegram_id,
            name=name,
            priority=priority,
        )
        session.add(user)
        session.flush()
        return user

    def get_by_id(self, session: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return session.query(User).filter(User.id == user_id).first()

    def get_by_telegram_id(self, session: Session, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID."""
        return session.query(User).filter(User.telegram_id == telegram_id).first()

    def get_by_name(self, session: Session, name: str) -> Optional[User]:
        """Get user by name."""
        return session.query(User).filter(User.name == name).first()

    def get_all(self, session: Session) -> list[User]:
        """Get all users."""
        return session.query(User).order_by(User.priority).all()

    def update(
        self,
        session: Session,
        user_id: int,
        **kwargs,
    ) -> Optional[User]:
        """Update user attributes."""
        user = self.get_by_id(session, user_id)
        if not user:
            return None

        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)

        user.updated_at = datetime.now(timezone.utc)
        return user

    def delete(self, session: Session, user_id: int) -> bool:
        """Delete a user."""
        user = self.get_by_id(session, user_id)
        if not user:
            return False

        session.delete(user)
        return True
