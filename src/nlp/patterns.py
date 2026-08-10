"""NLP regex patterns for Russian language."""

import re
from typing import Optional

from .normalizer import RussianNormalizer


class NLPPatterns:
    """Regex patterns for NLP processing."""

    PURCHASE_PATTERNS = [
        # "купил молоко 2 литра" / "купил молоко 2л"
        r"купил\s+(?P<item>[а-яА-ЯёЁ\s]+?)\s+(?P<amount>\d+(?:\.\d+)?)\s*(?P<unit>л|кг|г|мл|шт|упак|упаковка)?",
        # "купил 5 йогуртов" / "купил 10 яиц"
        r"купил\s+(?P<amount>\d+(?:\.\d+)?)\s+(?P<item>[а-яА-ЯёЁ\s]+)",
        # "купил молоко" (без количества)
        r"купил\s+(?P<item>[а-яА-ЯёЁ\s]+)",
        # "приобрёл молоко 2 литра"
        r"приобрёл\s+(?P<item>[а-яА-ЯёЁ\s]+?)\s+(?P<amount>\d+(?:\.\d+)?)\s*(?P<unit>л|кг|г|мл|шт|упак|упаковка)?",
        # "добавь молоко"
        r"добавь\s+(?P<item>[а-яА-ЯёЁ\s]+?)\s+(?P<amount>\d+(?:\.\d+)?)\s*(?P<unit>л|кг|г|мл|шт|упак|упаковка)?",
        # "взял молоко" (colloquial)
        r"взял\s+(?P<item>[а-яА-ЯёЁ\s]+?)\s+(?P<amount>\d+(?:\.\d+)?)\s*(?P<unit>л|кг|г|мл|шт|упак|упаковка)?",
    ]

    UPDATE_PATTERNS = [
        # "молока осталось 2 литра" / "молока осталось 2л"
        r"(?P<item>[а-яА-ЯёЁ\s]+?)\s+осталось\s+(?P<amount>\d+(?:\.\d+)?)\s*(?P<unit>л|кг|г|мл|шт)?",
        # "молока осталось половина"
        r"(?P<item>[а-яА-ЯёЁ\s]+?)\s+осталось\s+(?P<level>половина|пол-упаковки|пол упаковки)",
        # "молоко закончилось" / "молоко нет" / "кефир кончился"
        r"(?P<item>[а-яА-ЯёЁ\s]+?)\s+(?P<level>почти\s+закончилось|закончилось|кончилось|нет)",
        # "сахара совсем мало" / "сахара мало" / "сахара немного"
        r"(?P<item>[а-яА-ЯёЁ\s]+?)\s+(?P<level>совсем\s+мало|почти\s+нет|мало|немного|много|почти\s+полная|чуть[\s-]?чуть)",
        # "молока на донышке" (idiomatic)
        r"(?P<item>[а-яА-ЯёЁ\s]+?)\s+на\s+донышке",
    ]

    STATUS_PATTERNS = [
        # "что есть дома?"
        r"что\s+есть\s+дома",
        # "список покупок"
        r"список\s+покупок",
        # "сколько осталось молока?" — до конца строки или знака вопроса
        r"сколько\s+осталось\s+(?P<item>[а-яА-ЯёЁ\s]+?)(?:\?|$)",
        # "статус молоко"
        r"статус\s+(?P<item>[а-яА-ЯёЁ\s]+)",
        # "покажи молоко"
        r"покажи\s+(?P<item>[а-яА-ЯёЁ\s]+)",
        # "покажи все товары"
        r"покажи\s+все\s+товары",
        # "что у нас есть"
        r"что\s+у\s+нас\s+есть",
        # "есть ли молоко"
        r"есть\s+ли\s+(?P<item>[а-яА-ЯёЁ\s]+)",
    ]

    @classmethod
    def match_purchase(cls, text: str) -> Optional[dict]:
        """Match purchase command."""
        text = text.lower().strip()
        for pattern in cls.PURCHASE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                groups = match.groupdict()
                item = groups.get('item', '').strip()
                if item and len(item) > 1:
                    # Normalize item name
                    groups['item'] = RussianNormalizer.normalize_word(item)
                    return groups
        return None

    @classmethod
    def match_update(cls, text: str) -> Optional[dict]:
        """Match stock update command."""
        text = text.lower().strip()
        for pattern in cls.UPDATE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                groups = match.groupdict()
                item = groups.get('item', '').strip()
                if item and len(item) > 1:
                    # Normalize item name
                    groups['item'] = RussianNormalizer.normalize_word(item)
                    # Handle idiomatic expressions
                    if 'на донышке' in text:
                        groups['level'] = 'совсем мало'
                    return groups
        return None

    @classmethod
    def match_status(cls, text: str) -> Optional[dict]:
        """Match status query command."""
        text = text.lower().strip()
        for pattern in cls.STATUS_PATTERNS:
            match = re.search(pattern, text)
            if match:
                groups = match.groupdict()
                if 'item' in groups and groups['item']:
                    # Normalize item name
                    groups['item'] = RussianNormalizer.normalize_word(groups['item'])
                return groups
        return None
