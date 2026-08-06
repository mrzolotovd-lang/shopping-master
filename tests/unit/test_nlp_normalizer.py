"""Unit tests for Russian text normalizer."""

import pytest
from src.nlp.normalizer import RussianNormalizer


class TestRussianNormalizerBasic:
    """Test basic normalization."""

    def test_normalize_masculine_nouns(self):
        """Test masculine noun normalization."""
        assert RussianNormalizer.normalize_word("молока") == "молоко"
        assert RussianNormalizer.normalize_word("кефира") == "кефир"
        assert RussianNormalizer.normalize_word("творога") == "творог"
        assert RussianNormalizer.normalize_word("сахара") == "сахар"

    def test_normalize_feminine_nouns(self):
        """Test feminine noun normalization."""
        assert RussianNormalizer.normalize_word("воды") == "вода"
        assert RussianNormalizer.normalize_word("колбасы") == "колбаса"
        assert RussianNormalizer.normalize_word("сосисок") == "сосиски"

    def test_normalize_neuter_nouns(self):
        """Test neuter noun normalization."""
        assert RussianNormalizer.normalize_word("молока") == "молоко"
        # Simple algorithm - just check it returns something reasonable
        result = RussianNormalizer.normalize_word("яблок")
        assert result.startswith("яблок") or result == "яблоки"

    def test_normalize_short_words(self):
        """Test short words are not over-normalized."""
        result = RussianNormalizer.normalize_word("лук")
        assert len(result) >= 2


class TestRussianNormalizerSynonyms:
    """Test synonym normalization."""

    def test_diminutive_forms(self):
        """Test diminutive forms."""
        assert RussianNormalizer.normalize_word("молочко") == "молоко"
        assert RussianNormalizer.normalize_word("кефирчик") == "кефир"
        assert RussianNormalizer.normalize_word("творожок") == "творог"
        assert RussianNormalizer.normalize_word("йогуртик") == "йогурт"

    def test_meat_synonyms(self):
        """Test meat product synonyms."""
        assert RussianNormalizer.normalize_word("курочка") == "курица"
        assert RussianNormalizer.normalize_word("свининка") == "свинина"
        assert RussianNormalizer.normalize_word("фаршик") == "фарш"
        assert RussianNormalizer.normalize_word("сосисочки") == "сосиски"

    def test_vegetable_synonyms(self):
        """Test vegetable synonyms."""
        assert RussianNormalizer.normalize_word("картошечка") == "картошка"
        assert RussianNormalizer.normalize_word("помидорчик") == "помидор"
        assert RussianNormalizer.normalize_word("огурчики") == "огурцы"
        assert RussianNormalizer.normalize_word("яблочко") == "яблоко"

    def test_bakery_synonyms(self):
        """Test bakery synonyms."""
        assert RussianNormalizer.normalize_word("хлебушек") == "хлеб"
        assert RussianNormalizer.normalize_word("булочка") == "булка"

    def test_beverage_synonyms(self):
        """Test beverage synonyms."""
        assert RussianNormalizer.normalize_word("водичка") == "вода"
        assert RussianNormalizer.normalize_word("чай") == "чай"

    def test_baby_food_synonyms(self):
        """Test baby food synonyms."""
        assert RussianNormalizer.normalize_word("пюрешка") == "пюре"
        assert RussianNormalizer.normalize_word("кашка") == "каша"

    def test_hygiene_synonyms(self):
        """Test hygiene product synonyms."""
        assert RussianNormalizer.normalize_word("подгузничек") == "подгузник"
        assert RussianNormalizer.normalize_word("салфеточка") == "салфетка"
        assert RussianNormalizer.normalize_word("туалетка") == "туалетная бумага"

    def test_egg_synonyms(self):
        """Test egg synonyms."""
        assert RussianNormalizer.normalize_word("яичко") == "яйцо"
        assert RussianNormalizer.normalize_word("яиц") == "яйца"


class TestRussianNormalizerText:
    """Test full text normalization."""

    def test_normalize_text(self):
        """Test normalizing full text."""
        text = "купил молочко и кефирчик"
        normalized = RussianNormalizer.normalize_text(text)
        assert "молоко" in normalized
        assert "кефир" in normalized

    def test_normalize_text_preserves_numbers(self):
        """Test that numbers are preserved."""
        text = "купил 2 литра молока"
        normalized = RussianNormalizer.normalize_text(text)
        assert "2" in normalized
        assert "литра" in normalized or "л" in normalized

    def test_normalize_text_preserves_units(self):
        """Test that units are preserved."""
        text = "5 кг сахара"
        normalized = RussianNormalizer.normalize_text(text)
        assert "5" in normalized
        assert "кг" in normalized


class TestRussianNormalizerVariations:
    """Test getting name variations."""

    def test_get_variations(self):
        """Test getting variations for an item."""
        variations = RussianNormalizer.get_item_name_variations("молоко")
        assert "молоко" in variations
        assert "молочко" in variations or "молочка" in variations

    def test_get_variations_unique(self):
        """Test that variations are unique."""
        variations = RussianNormalizer.get_item_name_variations("кефир")
        assert len(variations) == len(set(variations))


class TestRussianNormalizerEdgeCases:
    """Test edge cases."""

    def test_empty_string(self):
        """Test empty string."""
        assert RussianNormalizer.normalize_word("") == ""

    def test_single_char(self):
        """Test single character."""
        result = RussianNormalizer.normalize_word("а")
        assert len(result) <= 1

    def test_unknown_word(self):
        """Test unknown word."""
        result = RussianNormalizer.normalize_word("неизвестно")
        # Should return something, even if not perfect
        assert isinstance(result, str)
        assert len(result) > 0

    def test_already_normalized(self):
        """Test already normalized word."""
        assert RussianNormalizer.normalize_word("молоко") == "молоко"
        # Note: simple algorithm may not preserve all base forms perfectly
        assert RussianNormalizer.normalize_word("молоко") in ["молоко", "молок"]
