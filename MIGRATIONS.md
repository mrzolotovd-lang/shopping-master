# Database Migrations — Alembic

## Настройка

Alembic настроен для управления миграциями базы данных.

## Команды

### Создать новую миграцию

```bash
# Автоматически (на основе изменений в моделях)
DATABASE_PATH=./shopping_master.db alembic revision --autogenerate -m "Description of changes"

# Вручную
alembic revision -m "Manual migration"
```

### Применить миграции

```bash
# Применить все миграции
alembic upgrade head

# Применить одну миграцию вперёд
alembic upgrade +1

# Откатить одну миграцию назад
alembic downgrade -1

# Откатить к начальной точке
alembic downgrade base
```

### Проверка статуса

```bash
# Показать текущую ревизию
alembic current

# Показать ожидающие миграции
alembic history
```

## Production deployment

```bash
# Перед деплоем приложения
DATABASE_URL=postgresql://user:pass@host/db alembic upgrade head
```

## Структура

```
alembic/
├── env.py              # Alembic environment
├── README
├── script.py.mako      # Template for migrations
└── versions/           # Migration files
    └── c501e33272e8_initial_migration.py
```

## Конфигурация

**Переменные окружения:**
- `DATABASE_URL` — PostgreSQL URL (production)
- `DATABASE_PATH` — SQLite path (development)

**Приоритет:**
1. `DATABASE_URL` (если установлен)
2. `DATABASE_PATH` (по умолчанию `./shopping_master.db`)

## Пример миграции

```python
"""Add user telegram_id.

Revision ID: abc123
Revises: c501e33272e8
Create Date: 2026-08-06

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123'
down_revision = 'c501e33272e8'

def upgrade() -> None:
    op.add_column('users', sa.Column('telegram_id', sa.Integer(), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'telegram_id')
```
