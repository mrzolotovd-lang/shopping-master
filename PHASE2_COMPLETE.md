# Shopping Master — Phase 2 Implementation

## ✅ Завершенные компоненты Phase 2

### 1. Telegram Бот 🤖

**Файлы:**
- `src/interfaces/telegram.py` — Telegram bot handler
- `src/bot.py` — Entry point
- `scripts/run_bot.py` — Launch script
- `TELEGRAM_BOT.md` — Документация

**Команды:**
- `/start` — Приветствие
- `/buy` — Список покупок
- `/status` — Все товары
- `/status <товар>` — Статус товара
- `/consume` — Ежедневное списание
- `/thresholds` — Проверка порогов
- `/help` — Справка

**Естественный язык:**
- "купил молоко 2л"
- "молока осталось половина"
- "список покупок"

**Запуск:**
```bash
cp .env.example .env
# Заполнить TELEGRAM_BOT_TOKEN
python scripts/run_bot.py
```

---

### 2. GitLab CI/CD 🔄

**Файлы:**
- `.gitlab-ci.yml` — Pipeline конфигурация
- `scripts/daily_consumption.py` — Scheduled job
- `scripts/backup.py` — S3 backup
- `GITLAB_CI.md` — Документация

**Pipeline stages:**
1. `test` — pytest с coverage (авто)
2. `lint` — ruff + mypy (авто)
3. `build` — компиляция (авто)
4. `deploy_staging` — ручной на develop
5. `deploy_production` — ручной на main
6. `daily_consumption` — scheduled (3:00 UTC)
7. `backup_production` — scheduled (воскресенье)

**Настройка переменных:**
```
DATABASE_URL
TELEGRAM_BOT_TOKEN
SSH_PRIVATE_KEY
STAGING_HOST, PROD_HOST
S3_BUCKET, AWS_*
```

---

### 3. PostgreSQL Миграция 🗄️

**Файлы:**
- `scripts/migrate_to_postgresql.py` — Прямая миграция
- `scripts/export_data.py` — Экспорт в JSON
- `scripts/import_data.py` — Импорт из JSON
- `POSTGRESQL_MIGRATION.md` — Документация

**Провайдеры:**
- **Neon** — Serverless PostgreSQL (0.5 GB free)
- **Supabase** — PostgreSQL + Realtime (500 MB free)
- **Self-hosted** — Docker PostgreSQL

**Миграция:**
```bash
# Прямая миграция SQLite → PostgreSQL
DATABASE_URL="postgresql://..." SQLITE_PATH="./shopping.db" \
  python scripts/migrate_to_postgresql.py

# Или через JSON
EXPORT_PATH=backup.json python scripts/export_data.py
DATABASE_URL="postgresql://..." IMPORT_PATH=backup.json \
  python scripts/import_data.py
```

---

### 4. Бэкапы 💾

**Файлы:**
- `scripts/backup.py` — Backup to S3
- `.gitlab-ci.yml` — Scheduled pipeline

**Автоматический бэкап:**
- Воскресенье в 2:00 UTC
- PostgreSQL → SQL dump → S3
- Retention: 30 дней

**Ручной бэкап:**
```bash
python scripts/backup.py
```

---

## 📁 Структура Phase 2

```
shopping-master/
├── src/
│   ├── interfaces/
│   │   ├── chat.py         # MCP Chat Interface
│   │   └── telegram.py     # Telegram Bot (NEW)
│   └── bot.py              # Bot entry point (NEW)
├── scripts/
│   ├── run_bot.py          # Launch bot (NEW)
│   ├── daily_consumption.py # CI/CD scheduled job (NEW)
│   ├── backup.py           # S3 backup (NEW)
│   ├── migrate_to_postgresql.py # Migration (NEW)
│   ├── export_data.py      # JSON export (NEW)
│   └── import_data.py      # JSON import (NEW)
├── config/
│   ├── default.yaml
│   ├── development.yaml
│   └── production.yaml     # PostgreSQL config
├── .gitlab-ci.yml          # CI/CD pipeline (NEW)
├── .env.example            # Environment template (NEW)
├── requirements.txt        # Updated dependencies
├── TELEGRAM_BOT.md         # Bot documentation (NEW)
├── GITLAB_CI.md            # CI/CD documentation (NEW)
└── POSTGRESQL_MIGRATION.md # Migration guide (NEW)
```

---

## 🚀 Быстрый старт

### 1. Telegram Бот

```bash
# Создать бота в @BotFather
# Получить токен

cp .env.example .env
# Заполнить TELEGRAM_BOT_TOKEN

source venv/bin/activate
pip install -r requirements.txt

python scripts/run_bot.py
```

### 2. Миграция на PostgreSQL

```bash
# Создать БД в Neon/Supabase
# Получить DATABASE_URL

# Миграция
DATABASE_URL="postgresql://..." \
  python scripts/migrate_to_postgresql.py

# Обновить .env
DATABASE_TYPE=postgresql
DATABASE_URL="postgresql://..."
```

### 3. CI/CD

```bash
# В GitLab UI: Settings → CI/CD → Variables
# Добавить переменные

# Запустить pipeline
git push origin main
```

### 4. Бэкапы

```bash
# В GitLab UI: Build → Pipeline Schedules
# Создать schedule: 0 2 * * 0

# Переменные: S3_BUCKET, DATABASE_URL, AWS_*
```

---

## 📊 Статус Phase 2

| Компонент | Статус | Файлы |
|-----------|--------|-------|
| Telegram Bot | ✅ 100% | `src/interfaces/telegram.py`, `src/bot.py` |
| GitLab CI/CD | ✅ 100% | `.gitlab-ci.yml`, `scripts/*.py` |
| PostgreSQL | ✅ 100% | `scripts/migrate_*.py`, `POSTGRESQL_MIGRATION.md` |
| Бэкапы | ✅ 100% | `scripts/backup.py`, `.gitlab-ci.yml` |
| Документация | ✅ 100% | `TELEGRAM_BOT.md`, `GITLAB_CI.md`, `POSTGRESQL_MIGRATION.md` |

---

## 🔧 Зависимости

```txt
aiogram>=3.4.0          # Telegram bot
psycopg2-binary>=2.9.0  # PostgreSQL driver
boto3>=1.34.0           # AWS S3 backup
python-dotenv>=1.0.0    # Environment variables
loguru>=0.7.0           # Logging
```

---

## 📝 Next Steps (Phase 3)

Возможные направления:

1. **Web Interface** — React/Vue dashboard
2. **Analytics** — Графики, статистика потребления
3. **Mobile App** — React Native / Flutter
4. **Multi-user** — Семья, команды, роли
5. **Integrations** — Delivery APIs, магазины
6. **ML Predictions** — Предсказание покупок
7. **Voice Commands** — Алиса, Siri интеграция

---

## 🆘 Troubleshooting

**Бот не запускается:**
```bash
# Проверить токен
echo $TELEGRAM_BOT_TOKEN

# Проверить базу
python -c "from src.database.connection import DatabaseConnection; db = DatabaseConnection('sqlite:///test.db'); db.create_tables()"
```

**Миграция не работает:**
```bash
# Экспорт в JSON (надежнее)
python scripts/export_data.py

# Импорт
DATABASE_URL="..." IMPORT_PATH=backup.json python scripts/import_data.py
```

**CI/CD failed:**
```bash
# Тест локально
pytest tests/ -v

# Линт локально
ruff check src/ tests/
```
