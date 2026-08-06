"""Consumption rule repository for database operations."""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from ..models import ConsumptionRule


class ConsumptionRuleRepository:
    """Repository for ConsumptionRule operations."""

    def __init__(self, db_connection):
        """Initialize repository."""
        self.db = db_connection

    def create(
        self,
        session: Session,
        name: str,
        rule_type: str,
        value: float,
        unit: str = "day",
    ) -> ConsumptionRule:
        """Create a new consumption rule."""
        rule = ConsumptionRule(
            name=name,
            rule_type=rule_type,
            value=value,
            unit=unit,
        )
        session.add(rule)
        session.flush()
        return rule

    def get_by_id(self, session: Session, rule_id: int) -> Optional[ConsumptionRule]:
        """Get rule by ID."""
        return session.query(ConsumptionRule).filter(ConsumptionRule.id == rule_id).first()

    def get_by_name(self, session: Session, name: str) -> Optional[ConsumptionRule]:
        """Get rule by name."""
        return session.query(ConsumptionRule).filter(ConsumptionRule.name == name).first()

    def get_all(self, session: Session) -> list[ConsumptionRule]:
        """Get all consumption rules."""
        return session.query(ConsumptionRule).order_by(ConsumptionRule.name).all()

    def get_by_type(self, session: Session, rule_type: str) -> list[ConsumptionRule]:
        """Get rules by type."""
        return (
            session.query(ConsumptionRule)
            .filter(ConsumptionRule.rule_type == rule_type)
            .order_by(ConsumptionRule.name)
            .all()
        )

    def update(
        self,
        session: Session,
        rule_id: int,
        **kwargs,
    ) -> Optional[ConsumptionRule]:
        """Update rule attributes."""
        rule = self.get_by_id(session, rule_id)
        if not rule:
            return None

        for key, value in kwargs.items():
            if hasattr(rule, key):
                setattr(rule, key, value)

        rule.updated_at = datetime.utcnow()
        return rule

    def delete(self, session: Session, rule_id: int) -> bool:
        """Delete a consumption rule."""
        rule = self.get_by_id(session, rule_id)
        if not rule:
            return False

        session.delete(rule)
        return True
