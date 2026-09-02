"""Russian text normalizer for NLP."""

import re
from typing import Optional


class RussianNormalizer:
    """Normalize Russian text to dictionary forms."""

    # Words that should NOT be normalized (base forms)
    PRESERVE_WORDS = {
        'вода', 'еда', 'еде', 'еду', 'кофе', 'чай', 'сок',
        'хлеб', 'сыр', 'лук', 'мак', 'сок', 'йогурт', 'кефир',
        'творог', 'сахар', 'соль', 'масло', 'молоко', 'сметана',
    }

    # Genitive case mappings (most common for inventory context)
    GENITIVE_MAPPINGS = {
        'молока': 'молоко',
        'кефира': 'кефир',
        'творога': 'творог',
        'сахара': 'сахар',
        'соли': 'соль',
        'воды': 'вода',
        'хлеба': 'хлеб',
        'масла': 'масло',
        'сыра': 'сыр',
        'лука': 'лук',
        'йогурта': 'йогурт',
        'сметаны': 'сметана',
        'колбасы': 'колбаса',
        'курицы': 'курица',
        'говядины': 'говядина',
        'свинины': 'свинина',
        'рыбы': 'рыба',
        'гречки': 'гречка',
        'риса': 'рис',
        'муки': 'мука',
    }

    # Common product synonyms
    PRODUCT_SYNONYMS = {
        # Молочные продукты
        'молочко': 'молоко',
        'молочка': 'молоко',
        'кефирчик': 'кефир',
        'творожок': 'творог',
        'сметанка': 'сметана',
        'йогуртик': 'йогурт',
        'сырок': 'сыр',
        
        # Мясо
        'курочка': 'курица',
        'курочку': 'курица',
        'свининка': 'свинина',
        'говядинка': 'говядина',
        'фаршик': 'фарш',
        'сосисочки': 'сосиски',
        'колбаска': 'колбаса',
        
        # Овощи/Фрукты
        'картошечка': 'картошка',
        'картошку': 'картошка',
        'помидорчик': 'помидор',
        'помидорчики': 'помидоры',
        'огурчик': 'огурец',
        'огурчики': 'огурцы',
        'яблочко': 'яблоко',
        'яблочки': 'яблоки',
        'бананчик': 'банан',
        
        # Бакалея
        'сахарок': 'сахар',
        'соль': 'соль',
        'маслице': 'масло',
        'мука': 'мука',
        'крупка': 'крупа',
        'рис': 'рис',
        'гречка': 'гречка',
        'макарошки': 'макароны',
        'спагетти': 'макароны',
        
        # Хлеб
        'хлебушек': 'хлеб',
        'хлебушок': 'хлеб',
        'батончик': 'батон',
        'булочка': 'булка',
        
        # Напитки
        'водичка': 'вода',
        'чай': 'чай',
        'кофе': 'кофе',
        'сок': 'сок',
        
        # Детское
        'пюрешка': 'пюре',
        'кашка': 'каша',
        'смесь': 'смесь',
        
        # Бытовая химия
        'порошок': 'порошок',
        'средство': 'средство',
        'мыло': 'мыло',
        'шампунь': 'шампунь',
        
        # Гигиена
        'подгузничек': 'подгузник',
        'подгузники': 'подгузник',
        'салфеточка': 'салфетка',
        'салфетки': 'салфетка',
        'туалетка': 'туалетная бумага',
        'бумага': 'туалетная бумага',
        
        # Яйца
        'яичко': 'яйцо',
        'яички': 'яйца',
        'яиц': 'яйца',
        'яйца': 'яйца',
    }

    # Words that should be normalized to specific forms
    SPECIAL_CASES = {
        'яиц': 'яйца',
        'молока': 'молоко',
        'кефира': 'кефир',
        'творога': 'творог',
        'сахара': 'сахар',
        'соли': 'соль',
        'воды': 'вода',
        'хлеба': 'хлеб',
        'масла': 'масло',
        'сыра': 'сыр',
        'колбасы': 'колбаса',
        'сосисок': 'сосиски',
        'помидоров': 'помидоры',
        'огурцов': 'огурцы',
        'яблок': 'яблоки',
        'бананов': 'бананы',
        'картошки': 'картошка',
        'лука': 'лук',
        'чеснока': 'чеснок',
        'моркови': 'морковь',
        'капусты': 'капуста',
        'свеклы': 'свекла',
    }

    @classmethod
    def normalize_word(cls, word: str) -> str:
        """Normalize a single word to dictionary form."""
        word = word.lower().strip()

        # Preserve known base forms
        if word in cls.PRESERVE_WORDS:
            return word

        # Check special cases first
        if word in cls.SPECIAL_CASES:
            return cls.SPECIAL_CASES[word]

        # Check genitive mappings (most common in "осталось X" context)
        if word in cls.GENITIVE_MAPPINGS:
            return cls.GENITIVE_MAPPINGS[word]

        # Check synonyms
        if word in cls.PRODUCT_SYNONYMS:
            return cls.PRODUCT_SYNONYMS[word]

        # For short words (2-3 chars), return as-is
        if len(word) <= 3:
            return word

        # Try to find base form by checking common patterns
        normalized = cls._try_base_forms(word)

        # Check if normalized form is in synonyms (reverse lookup)
        if normalized in cls.PRODUCT_SYNONYMS:
            return cls.PRODUCT_SYNONYMS[normalized]

        return normalized

    @classmethod
    def _try_base_forms(cls, word: str) -> str:
        """Try to find base form by removing common endings."""
        # Words ending in 'а' after consonant often genitive singular
        if word.endswith('а') and len(word) > 4:
            # Check if removing 'а' gives a known word
            base = word[:-1]
            if base in cls.PRESERVE_WORDS or base in cls.PRODUCT_SYNONYMS:
                return base
            # For most food words, 'а' ending is genitive
            if base.endswith(('л', 'р', 'н', 'с', 'т', 'к')):
                return base

        # Words ending in 'ы' often plural genitive
        if word.endswith('ы') and len(word) > 4:
            base = word[:-1]
            if base in cls.PRESERVE_WORDS:
                return base

        # Words ending in 'и' 
        if word.endswith('и') and len(word) > 4:
            base = word[:-1]
            if base in cls.PRESERVE_WORDS:
                return base

        return word

    @classmethod
    def normalize_text(cls, text: str) -> str:
        """Normalize entire text."""
        words = text.split()
        normalized_words = []

        for word in words:
            # Keep numbers and units as-is
            if re.match(r'^\d+(\.\d+)?$', word):
                normalized_words.append(word)
            elif re.match(r'^(л|кг|г|мл|шт|упак)$', word.lower()):
                normalized_words.append(word.lower())
            else:
                normalized_words.append(cls.normalize_word(word))

        return ' '.join(normalized_words)

    @classmethod
    def get_item_name_variations(cls, item_name: str) -> list[str]:
        """Get all possible name variations for an item."""
        variations = [item_name.lower()]

        # Add normalized form
        normalized = cls.normalize_word(item_name)
        if normalized != item_name.lower():
            variations.append(normalized)

        # Add synonyms
        for synonym, base in cls.PRODUCT_SYNONYMS.items():
            if base == item_name.lower() or normalized == base:
                variations.append(synonym)

        return list(set(variations))
