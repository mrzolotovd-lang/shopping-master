"""Telegram bot interface for Shopping Master."""

import os
from datetime import datetime
from typing import Optional

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from loguru import logger

from ..core.agent import Agent
from ..database.connection import DatabaseConnection
from ..nlp.processor import NLPProcessor


class TelegramBot:
    """Telegram bot for Shopping Master."""

    def __init__(self, token: str, db_connection: DatabaseConnection):
        """Initialize Telegram bot."""
        self.token = token
        self.db = db_connection
        self.agent = Agent(db_connection)
        self.nlp = NLPProcessor()
        
        # Create bot with default SSL verification (secure)
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        
        self._register_handlers()
        logger.info("Telegram bot initialized")

    def _register_handlers(self):
        """Register message handlers."""
        self.dp.message(CommandStart())(self.cmd_start)
        self.dp.message(Command("buy"))(self.cmd_buy)
        self.dp.message(Command("status"))(self.cmd_status)
        self.dp.message(Command("consume"))(self.cmd_consume)
        self.dp.message(Command("thresholds"))(self.cmd_thresholds)
        self.dp.message(Command("help"))(self.cmd_help)
        
        # Handle all other messages as natural language
        self.dp.message()(self.handle_message)

    async def cmd_start(self, message: Message):
        """Handle /start command."""
        user_id = message.from_user.id
        user_name = message.from_user.full_name or "User"
        
        response = f"Привет, {user_name}! 🤖\n\n"
        response += "Я Shopping Master Bot — помогу управлять запасами продуктов.\n\n"
        response += "**Команды:**\n"
        response += "/buy — список покупок\n"
        response += "/status — все товары\n"
        response += "/status <товар> — статус товара\n"
        response += "/consume — ежедневное списание\n"
        response += "/thresholds — проверка порогов\n"
        response += "/help — помощь\n\n"
        response += "**Естественный язык:**\n"
        response += "• 'купил молоко 2л'\n"
        response += "• 'молока осталось половина'\n"
        response += "• 'список покупок'\n"
        
        await message.answer(response, parse_mode="Markdown")

    async def cmd_buy(self, message: Message):
        """Handle /buy command — show shopping list."""
        try:
            shopping_list = self.agent.get_shopping_list()
            
            if not shopping_list:
                await message.answer("🛒 Список покупок пуст!")
                return
            
            response = "🛒 **Список покупок:**\n\n"
            response += "```\n"
            response += f"{'Товар':<25} {'Кол-во':>10} {'Ед':<8} {'Причина':<12}\n"
            response += "-" * 60 + "\n"
            
            for entry in shopping_list:
                item_name = entry.item.name if entry.item else "Unknown"
                unit = entry.item.unit if entry.item else "шт"
                response += f"{item_name:<25} {float(entry.quantity):>10.2f} {unit:<8} {entry.reason:<12}\n"
            
            response += "```"
            await message.answer(response, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error in /buy command: {e}", exc_info=True)
            await message.answer("❌ Ошибка при получении списка покупок")

    async def cmd_status(self, message: Message):
        """Handle /status command."""
        args = message.text.split(maxsplit=1)
        
        if len(args) > 1:
            # Status for specific item
            item_name = args[1]
            response = self._get_item_status(item_name)
        else:
            # Status for all items
            response = self._get_all_status()
        
        await message.answer(response, parse_mode="Markdown")

    async def cmd_consume(self, message: Message):
        """Handle /consume command — run daily consumption."""
        try:
            result = self.agent.run_daily_consumption()
            response = f"📉 Ежедневное списание: {result['updated']} из {result['processed']} товаров обновлено"
            await message.answer(response)
        except Exception as e:
            logger.error(f"Consumption error: {e}", exc_info=True)
            await message.answer("❌ Ошибка при выполнении списания. Проверьте логи.")

    async def cmd_thresholds(self, message: Message):
        """Handle /thresholds command — check thresholds."""
        try:
            result = self.agent.run_threshold_check()
            messages = []
            if result["added"] > 0:
                messages.append(f"➕ Добавлено: {result['added']}")
            if result["removed"] > 0:
                messages.append(f"➖ Удалено: {result['removed']}")
            if not messages:
                messages.append("Без изменений")
            response = f"🔍 Проверка порогов: {', '.join(messages)}"
            await message.answer(response)
        except Exception as e:
            logger.error(f"Threshold check error: {e}", exc_info=True)
            await message.answer("❌ Ошибка при проверке порогов. Проверьте логи.")

    async def cmd_help(self, message: Message):
        """Handle /help command."""
        response = "**Shopping Master Bot — Помощь**\n\n"
        response += "**Команды:**\n"
        response += "/start — приветствие\n"
        response += "/buy — список покупок\n"
        response += "/status — все товары\n"
        response += "/status <товар> — статус товара\n"
        response += "/consume — ежедневное списание\n"
        response += "/thresholds — проверка порогов\n"
        response += "/help — эта справка\n\n"
        response += "**Естественный язык:**\n"
        response += "• 'купил молоко 2л' — покупка\n"
        response += "• 'молока осталось 30%' — обновить остаток\n"
        response += "• 'список покупок' — показать список\n"
        response += "• 'что нужно купить?' — список покупок\n"
        
        await message.answer(response, parse_mode="Markdown")

    async def handle_message(self, message: Message):
        """Handle natural language messages with error handling."""
        if not message.text:
            return
        
        try:
            text = message.text
            user_id = message.from_user.id
            user_name = message.from_user.full_name or "User"
            
            logger.debug(f"Message from {user_id}: '{text}'")
            
            # Process with NLP
            nlp_result = self.nlp.process(text, user_id)
            
            if not nlp_result["success"]:
                await message.answer(nlp_result["message"])
                return
            
            command_type = nlp_result["command_type"]
            
            if command_type == "purchase":
                response = self._handle_purchase(nlp_result["data"])
            elif command_type == "update":
                response = self._handle_update(nlp_result["data"])
            elif command_type == "status_all":
                response = self._get_all_status()
            elif command_type == "status_item":
                response = self._get_item_status(nlp_result["data"]["item_name"])
            else:
                response = "Извините, я не понял команду. Попробуйте:\n"
                response += "• 'купил молоко 2л'\n"
                response += "• 'молока осталось половина'\n"
                response += "• 'список покупок'"
            
            await message.answer(response, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error processing message from {message.from_user.id}: {e}", exc_info=True)
            await message.answer(
                "❌ Произошла ошибка при обработке сообщения. Попробуйте позже.",
                parse_mode="Markdown"
            )

    def _handle_purchase(self, data: dict) -> str:
        """Handle purchase command."""
        item_name = data["item_name"]
        amount = data.get("amount")
        unit = data.get("unit")
        
        result = self.agent.process_purchase(
            item_name,
            amount,
            unit,
            None  # user_id can be added if needed
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
            None
        )
        
        if result["success"]:
            return f"✅ {result['item_name']}: обновлено до {result['new_stock']:.2f}"
        else:
            return f"❌ {result.get('error', 'Ошибка при обновлении')}"

    def _get_all_status(self) -> str:
        """Get status of all items."""
        items = self.agent.get_all_items_status()
        
        if not items:
            return "📭 У вас пока нет товаров в базе"
        
        response = "📦 **Ваши запасы:**\n\n"
        response += "```\n"
        response += f"{'Товар':<25} {'Остаток':>10} {'Ед':<8}\n"
        response += "-" * 45 + "\n"
        
        for item in items:
            response += f"{item.name:<25} {float(item.current_stock):>10.2f} {item.unit:<8}\n"
        
        response += "```"
        return response

    def _get_item_status(self, item_name: str) -> str:
        """Get status for specific item."""
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

    async def run_polling(self, retry_limit: int = 5, retry_delay: int = 5):
        """Run bot polling with error handling and retry limit."""
        import asyncio
        
        logger.info("Starting Telegram bot polling...")
        retry_count = 0
        
        while retry_count < retry_limit:
            try:
                await self.dp.start_polling(self.bot)
                # If polling exits without error, break the loop
                break
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                break
            except Exception as e:
                retry_count += 1
                logger.critical(f"Bot crashed (attempt {retry_count}/{retry_limit}): {type(e).__name__}: {e}", exc_info=True)
                
                if retry_count >= retry_limit:
                    logger.error(f"Max retry limit ({retry_limit}) reached. Stopping bot.")
                    await self._send_alert(f"Bot crashed after {retry_count} attempts: {e}")
                    raise
                
                # Send alert on first failure
                if retry_count == 1:
                    await self._send_alert(f"Bot crashed (attempt {retry_count}/{retry_limit}): {e}")
                
                # Wait before retry (exponential backoff)
                wait_time = retry_delay * (2 ** (retry_count - 1))
                logger.info(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
        else:
            logger.error("Retry limit exceeded, stopping bot")
            await self._send_alert(f"Bot stopped: retry limit ({retry_limit}) exceeded")
        
        await self.stop()

    async def _send_alert(self, error_message: str):
        """Send error alert to admin chat."""
        admin_chat_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID")
        if not admin_chat_id:
            logger.warning("TELEGRAM_ADMIN_CHAT_ID not set, skipping alert")
            return
        
        try:
            alert_text = f"🚨 **BOT CRASHED**\n\n"
            alert_text += f"Error: `{error_message}`\n"
            alert_text += f"Time: `{datetime.now().isoformat()}`\n"
            alert_text += f"\nPlease check logs immediately!"
            
            await self.bot.send_message(
                chat_id=int(admin_chat_id),
                text=alert_text,
                parse_mode="Markdown"
            )
            logger.info("Alert sent to admin")
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")

    async def stop(self):
        """Stop the bot gracefully."""
        try:
            await self.bot.session.close()
            logger.info("Telegram bot stopped gracefully")
        except Exception as e:
            logger.error(f"Error during bot shutdown: {e}")


def create_bot_from_config(db_connection: DatabaseConnection) -> TelegramBot:
    """Create Telegram bot from configuration."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")
    
    return TelegramBot(token, db_connection)
