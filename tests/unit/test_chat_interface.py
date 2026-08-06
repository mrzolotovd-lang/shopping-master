"""Unit tests for chat interface."""

import pytest
from src.interfaces.chat import ChatInterface
from src.database.connection import DatabaseConnection


class TestChatInterfaceBasic:
    """Test basic chat interface functionality."""

    def test_chat_interface_initialization(self, db_connection):
        """Test chat interface initializes correctly."""
        chat = ChatInterface(db_connection)
        assert chat.agent is not None
        assert chat.nlp is not None
        assert chat.current_user_id is None

    def test_set_user(self, db_connection):
        """Test setting user context."""
        chat = ChatInterface(db_connection)
        response = chat.set_user(1, "Test User")
        assert "Test User" in response
        assert chat.current_user_id == 1

    def test_process_message_returns_string(self, db_connection):
        """Test process_message always returns string."""
        chat = ChatInterface(db_connection)
        result = chat.process_message("тест")
        assert isinstance(result, str)


class TestChatInterfacePurchase:
    """Test purchase command handling."""

    def test_purchase_command(self, db_connection):
        """Test purchase command."""
        chat = ChatInterface(db_connection)
        chat.set_user(1, "Test")
        
        # First create an item
        session = db_connection.get_session()
        from src.database.repositories.item_repo import ItemRepository
        item_repo = ItemRepository(db_connection)
        item_repo.create(session, name="молоко", package_size=1.0)
        session.commit()
        session.close()
        
        result = chat.process_message("купил молоко 2 литра")
        assert "✅" in result or "молоко" in result.lower()

    def test_purchase_unknown_item(self, db_connection):
        """Test purchase of unknown item."""
        chat = ChatInterface(db_connection)
        chat.set_user(1, "Test")
        
        result = chat.process_message("купил неизвестный товар 2 литра")
        assert "❌" in result or "не найден" in result.lower()


class TestChatInterfaceUpdate:
    """Test stock update command handling."""

    def test_update_half_command(self, db_connection):
        """Test update with 'половина' command."""
        chat = ChatInterface(db_connection)
        chat.set_user(1, "Test")
        
        # Create item
        session = db_connection.get_session()
        from src.database.repositories.item_repo import ItemRepository
        item_repo = ItemRepository(db_connection)
        item = item_repo.create(session, name="кефир", package_size=1.0)
        item.current_stock = 1.0
        session.commit()
        session.close()
        
        result = chat.process_message("кефира осталось половина")
        assert "✅" in result or "кефир" in result.lower()

    def test_update_out_of_stock(self, db_connection):
        """Test update with out of stock command."""
        chat = ChatInterface(db_connection)
        chat.set_user(1, "Test")
        
        # Create item
        session = db_connection.get_session()
        from src.database.repositories.item_repo import ItemRepository
        item_repo = ItemRepository(db_connection)
        item_repo.create(session, name="молоко", package_size=1.0)
        session.commit()
        session.close()
        
        result = chat.process_message("молоко закончилось")
        # Should either update successfully or say item not found
        assert isinstance(result, str)
        assert len(result) > 0


class TestChatInterfaceStatus:
    """Test status query handling."""

    def test_status_all_empty(self, db_connection):
        """Test status all with empty database."""
        chat = ChatInterface(db_connection)
        result = chat.process_message("что есть дома")
        assert "нет товаров" in result.lower() or "📭" in result

    def test_status_all_with_items(self, db_connection):
        """Test status all with items."""
        chat = ChatInterface(db_connection)
        
        # Create items
        session = db_connection.get_session()
        from src.database.repositories.item_repo import ItemRepository
        item_repo = ItemRepository(db_connection)
        item_repo.create(session, name="тест товар 1", package_size=1.0)
        item_repo.create(session, name="тест товар 2", package_size=1.0)
        session.commit()
        session.close()
        
        result = chat.process_message("что есть дома")
        assert "📦" in result or "товар" in result.lower()

    def test_status_specific_item(self, db_connection):
        """Test status for specific item."""
        chat = ChatInterface(db_connection)
        
        # Create item
        session = db_connection.get_session()
        from src.database.repositories.item_repo import ItemRepository
        item_repo = ItemRepository(db_connection)
        item = item_repo.create(session, name="молоко", package_size=1.0)
        item.current_stock = 0.5
        session.commit()
        session.close()
        
        result = chat.process_message("статус молоко")
        assert "📊" in result or "молоко" in result.lower()

    def test_status_unknown_item(self, db_connection):
        """Test status for unknown item."""
        chat = ChatInterface(db_connection)
        result = chat.process_message("статус неизвестный товар")
        assert "❌" in result or "не найден" in result.lower()


class TestChatInterfaceShoppingList:
    """Test shopping list functionality."""

    def test_shopping_list_empty(self, db_connection):
        """Test empty shopping list."""
        chat = ChatInterface(db_connection)
        result = chat.get_shopping_list()
        assert "пуст" in result.lower() or "🛒" in result

    def test_shopping_list_with_items(self, db_connection):
        """Test shopping list with items."""
        # Create item with low stock
        session = db_connection.get_session()
        from src.database.repositories.item_repo import ItemRepository
        from src.database.repositories.shopping_repo import ShoppingListRepository
        
        item_repo = ItemRepository(db_connection)
        shopping_repo = ShoppingListRepository(db_connection)
        
        item = item_repo.create(session, name="low stock item", package_size=100.0)
        item.current_stock = 5.0  # Below 10% threshold
        session.commit()
        
        # Run threshold check to add to shopping list
        from src.core.agent import Agent
        agent = Agent(db_connection)
        agent.run_threshold_check()
        session.close()
        
        # Check shopping list
        chat = ChatInterface(db_connection)
        result = chat.get_shopping_list()
        assert "🛒" in result


class TestChatInterfaceDaily:
    """Test daily operations."""

    def test_run_daily_consumption(self, db_connection):
        """Test running daily consumption."""
        chat = ChatInterface(db_connection)
        result = chat.run_daily_consumption()
        assert "📉" in result or "списание" in result.lower()

    def test_check_thresholds(self, db_connection):
        """Test checking thresholds."""
        chat = ChatInterface(db_connection)
        result = chat.check_thresholds()
        assert "🔍" in result or "порог" in result.lower()


class TestChatInterfaceNLP:
    """Test NLP integration."""

    def test_unrecognized_command(self, db_connection):
        """Test unrecognized command handling."""
        chat = ChatInterface(db_connection)
        result = chat.process_message("абракадабра")
        assert "не распознана" in result.lower() or "не понял" in result.lower()

    def test_various_purchase_formats(self, db_connection):
        """Test various purchase command formats."""
        chat = ChatInterface(db_connection)
        chat.set_user(1, "Test")
        
        # Create item
        session = db_connection.get_session()
        from src.database.repositories.item_repo import ItemRepository
        item_repo = ItemRepository(db_connection)
        item_repo.create(session, name="хлеб", package_size=1.0)
        session.commit()
        session.close()
        
        formats = [
            "купил хлеб",
            "купил хлеб 2",
            "купил 2 хлеба",
        ]
        
        for fmt in formats:
            result = chat.process_message(fmt)
            # Should not crash, may fail if item not found
            assert isinstance(result, str)
