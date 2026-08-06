# Telegram Bot — Shopping Master

## Настройка

### 1. Создание бота

1. Откройте **@BotFather** в Telegram
2. Отправьте `/newbot`
3. Введите имя: `Shopping Master Bot`
4. Введите username: `shopping_master_bot` (должен заканчиваться на `bot`)
5. Сохраните токен

### 2. Установка зависимостей

```bash
cd shopping-master
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Конфигурация

Создайте `.env` файл:

```bash
cp .env.example .env
```

Заполните:

```env
# Database
DATABASE_TYPE=sqlite
DATABASE_PATH=./shopping_master.db

# Telegram Bot
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### 4. Запуск бота

```bash
python scripts/run_bot.py
```

Или напрямую:

```bash
python -m src.bot
```

## Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Приветствие и инструкции |
| `/buy` | Список покупок |
| `/status` | Все товары |
| `/status <товар>` | Статус конкретного товара |
| `/consume` | Ежедневное списание |
| `/thresholds` | Проверка порогов |
| `/help` | Справка |

## Естественный язык

Бот понимает команды на русском языке:

**Покупки:**
- "купил молоко 2л"
- "купили яйца 10шт"
- "приобрёл хлеб"

**Обновление остатков:**
- "молока осталось половина"
- "яиц осталось 30%"
- "хлеба осталось треть"

**Запросы:**
- "список покупок"
- "что нужно купить?"
- "статус молоко"

## Архитектура

```
src/interfaces/telegram.py    # Telegram bot handler
src/bot.py                    # Entry point
scripts/run_bot.py           # Launch script
```

Бот использует существующие компоненты:
- `ChatInterface` — логика обработки
- `NLPProcessor` — обработка естественного языка
- `Agent` — бизнес-логика

## Production запуск

Для production используйте supervisor или systemd:

**supervisor:**
```ini
[program:shopping-bot]
command=/path/to/venv/bin/python -m src.bot
directory=/path/to/shopping-master
autostart=true
autorestart=true
```

**systemd:**
```ini
[Unit]
Description=Shopping Master Telegram Bot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/shopping-master
ExecStart=/path/to/venv/bin/python -m src.bot
Restart=always

[Install]
WantedBy=multi-user.target
```

## Тестирование

Проверка команд:

```bash
# Запустить бота
python scripts/run_bot.py

# В Telegram:
/start
/buy
/status
купил молоко 2л
```
