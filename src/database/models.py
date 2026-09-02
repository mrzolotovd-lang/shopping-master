"""SQLAlchemy database models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base model class."""

    pass


class User(Base):
    """User model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=5)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    items_created: Mapped[list["Item"]] = relationship(
        "Item", back_populates="creator", foreign_keys="Item.created_by"
    )
    shopping_list_items: Mapped[list["ShoppingListItem"]] = relationship(
        "ShoppingListItem", back_populates="user"
    )
    operations: Mapped[list["OperationLog"]] = relationship(
        "OperationLog", back_populates="user"
    )


class ConsumptionRule(Base):
    """Consumption rule model."""

    __tablename__ = "consumption_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    rule_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # percentage_daily, absolute_daily, manual
    value: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    __table_args__ = (
        CheckConstraint(
            "rule_type IN ('percentage_daily', 'absolute_daily', 'manual')",
            name="check_consumption_rule_type",
        ),
    )

    items: Mapped[list["Item"]] = relationship("Item", back_populates="consumption_rule")
    categories: Mapped[list["Category"]] = relationship(
        "Category", back_populates="default_consumption_rule"
    )


class Category(Base):
    """Category model."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    default_consumption_rule_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("consumption_rules.id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    default_consumption_rule: Mapped[Optional["ConsumptionRule"]] = relationship(
        "ConsumptionRule", back_populates="categories"
    )
    items: Mapped[list["Item"]] = relationship("Item", back_populates="category")


class Item(Base):
    """Item model."""

    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"))
    current_stock: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    package_size: Mapped[float] = mapped_column(Numeric(10, 2), default=1)
    unit: Mapped[str] = mapped_column(String(50), default="шт")
    reorder_threshold: Mapped[float] = mapped_column(Numeric(5, 2), default=10)
    consumption_rule_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("consumption_rules.id")
    )
    auto_fill_mode: Mapped[str] = mapped_column(
        String(20), default="ask"
    )  # ask, package, smart
    purchase_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp()
    )
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="items")
    consumption_rule: Mapped[Optional["ConsumptionRule"]] = relationship(
        "ConsumptionRule", back_populates="items"
    )
    creator: Mapped[Optional["User"]] = relationship(
        "User", back_populates="items_created", foreign_keys=[created_by]
    )
    shopping_list_entries: Mapped[list["ShoppingListItem"]] = relationship(
        "ShoppingListItem", back_populates="item"
    )
    operation_logs: Mapped[list["OperationLog"]] = relationship(
        "OperationLog", back_populates="item"
    )

    __table_args__ = (
        CheckConstraint(
            "auto_fill_mode IN ('ask', 'package', 'smart')",
            name="check_auto_fill_mode",
        ),
    )


class ShoppingListItem(Base):
    """Shopping list item model."""

    __tablename__ = "shopping_list"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    quantity: Mapped[float] = mapped_column(Numeric(10, 2), default=1)
    reason: Mapped[str] = mapped_column(String(50), default="threshold")
    status: Mapped[str] = mapped_column(String(20), default="pending")
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    item: Mapped["Item"] = relationship("Item", back_populates="shopping_list_entries")
    user: Mapped[Optional["User"]] = relationship("User", back_populates="shopping_list_items")

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'completed', 'cancelled')",
            name="check_shopping_status",
        ),
        UniqueConstraint("item_id", "status", name="unique_active_item_in_shopping_list"),
    )


class OperationLog(Base):
    """Operation log model (audit trail)."""

    __tablename__ = "operation_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    operation_type: Mapped[str] = mapped_column(String(30), nullable=False)
    old_value: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    new_value: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    comment: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    item: Mapped["Item"] = relationship("Item", back_populates="operation_logs")
    user: Mapped[Optional["User"]] = relationship("User", back_populates="operations")

    __table_args__ = (
        CheckConstraint(
            "operation_type IN ('purchase', 'manual_update', 'auto_consumption', "
            "'added_to_shopping', 'removed_from_shopping', 'rule_change')",
            name="check_operation_type",
        ),
    )
