"""Chat interface for MCP integration."""

from typing import Optional

from loguru import logger

from ..core.agent import Agent
from ..database.connection import DatabaseConnection
from ..nlp.processor import NLPProcessor


class ChatInterface:
    """Chat interface for natural language interaction."""

    def __init__(self, db_connection: DatabaseConnection):
        """Initialize chat interface."""
        self.db = db_connection
        self.agent = Agent(db_connection)
        self.nlp = NLPProcessor()
        self.current_user_id: Optional[int] = None

    def set_user(self, user_id: int, name: str = "User") -> str:
        """Set current user context."""
        self.current_user_id = user_id
        logger.info(f"User set: {user_id} ({name})")
        return f"Привет, {name}! Я готов помогать управлять запасами."

    def process_message(self, text: str) -> str:
        """Process a chat message and return response."""
        logger.info(f"Processing message: '{text}'")

        # Parse with NLP
        nlp_result = self.nlp.process(text, self.current_user_id)

        if not nlp_result["success"]:
            return nlp_result["message"]

        # Handle different command types
        command_type = nlp_result["command_type"]

        if command_type == "purchase":
            return self._handle_purchase(nlp_result["data"])
        elif command_type == "update":
            return self._handle_update(nlp_result["data"])
        elif command_type == "status_all":
            return self._handle_status_all()
        elif command_type == "status_item":
            return self._handle_status_item(nlp_result["data"]["item_name"])
        else:
            return "Извините, я не понял команду. Попробуйте: 'купил молоко 2л', 'молока осталось половина', 'список покупок'"

    def _handle_purchase(self, data: dict) -> str:
        """Handle purchase command."""
        item_name = data["item_name"]
        amount = data.get("amount")
        unit = data.get("unit")

        result = self.agent.process_purchase(
            item_name,
            amount,
            unit,
            self.current_user_id
        )

        if result["success"]:
            response = f"✅ {result['item_name']}: {result['old_stock']:.2f} → {result['new_stock']:.2f}"
            if result.get("suggest_smart_mode"):
                response += "\n💡 Хотите переключить на авто-заполнение? (10+ покупок)"
            return response
        else:
            return f"❌ {result.get('error', 'Ошибка при обработке покупки')}"

    def _handle_update(self, data: dict) -> str:
        """Handle stock update command."""
        item_name = data["item_name"]
        stock_level = data["stock_level"]

        # Convert percentage to absolute if needed
        if stock_level <= 1.0:
            # It's a percentage, need to get package_size
            session = self.db.get_session()
            try:
                from ..database.repositories.item_repo import ItemRepository
                item_repo = ItemRepository(self.db)
                item = item_repo.get_by_name(session, item_name)
                if item:
                    stock_level = float(item.package_size) * stock_level
                else:
                    return f"❌ Товар '{item_name}' не найден"
            finally:
                session.close()

        result = self.agent.process_stock_update(
            item_name,
            stock_level,
            self.current_user_id
        )

        if result["success"]:
            return f"✅ {result['item_name']}: обновлено до {result['new_stock']:.2f}"
        else:
            return f"❌ {result.get('error', 'Ошибка при обновлении')}"

    def _handle_status_all(self) -> str:
        """Handle status all items command."""
        items = self.agent.get_all_items_status()

        if not items:
            return "📭 У вас пока нет товаров в базе"

        response = "📦 **Ваши запасы:**\n\n"
        response += "```\n"
        response += f"{'Товар':<25} {'Остаток':>10} {'Ед':<8}\n"
        response += "-" * 45 + "\n"

        for item in items:
            category_name = item.category.name if item.category else ""
            response += f"{item.name:<25} {float(item.current_stock):>10.2f} {item.unit:<8}\n"

        response += "```"
        return response

    def _handle_status_item(self, item_name: str) -> str:
        """Handle status for specific item."""
        session = self.db.get_session()
        try:
            from ..database.repositories.item_repo import ItemRepository
            from ..database.repositories.shopping_repo import ShoppingListRepository

            item_repo = ItemRepository(self.db)
            shopping_repo = ShoppingListRepository(self.db)

            item = item_repo.get_by_name(session, item_name)

            if not item:
                return f"❌ Товар '{item_name}' не найден"

            category_name = item.category.name if item.category else "Без категории"
            threshold = float(item.package_size) * (float(item.reorder_threshold) / 100)

            response = f"📊 **{item.name}**\n\n"
            response += f"• Категория: {category_name}\n"
            response += f"• Остаток: {float(item.current_stock):.2f} {item.unit}\n"
            response += f"• Упаковка: {float(item.package_size):.2f} {item.unit}\n"
            response += f"• Порог покупки: {threshold:.2f} {item.unit} ({item.reorder_threshold}%)\n"

            # Check if in shopping list
            in_list = shopping_repo.get_pending_for_item(session, item.id)
            if in_list:
                response += f"\n⚠️ **В списке покупок!** (рекомендуется: {float(in_list.quantity):.2f} {item.unit})"

            return response
        finally:
            session.close()

    def get_shopping_list(self) -> str:
        """Get shopping list as formatted string."""
        shopping_list = self.agent.get_shopping_list("pending")

        if not shopping_list:
            return "🛒 Список покупок пуст!"

        response = "🛒 **Список покупок:**\n\n"
        response += "```\n"
        response += f"{'Товар':<25} {'Кол-во':>10} {'Ед':<8} {'Причина':<12}\n"
        response += "-" * 60 + "\n"

        for entry in shopping_list:
            response += f"{entry.item.name:<25} {float(entry.quantity):>10.2f} {entry.item.unit:<8} {entry.reason:<12}\n"

        response += "```"
        return response

    def run_daily_consumption(self) -> str:
        """Run daily consumption and return summary."""
        result = self.agent.run_daily_consumption()
        return f"📉 Ежедневное списание: {result['updated']} из {result['processed']} товаров обновлено"

    def check_thresholds(self) -> str:
        """Check thresholds and return summary."""
        result = self.agent.run_threshold_check()
        messages = []
        if result["added"] > 0:
            messages.append(f"➕ Добавлено: {result['added']}")
        if result["removed"] > 0:
            messages.append(f"➖ Удалено: {result['removed']}")
        if not messages:
            messages.append("Без изменений")
        return f"🔍 Проверка порогов: {', '.join(messages)}"
