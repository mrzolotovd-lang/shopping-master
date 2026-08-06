# 🚀 Production Deployment — Quick Start

## 3 шага до продакшена

### 1️⃣ Создать PostgreSQL

**Neon (рекомендуется):**
```bash
# 1. https://neon.tech → Sign Up
# 2. Create Project → "shopping-master"
# 3. Connection Details → Copy URI
#    postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
```

**Supabase:**
```bash
# 1. https://supabase.com → Sign Up
# 2. New Project
# 3. Settings → Database → Connection string
```

---

### 2️⃣ Настроить GitLab Variables

**Settings → CI/CD → Variables → Add:**

```
DATABASE_URL=postgresql://user:password@host:5432/dbname
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_ADMIN_CHAT_ID=123456789
DATABASE_TYPE=postgresql
```

**Для деплоя на сервер:**
```
SSH_PRIVATE_KEY=-----BEGIN OPENSSH...
PROD_HOST=your-server.com
PROD_USER=deploy
PROD_DIR=/var/www/shopping-master
```

---

### 3️⃣ Применить миграции

**Вариант A: Через GitLab CI/CD (автоматически)**
```bash
git push origin main
# Pipeline запустит "migrate" job автоматически
```

**Вариант B: Локально**
```bash
export DATABASE_URL="postgresql://..."
./scripts/deploy.sh
```

**Вариант C: Вручную**
```bash
export DATABASE_URL="postgresql://..."
alembic upgrade head
alembic current  # Проверить
```

---

## ✅ Проверка

```bash
# 1. Запустить бота
python -m src.bot

# 2. В Telegram:
/start
/status
купил молоко 2л

# 3. Проверить логи
journalctl -u shopping-bot -f
```

---

## 📁 Файлы для деплоя

| Файл | Назначение |
|------|------------|
| `scripts/deploy.sh` | Quick deploy скрипт |
| `scripts/migrate.py` | Python миграции |
| `alembic/env.py` | Alembic конфигурация |
| `DEPLOYMENT.md` | Полная документация |
| `.gitlab-ci.yml` | CI/CD pipeline |

---

## 🆘 Troubleshooting

### Миграции не применяются
```bash
# Проверить текущую ревизию
alembic current

# Откатить и применить заново
alembic downgrade base
alembic upgrade head
```

### Бот не подключается к БД
```bash
# Проверить SSL mode (должен быть require)
echo $DATABASE_URL | grep sslmode

# Для Neon/Supabase SSL обязателен
```

### Ошибки в CI/CD
```bash
# Проверить переменные
echo $DATABASE_URL | head -c 30

# Запустить локально
./scripts/deploy.sh
```

---

**Ready to deploy! 🎉**
