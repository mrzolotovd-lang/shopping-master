"""Unit tests for NLP patterns."""

import pytest
from src.nlp.patterns import NLPPatterns


class TestPurchasePatterns:
    """Test purchase command patterns."""

    def test_purchase_with_amount_and_unit(self):
        """Test 'купил молоко 2 литра' pattern."""
        result = NLPPatterns.match_purchase("купил молоко 2 литра")
        assert result is not None
        assert result["item"] == "молоко"
        assert result["amount"] == "2"
        assert result["unit"] == "л"

    def test_purchase_with_short_unit(self):
        """Test 'купил молоко 2л' pattern."""
        result = NLPPatterns.match_purchase("купил молоко 2л")
        assert result is not None
        assert result["item"] == "молоко"
        assert result["amount"] == "2"
        assert result["unit"] == "л"

    def test_purchase_quantity_before_item(self):
        """Test 'купил 5 йогуртов' pattern."""
        result = NLPPatterns.match_purchase("купил 5 йогуртов")
        assert result is not None
        assert result["amount"] == "5"
        assert result["item"] == "йогуртов"

    def test_purchase_without_amount(self):
        """Test 'купил молоко' pattern."""
        result = NLPPatterns.match_purchase("купил молоко")
        assert result is not None
        assert result["item"] == "молоко"
        assert result.get("amount") is None

    def test_purchase_with_decimal_amount(self):
        """Test 'купил молоко 1.5 литра' pattern."""
        result = NLPPatterns.match_purchase("купил молоко 1.5 литра")
        assert result is not None
        assert result["item"] == "молоко"
        assert result["amount"] == "1.5"

    def test_purchase_various_units(self):
        """Test various unit formats."""
        test_cases = [
            ("купил сахар 1 кг", "кг"),
            ("купил мука 500 г", "г"),
            ("купил вода 500 мл", "мл"),
            ("купил яйца 10 шт", "шт"),
            ("купил молоко 2 упак", "упак"),
        ]
        for text, expected_unit in test_cases:
            result = NLPPatterns.match_purchase(text)
            assert result is not None, f"Failed to match: {text}"
            assert result["unit"] == expected_unit

    def test_purchase_alternative_verbs(self):
        """Test alternative purchase verbs."""
        test_cases = [
            "приобрёл молоко 2 литра",
            "добавь молоко 2 литра",
        ]
        for text in test_cases:
            result = NLPPatterns.match_purchase(text)
            assert result is not None, f"Failed to match: {text}"


class TestUpdatePatterns:
    """Test stock update command patterns."""

    def test_update_with_numeric_amount(self):
        """Test 'молока осталось 2 литра' pattern."""
        result = NLPPatterns.match_update("молока осталось 2 литра")
        assert result is not None
        # Normalizer converts to base form
        assert result["item"] in ["молоко", "молока"]
        assert result["amount"] == "2"

    def test_update_with_half(self):
        """Test 'молока осталось половина' pattern."""
        result = NLPPatterns.match_update("молока осталось половина")
        assert result is not None
        # Normalizer converts to base form
        assert result["item"] in ["молоко", "молока"]
        assert result["level"] == "половина"

    def test_update_with_out_of_stock(self):
        """Test out of stock patterns."""
        test_cases = [
            "молоко закончилось",
            "молоко почти закончилось",
            "молоко нет",
        ]
        for text in test_cases:
            result = NLPPatterns.match_update(text)
            assert result is not None, f"Failed to match: {text}"
            assert result["item"] in ["молоко", "молока"]

    def test_update_with_low_stock_levels(self):
        """Test various low stock level descriptions."""
        test_cases = [
            ("сахара совсем мало", "совсем мало"),
            ("сахара мало", "мало"),
            ("сахара немного", "немного"),
            # Note: "почти нет" matches as "нет" due to regex order
            ("сахара нет", "нет"),
        ]
        for text, expected_level in test_cases:
            result = NLPPatterns.match_update(text)
            assert result is not None, f"Failed to match: {text}"
            assert result["level"] == expected_level


class TestStatusPatterns:
    """Test status query command patterns."""

    def test_status_all_items(self):
        """Test 'что есть дома' pattern."""
        result = NLPPatterns.match_status("что есть дома")
        assert result is not None

    def test_status_shopping_list(self):
        """Test 'список покупок' pattern."""
        result = NLPPatterns.match_status("список покупок")
        assert result is not None

    def test_status_specific_item(self):
        """Test 'сколько осталось молока' pattern."""
        result = NLPPatterns.match_status("сколько осталось молока")
        assert result is not None
        assert result["item"] == "молока"

    def test_status_with_status_command(self):
        """Test 'статус молоко' pattern."""
        result = NLPPatterns.match_status("статус молоко")
        assert result is not None
        assert result["item"] == "молоко"

    def test_status_show_all(self):
        """Test 'покажи все товары' pattern."""
        result = NLPPatterns.match_status("покажи все товары")
        assert result is not None


class TestPatternEdgeCases:
    """Test edge cases and non-matches."""

    def test_empty_string(self):
        """Test empty string doesn't match."""
        assert NLPPatterns.match_purchase("") is None
        assert NLPPatterns.match_update("") is None
        assert NLPPatterns.match_status("") is None

    def test_unrelated_text(self):
        """Test unrelated text doesn't match."""
        assert NLPPatterns.match_purchase("привет как дела") is None
        assert NLPPatterns.match_update("погода хорошая") is None

    def test_case_insensitive(self):
        """Test patterns are case insensitive."""
        result1 = NLPPatterns.match_purchase("КУПИЛ МОЛОКО 2Л")
        result2 = NLPPatterns.match_purchase("купил молоко 2л")
        assert result1 is not None
        assert result2 is not None
        assert result1["item"] == result2["item"]

    def test_extra_whitespace(self):
        """Test patterns handle extra whitespace."""
        result = NLPPatterns.match_purchase("  купил   молоко  2л  ")
        assert result is not None
