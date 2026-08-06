# PostgreSQL Migration — Shopping Master

## Обзор

Phase 2 включает миграцию с SQLite на PostgreSQL для production окружения.

## Варианты PostgreSQL

### 1. Neon (Serverless PostgreSQL)

**Преимущества:**
- Бесплатный тариф: 0.5 GB, 10 часов активности/день
- Автоматическое масштабирование
- Built-in branching
- Serverless архитектура

**Настройка:**
1. Зарегистрироваться: https://neon.tech
2. Создать проект
3. Получить connection string:
   ```
   postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
   ```

### 2. Supabase

**Преимущества:**
- Бесплатный тариф: 500 MB
- Включает Realtime, Auth, Storage
- PostgreSQL 15+
- Dashboard с UI

**Настройка:**
1. Зарегистрироваться: https://supabase.com
2. Создать проект
3. Settings → Database → Connection string
   ```
   postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
   ```

### 3. Self-hosted PostgreSQL

**Настройка:**
```bash
# Docker
docker run -d \
  -e POSTGRES_USER=shopping \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=shopping_master \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  postgres:15-alpine
```

## Миграция данных

### Шаг 1: Экспорт SQLite

```bash
cd shopping-master
source venv/bin/activate

# Экспорт в JSON
EXPORT_PATH=backup_$(date +%Y%m%d).json python scripts/export_data.py
```

### Шаг 2: Создание PostgreSQL

```bash
# Выбрать провайдера (Neon/Supabase/Self-hosted)
# Получить DATABASE_URL
```

### Шаг 3: Миграция

```bash
# Прямая миграция SQLite → PostgreSQL
DATABASE_URL="postgresql://..." SQLITE_PATH="./shopping_master.db" \
  python scripts/migrate_to_postgresql.py
```

### Шаг 4: Импорт из JSON (альтернатива)

```bash
# Если прямая миграция не сработала
DATABASE_URL="postgresql://..." IMPORT_PATH=backup.json \
  python scripts/import_data.py
```

### Шаг 5: Проверка

```bash
# Подключиться к PostgreSQL и проверить данные
psql $DATABASE_URL -c "SELECT COUNT(*) FROM items;"
```

## Конфигурация приложения

### .env для production

```env
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://user:password@host:5432/dbname?sslmode=require

# Telegram
TELEGRAM_BOT_TOKEN=1234567890:ABCdef...

# Backup
S3_BUCKET=shopping-backups
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
```

### config/production.yaml

```yaml
database:
  type: "postgresql"
  postgresql_url: "${DATABASE_URL}"

notifications:
  enabled: true
  telegram_bot_token: "${TELEGRAM_BOT_TOKEN}"

backup:
  enabled: true
  schedule: "0 3 * * 0"
  storage: "s3"
  retention_days: 60
```

## Экспорт/Импорт утилиты

### export_data.py

Экспортирует все таблицы в JSON:

```bash
# SQLite
python scripts/export_data.py

# PostgreSQL
DATABASE_TYPE=postgresql DATABASE_URL="..." \
  python scripts/export_data.py
```

### import_data.py

Импортирует из JSON:

```bash
IMPORT_PATH=backup.json DATABASE_URL="..." \
  python scripts/import_data.py
```

## Миграционная схема

```
SQLite (development)
    ↓
export_data.py → backup.json
    ↓
import_data.py → PostgreSQL (production)
    ↓
daily_consumption.py → scheduled CI/CD
    ↓
backup.py → S3 (weekly)
```

## Rollback

Если нужно вернуться на SQLite:

```bash
# Экспорт из PostgreSQL
DATABASE_TYPE=postgresql DATABASE_URL="..." \
  EXPORT_PATH=pg_backup.json python scripts/export_data.py

# Импорт в SQLite
DATABASE_TYPE=sqlite IMPORT_PATH=pg_backup.json \
  python scripts/import_data.py
```

## Производительность

**SQLite → PostgreSQL преимущества:**
- Concurrent writes
- Better indexing
- WAL logging
- Production-ready
- Row-level locking

**Рекомендации:**
- Добавить индексы на часто используемые поля
- Настроить connection pooling
- Включить query logging для отладки

## Мониторинг

```sql
-- Проверка размера БД
SELECT pg_size_pretty(pg_database_size(current_database()));

-- Топ таблиц по размеру
SELECT 
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Активные подключения
SELECT count(*) FROM pg_stat_activity;
```

## Troubleshooting

**Connection refused:**
```bash
# Проверить SSL mode
DATABASE_URL="postgresql://...?sslmode=require"
```

**Authentication failed:**
```bash
# Проверить credentials
echo $DATABASE_URL
```

**Table doesn't exist:**
```bash
# Запустить миграцию заново
python scripts/migrate_to_postgresql.py
```

## Следующие шаги

1. ✅ Миграция на PostgreSQL
2. ⏳ Настройка бэкапов в S3
3. ⏳ Мониторинг и алерты
4. ⏳ Оптимизация запросов
