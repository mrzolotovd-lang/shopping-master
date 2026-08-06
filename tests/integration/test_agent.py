"""Integration tests for the agent."""

import pytest
from src.core.agent import Agent
from src.database.connection import DatabaseConnection


class TestAgentInitialization:
    """Test agent initialization."""

    def test_agent_creates_repos(self, db_connection):
        """Test agent initializes repositories."""
        agent = Agent(db_connection)
        assert agent.item_repo is not None
        assert agent.shopping_repo is not None
        assert agent.consumption_engine is not None
        assert agent.threshold_checker is not None


class TestAgentConsumption:
    """Test agent consumption functionality."""

    def test_run_daily_consumption(self, db_connection):
        """Test running daily consumption."""
        # Setup: Create test item
        from src.database.repositories.item_repo import ItemRepository
        from src.database.repositories.rule_repo import ConsumptionRuleRepository
        
        session = db_connection.get_session()
        rule_repo = ConsumptionRuleRepository(db_connection)
        item_repo = ItemRepository(db_connection)
        
        rule = rule_repo.create(session, "Test Rule", "percentage_daily", 10.0)
        item = item_repo.create(
            session,
            name="Test Item",
            package_size=100.0,
            consumption_rule_id=rule.id
        )
        item.current_stock = 100.0
        session.commit()
        session.close()
        
        # Run consumption
        agent = Agent(db_connection)
        result = agent.run_daily_consumption()
        
        assert result["processed"] >= 1
        assert result["updated"] >= 1
        
        # Verify stock decreased
        session = db_connection.get_session()
        updated_item = item_repo.get_by_name(session, "Test Item")
        assert float(updated_item.current_stock) < 100.0
        session.close()


class TestAgentThresholds:
    """Test agent threshold checking."""

    def test_threshold_adds_to_shopping_list(self, db_connection):
        """Test that low stock items are added to shopping list."""
        from src.database.repositories.item_repo import ItemRepository
        
        session = db_connection.get_session()
        item_repo = ItemRepository(db_connection)
        
        # Create item with very low stock (below 10% threshold)
        item = item_repo.create(
            session,
            name="Low Stock Item",
            package_size=100.0,
            reorder_threshold=10.0
        )
        item.current_stock = 5.0  # 5% of package_size
        session.commit()
        session.close()
        
        # Run threshold check
        agent = Agent(db_connection)
        result = agent.run_threshold_check()
        
        assert result["checked"] >= 1
        assert result["added"] >= 1
        
        # Verify item is in shopping list
        session = db_connection.get_session()
        shopping_list = agent.get_shopping_list("pending")
        assert len(shopping_list) > 0
        session.close()


class TestAgentWorkflow:
    """Test complete agent workflow."""

    def test_purchase_then_consume(self, db_connection):
        """Test purchase followed by consumption."""
        from src.database.repositories.rule_repo import ConsumptionRuleRepository
        from src.database.repositories.item_repo import ItemRepository
        
        agent = Agent(db_connection)
        session = db_connection.get_session()
        
        # Create consumption rule
        rule_repo = ConsumptionRuleRepository(db_connection)
        rule = rule_repo.create(session, "Test Rule", "percentage_daily", 10.0)
        session.commit()
        
        # Create item with consumption rule
        item_repo = ItemRepository(db_connection)
        item = item_repo.create(
            session,
            name="Workflow Test Item",
            package_size=10.0,
            consumption_rule_id=rule.id
        )
        item.current_stock = 0
        session.commit()
        session.close()
        
        # Process purchase
        result = agent.process_purchase("Workflow Test Item", 10.0)
        assert result["success"] is True
        
        # Run consumption
        consume_result = agent.run_daily_consumption()
        assert consume_result["processed"] >= 1
        
        # Verify stock decreased (10 - 10% = 9)
        session = db_connection.get_session()
        item = item_repo.get_by_name(session, "Workflow Test Item")
        assert float(item.current_stock) < 10.0
        session.close()
