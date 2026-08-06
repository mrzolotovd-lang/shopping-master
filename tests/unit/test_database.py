"""Unit tests for database operations."""

import pytest
from sqlalchemy.orm import Session

from src.database.models import Item, Category, ConsumptionRule, User
from src.database.repositories.item_repo import ItemRepository
from src.database.repositories.category_repo import CategoryRepository
from src.database.repositories.rule_repo import ConsumptionRuleRepository
from src.database.repositories.user_repo import UserRepository


class TestUserRepository:
    """Test user repository operations."""

    def test_create_user(self, db_session, db_connection):
        """Test creating a user."""
        repo = UserRepository(db_connection)
        user = repo.create(db_session, name="Test User", priority=1)
        db_session.commit()
        
        assert user.id is not None
        assert user.name == "Test User"
        assert user.priority == 1

    def test_get_user_by_name(self, db_session, db_connection):
        """Test getting user by name."""
        repo = UserRepository(db_connection)
        repo.create(db_session, name="Test User", priority=1)
        db_session.commit()
        
        user = repo.get_by_name(db_session, "Test User")
        assert user is not None
        assert user.name == "Test User"

    def test_get_user_by_telegram_id(self, db_session, db_connection):
        """Test getting user by Telegram ID."""
        repo = UserRepository(db_connection)
        repo.create(db_session, name="Test User", telegram_id=12345)
        db_session.commit()
        
        user = repo.get_by_telegram_id(db_session, 12345)
        assert user is not None
        assert user.telegram_id == 12345


class TestConsumptionRuleRepository:
    """Test consumption rule repository operations."""

    def test_create_rule(self, db_session, db_connection):
        """Test creating a consumption rule."""
        repo = ConsumptionRuleRepository(db_connection)
        rule = repo.create(
            db_session,
            name="Test Rule",
            rule_type="percentage_daily",
            value=5.0
        )
        db_session.commit()
        
        assert rule.id is not None
        assert rule.name == "Test Rule"
        assert rule.rule_type == "percentage_daily"
        assert float(rule.value) == 5.0

    def test_get_rule_by_name(self, db_session, db_connection):
        """Test getting rule by name."""
        repo = ConsumptionRuleRepository(db_connection)
        repo.create(db_session, name="Test Rule", rule_type="percentage_daily", value=5.0)
        db_session.commit()
        
        rule = repo.get_by_name(db_session, "Test Rule")
        assert rule is not None
        assert rule.name == "Test Rule"


class TestCategoryRepository:
    """Test category repository operations."""

    def test_create_category(self, db_session, db_connection):
        """Test creating a category."""
        repo = CategoryRepository(db_connection)
        category = repo.create(db_session, name="Test Category")
        db_session.commit()
        
        assert category.id is not None
        assert category.name == "Test Category"

    def test_get_all_categories(self, db_session, db_connection):
        """Test getting all categories."""
        repo = CategoryRepository(db_connection)
        repo.create(db_session, name="Category 1")
        repo.create(db_session, name="Category 2")
        db_session.commit()
        
        categories = repo.get_all(db_session)
        assert len(categories) == 2


class TestItemRepository:
    """Test item repository operations."""

    def test_create_item(self, db_session, db_connection):
        """Test creating an item."""
        item_repo = ItemRepository(db_connection)
        item = item_repo.create(
            db_session,
            name="Test Item",
            package_size=1.0,
            unit="шт"
        )
        db_session.commit()
        
        assert item.id is not None
        assert item.name == "Test Item"
        assert float(item.package_size) == 1.0

    def test_get_item_by_name(self, db_session, db_connection):
        """Test getting item by name."""
        item_repo = ItemRepository(db_connection)
        item_repo.create(db_session, name="Test Item")
        db_session.commit()
        
        item = item_repo.get_by_name(db_session, "test item")
        assert item is not None
        assert item.name == "Test Item"

    def test_update_stock_level(self, db_session, db_connection):
        """Test updating stock level."""
        item_repo = ItemRepository(db_connection)
        item_repo.create(db_session, name="Test Item", package_size=1.0)
        db_session.commit()
        
        result = item_repo.update_stock_level(db_session, "test item", 5.0)
        db_session.commit()
        
        assert result["success"] is True
        item = item_repo.get_by_name(db_session, "test item")
        assert float(item.current_stock) == 5.0

    def test_process_purchase(self, db_session, db_connection):
        """Test processing a purchase."""
        item_repo = ItemRepository(db_connection)
        item_repo.create(db_session, name="Test Item", package_size=1.0)
        db_session.commit()
        
        result = item_repo.process_purchase(db_session, "test item", 2.0)
        db_session.commit()
        
        assert result["success"] is True
        item = item_repo.get_by_name(db_session, "test item")
        assert float(item.current_stock) == 2.0
        assert item.purchase_count == 1

    def test_get_all_active(self, db_session, db_connection):
        """Test getting all active items."""
        item_repo = ItemRepository(db_connection)
        item_repo.create(db_session, name="Item 1")
        item_repo.create(db_session, name="Item 2")
        db_session.commit()
        
        items = item_repo.get_all_active(db_session)
        assert len(items) == 2
