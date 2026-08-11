"""NLP processor for natural language commands."""

from typing import Optional

from loguru import logger

from .dictionary import get_stock_level, normalize_unit
from .patterns import NLPPatterns


class NLPProcessor:
    """Process natural language commands."""

    def __init__(self):
        """Initialize NLP processor."""
        self.patterns = NLPPatterns()

    def process(self, text: str, user_id: Optional[int] = None) -> dict:
        """Process a text command."""
        logger.debug(f"Processing: '{text}' (user_id={user_id})")

        result = {
            "success": False,
            "command_type": None,
            "data": {},
            "message": "",
        }

        # Try status patterns first (more specific)
        status = self.patterns.match_status(text)
        if status is not None:
            return self._process_status(status, result)

        # Try purchase patterns
        purchase = self.patterns.match_purchase(text)
        if purchase:
            return self._process_purchase(purchase, result)

        # Try update patterns
        update = self.patterns.match_update(text)
        if update:
            return self._process_update(update, result)

        # Try rule patterns
        rule = self.patterns.match_rule(text)
        if rule:
            return self._process_rule(rule, result)

        result["message"] = "Команда не распознана. Попробуйте: 'купил молоко 2л', 'молока осталось половина', 'список покупок'"
        return result

    def _process_purchase(self, match: dict, result: dict) -> dict:
        """Process purchase command."""
        item = match.get("item", "").strip()
        amount = match.get("amount")
        unit = match.get("unit")

        if not item:
            result["message"] = "Не указан товар"
            return result

        if amount:
            amount = float(amount)
        if unit:
            unit = normalize_unit(unit)

        result["success"] = True
        result["command_type"] = "purchase"
        result["data"] = {
            "item_name": item,
            "amount": amount,
            "unit": unit,
        }
        result["message"] = f"Зафиксирована покупка: {item}"
        if amount:
            result["message"] += f" ({amount} {unit or 'шт'})"

        return result

    def _process_update(self, match: dict, result: dict) -> dict:
        """Process stock update command."""
        item = match.get("item", "").strip()
        amount = match.get("amount")
        level = match.get("level")

        if not item:
            result["message"] = "Не указан товар"
            return result

        stock_level = None
        if amount:
            stock_level = float(amount)
        elif level:
            stock_level = get_stock_level(level)
            if stock_level is None:
                if "половина" in level or "пол-" in level:
                    stock_level = 0.5

        if stock_level is None:
            result["message"] = "Не удалось определить уровень остатка"
            return result

        result["success"] = True
        result["command_type"] = "update"
        result["data"] = {
            "item_name": item,
            "stock_level": stock_level,
        }
        result["message"] = f"Обновлён остаток: {item}"

        return result

    def _process_status(self, match: dict, result: dict) -> dict:
        """Process status query command."""
        item = match.get("item")

        result["success"] = True
        
        if item:
            result["command_type"] = "status_item"
            result["data"] = {"item_name": item.strip()}
            result["message"] = f"Статус товара: {item.strip()}"
        else:
            result["command_type"] = "status_all"
            result["message"] = "Показываю все товары"

        return result

    def _process_rule(self, match: dict, result: dict) -> dict:
        """Process consumption rule command."""
        item = match.get("item", "").strip()
        amount = match.get("amount")
        unit = match.get("unit")
        period = match.get("period", "день")

        if not item:
            result["message"] = "Не указан товар"
            return result

        if amount:
            amount = float(amount)
        if unit:
            unit = normalize_unit(unit)

        result["success"] = True
        result["command_type"] = "rule"
        result["data"] = {
            "item_name": item,
            "daily_consumption": amount,
            "unit": unit,
            "period": period,
        }
        result["message"] = f"Создано правило расхода: {item}"
        if amount:
            result["message"] += f" ({amount} {unit or 'шт'}/день)"

        return result
