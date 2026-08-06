"""Operation log repository for database operations."""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from ..models import OperationLog


class OperationLogRepository:
    """Repository for OperationLog operations."""

    def __init__(self, db_connection):
        """Initialize repository."""
        self.db = db_connection

    def create(
        self,
        session: Session,
        item_id: int,
        operation_type: str,
        user_id: Optional[int] = None,
        old_value: Optional[float] = None,
        new_value: Optional[float] = None,
        comment: Optional[str] = None,
    ) -> OperationLog:
        """Create operation log entry."""
        log_entry = OperationLog(
            item_id=item_id,
            user_id=user_id,
            operation_type=operation_type,
            old_value=old_value,
            new_value=new_value,
            comment=comment,
        )
        session.add(log_entry)
        session.flush()
        return log_entry

    def get_by_item(
        self, session: Session, item_id: int, limit: int = 50
    ) -> list[OperationLog]:
        """Get operation logs for an item."""
        return (
            session.query(OperationLog)
            .filter(OperationLog.item_id == item_id)
            .order_by(OperationLog.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_user(
        self, session: Session, user_id: int, limit: int = 50
    ) -> list[OperationLog]:
        """Get operation logs by a user."""
        return (
            session.query(OperationLog)
            .filter(OperationLog.user_id == user_id)
            .order_by(OperationLog.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_type(
        self, session: Session, operation_type: str, limit: int = 50
    ) -> list[OperationLog]:
        """Get operation logs by type."""
        return (
            session.query(OperationLog)
            .filter(OperationLog.operation_type == operation_type)
            .order_by(OperationLog.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_recent(
        self, session: Session, limit: int = 100
    ) -> list[OperationLog]:
        """Get recent operation logs."""
        return (
            session.query(OperationLog)
            .order_by(OperationLog.created_at.desc())
            .limit(limit)
            .all()
        )
