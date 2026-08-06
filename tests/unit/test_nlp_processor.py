"""Unit tests for NLP processor."""

import pytest
from src.nlp.processor import NLPProcessor
from src.nlp.dictionary import STOCK_LEVELS, UNIT_ALIASES


class TestNLPProcessorBasic:
    """Test basic NLP processor functionality."""

    def test_processor_initialization(self):
        """Test processor initializes correctly."""
        processor = NLPProcessor()
        assert processor.patterns is not None

    def test_process_returns_dict(self):
        """Test process always returns a dict."""
        processor = NLPProcessor()
        result = processor.process("тест")
        assert isinstance(result, dict)
        assert "success" in result
        assert "command_type" in result
        assert "data" in result
        assert "message" in result


class TestNLPProcessorPurchase:
    """Test purchase command processing."""

    def test_purchase_simple(self, nlp_processor):
        """Test simple purchase command."""
        result = nlp_processor.process("купил молоко")
        assert result["success"] is True
        assert result["command_type"] == "purchase"
        assert result["data"]["item_name"] == "молоко"

    def test_purchase_with_amount(self, nlp_processor):
        """Test purchase with amount."""
        result = nlp_processor.process("купил молоко 2 литра")
        assert result["success"] is True
        assert result["data"]["amount"] == 2.0
        assert result["data"]["unit"] == "л"

    def test_purchase_quantity_first(self, nlp_processor):
        """Test purchase with quantity before item."""
        result = nlp_processor.process("купил 5 йогуртов")
        assert result["success"] is True
        assert result["data"]["amount"] == 5.0
        assert result["data"]["item_name"] == "йогуртов"

    def test_purchase_message_content(self, nlp_processor):
        """Test purchase response message."""
        result = nlp_processor.process("купил молоко 2л")
        assert "Зафиксирована покупка" in result["message"]
        assert "молоко" in result["message"]


class TestNLPProcessorUpdate:
    """Test stock update command processing."""

    def test_update_half(self, nlp_processor):
        """Test update with 'половина'."""
        result = nlp_processor.process("молока осталось половина")
        assert result["success"] is True
        assert result["command_type"] == "update"
        assert result["data"]["stock_level"] == 0.5

    def test_update_out_of_stock(self, nlp_processor):
        """Test update with out of stock."""
        result = nlp_processor.process("молоко закончилось")
        assert result["success"] is True
        assert result["data"]["stock_level"] == 0.0

    def test_update_low_stock(self, nlp_processor):
        """Test update with low stock levels."""
        test_cases = [
            ("сахара совсем мало", 0.1),
            ("сахара мало", 0.25),
            ("сахара немного", 0.25),
        ]
        for text, expected_level in test_cases:
            result = nlp_processor.process(text)
            assert result["success"] is True, f"Failed: {text}"
            assert result["data"]["stock_level"] == expected_level, f"Failed: {text}"

    def test_update_message_content(self, nlp_processor):
        """Test update response message."""
        result = nlp_processor.process("молока осталось половина")
        assert "Обновлён остаток" in result["message"]


class TestNLPProcessorStatus:
    """Test status query command processing."""

    def test_status_all_items(self, nlp_processor):
        """Test status query for all items."""
        result = nlp_processor.process("что есть дома")
        assert result["success"] is True
        assert result["command_type"] == "status_all"

    def test_status_shopping_list(self, nlp_processor):
        """Test shopping list query."""
        result = nlp_processor.process("список покупок")
        assert result["success"] is True
        assert result["command_type"] == "status_all"

    def test_status_specific_item(self, nlp_processor):
        """Test status query for specific item."""
        result = nlp_processor.process("статус молоко")
        assert result["success"] is True
        assert result["command_type"] == "status_item"
        assert result["data"]["item_name"] == "молоко"

    def test_status_how_much_left(self, nlp_processor):
        """Test 'сколько осталось' query."""
        result = nlp_processor.process("сколько осталось кефир")
        assert result["success"] is True
        assert result["command_type"] == "status_item"
        assert result["data"]["item_name"] == "кефир"


class TestNLPProcessorUnknown:
    """Test unknown command handling."""

    def test_unknown_command(self, nlp_processor):
        """Test unknown command returns error."""
        result = nlp_processor.process("непонятная команда")
        assert result["success"] is False
        assert result["command_type"] is None
        assert "не распознана" in result["message"]

    def test_gibberish(self, nlp_processor):
        """Test gibberish text."""
        result = nlp_processor.process("абракадабра")
        assert result["success"] is False


class TestNLPDictionary:
    """Test NLP dictionary functions."""

    def test_stock_levels_dictionary(self):
        """Test stock levels dictionary values."""
        assert STOCK_LEVELS["совсем мало"] == 0.10
        assert STOCK_LEVELS["половина"] == 0.50
        assert STOCK_LEVELS["нет"] == 0.0
        assert STOCK_LEVELS["закончилось"] == 0.0

    def test_get_stock_level(self):
        """Test get_stock_level function."""
        from src.nlp.dictionary import get_stock_level
        
        assert get_stock_level("совсем мало") == 0.10
        assert get_stock_level("половина") == 0.50
        assert get_stock_level("нет") == 0.0
        assert get_stock_level("неизвестно") is None

    def test_unit_aliases(self):
        """Test unit normalization."""
        from src.nlp.dictionary import normalize_unit
        
        assert normalize_unit("литр") == "л"
        assert normalize_unit("литра") == "л"
        assert normalize_unit("килограмм") == "кг"
        assert normalize_unit("штук") == "шт"
        assert normalize_unit("неизвестно") == "неизвестно"
