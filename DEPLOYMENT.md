# 🚀 Production Deployment Checklist

## Предварительные требования

- [ ] GitLab проект настроен
- [ ] PostgreSQL база создана (Neon/Supabase)
- [ ] Telegram бот создан через @BotFather
- [ ] Сервер для деплоя подготовлен (VPS)

---

## 1. Создание PostgreSQL

### Neon (Рекомендуется)

```bash
# 1. Зарегистрироваться: https://neon.tech
# 2. Создать проект
# 3. Получить Connection String:
#    postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
```

### Supabase

```bash
# 1. Зарегистрироваться: https://supabase.com
# 2. Создать проект
# 3. Settings → Database → Connection string
```

### Проверка подключения

```bash
# Локально
psql "postgresql://user:password@host:5432/dbname"

# Должно показать:
# dbname=>
```

---

## 2. Настройка GitLab Variables

**Settings → CI/CD → Variables → Add Variable**

| Key | Value | Protected | Masked |
|-----|-------|-----------|--------|
| `DATABASE_URL` | `postgresql://...` | ✅ | ✅ |
| `TELEGRAM_BOT_TOKEN` | `1234567890:ABC...` | ✅ | ✅ |
| `TELEGRAM_ADMIN_CHAT_ID` | `123456789` | ✅ | ❌ |
| `SSH_PRIVATE_KEY` | `-----BEGIN...` | ✅ | ✅ |
| `PROD_HOST` | `your-server.com` | ✅ | ❌ |
| `PROD_USER` | `deploy` | ✅ | ❌ |
| `PROD_DIR` | `/var/www/shopping-master` | ✅ | ❌ |
| `S3_BUCKET` | `shopping-backups` | ✅ | ❌ |
| `AWS_ACCESS_KEY_ID` | `AKIA...` | ✅ | ✅ |
| `AWS_SECRET_ACCESS_KEY` | `...` | ✅ | ✅ |

---

## 3. Применение миграций

### Локально (для теста)

```bash
cd shopping-master

# Установить переменную
export DATABASE_URL="postgresql://user:password@host:5432/dbname"

# Применить миграции
alembic upgrade head

# Проверить статус
alembic current
```

### Через GitLab CI/CD (автоматически)

```yaml
# .gitlab-ci.yml уже настроен
# При merge в main:
# 1. Запустится job "migrate"
# 2. Применит миграции
# 3. Задеплоит приложение
```

### Вручную на сервере

```bash
ssh deploy@your-server.com

cd /var/www/shopping-master
source venv/bin/activate
export DATABASE_URL="postgresql://..."
alembic upgrade head
```

---

## 4. Деплой приложения

### На сервере

```bash
# 1. Подготовить директорию
sudo mkdir -p /var/www/shopping-master
sudo chown deploy:deploy /var/www/shopping-master

# 2. Клонировать репозиторий
cd /var/www/shopping-master
git clone <repo-url> .

# 3. Установить зависимости
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Создать .env
cp .env.example .env
nano .env  # Заполнить переменные

# 5. Применить миграции
export DATABASE_URL="postgresql://..."
alembic upgrade head

# 6. Запустить бота (тест)
python -m src.bot

# 7. Настроить systemd
sudo nano /etc/systemd/system/shopping-bot.service
```

### Systemd service

```ini
[Unit]
Description=Shopping Master Telegram Bot
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/var/www/shopping-master
Environment="PATH=/var/www/shopping-master/venv/bin"
ExecStart=/var/www/shopping-master/venv/bin/python -m src.bot
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Запуск

```bash
# Перезагрузить systemd
sudo systemctl daemon-reload

# Включить автозапуск
sudo systemctl enable shopping-bot

# Запустить
sudo systemctl start shopping-bot

# Проверить статус
sudo systemctl status shopping-bot

# Посмотреть логи
journalctl -u shopping-bot -f
```

---

## 5. Проверка

### Тестирование бота

```
В Telegram:
1. /start — должно показать приветствие
2. /status — должно показать товары
3. /buy — должно показать список покупок
4. "купил молоко 2л" — должно зафиксировать покупку
```

### Проверка логов

```bash
# Логи приложения
journalctl -u shopping-bot -f

# Логи GitLab CI/CD
# Build → Pipelines → Выбрать pipeline → Jobs
```

### Проверка БД

```bash
# Подключиться к PostgreSQL
psql $DATABASE_URL

# Проверить таблицы
\dt

# Проверить данные
SELECT COUNT(*) FROM items;
SELECT COUNT(*) FROM users;
```

---

## 6. Настройка Scheduled Pipelines

**Build → Pipeline Schedules → New Schedule**

### Daily Consumption

```
Description: Daily consumption
Cron: 0 3 * * * (каждый день в 3:00 UTC)
Branch: main
Variables:
  DATABASE_URL: (защищённая переменная)
```

### Weekly Backup

```
Description: Weekly backup
Cron: 0 2 * * 0 (воскресенье в 2:00 UTC)
Branch: main
Variables:
  DATABASE_URL: (защищённая переменная)
  S3_BUCKET: (защищённая переменная)
  AWS_ACCESS_KEY_ID: (защищённая переменная)
  AWS_SECRET_ACCESS_KEY: (защищённая переменная)
```

---

## 7. Мониторинг

### Health Check

```bash
# Создать файл healthcheck.sh
#!/bin/bash
systemctl is-active --quiet shopping-bot && echo "OK" || echo "FAIL"
```

### Алерты

```
Бот автоматически отправит алерт в TELEGRAM_ADMIN_CHAT_ID при:
- Crash бота
- Ошибке подключения к БД
- Критичной ошибке
```

### Логи

```bash
# Просмотр логов
journalctl -u shopping-bot -n 100

# Поиск ошибок
journalctl -u shopping-bot -p err

# Логи за сегодня
journalctl -u shopping-bot --since today
```

---

## Troubleshooting

### Бот не запускается

```bash
# Проверить логи
journalctl -u shopping-bot -f

# Проверить переменные окружения
systemctl show shopping-bot | grep Environment

# Проверить подключение к БД
psql $DATABASE_URL -c "SELECT 1"
```

### Миграции не применяются

```bash
# Проверить текущую ревизию
alembic current

# Проверить историю
alembic history

# Применить заново
alembic upgrade head
```

### Ошибки SSL

```bash
# Убедиться что URL содержит sslmode=require
echo $DATABASE_URL | grep sslmode

# Для Neon/Supabase SSL обязателен
```

---

## Post-Deployment

### Резервное копирование

```bash
# Ручной бэкап
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Восстановление
psql $DATABASE_URL < backup_20260806.sql
```

### Обновление

```bash
# На сервере
cd /var/www/shopping-master
git pull
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart shopping-bot
```

### Откат

```bash
# Откатить миграцию
alembic downgrade -1

# Откатить код
git revert HEAD
sudo systemctl restart shopping-bot
```

---

## ✅ Checklist

- [ ] PostgreSQL создан
- [ ] GitLab Variables настроены
- [ ] Миграции применены
- [ ] Бот запущен
- [ ] Telegram команды работают
- [ ] Scheduled pipelines настроены
- [ ] Мониторинг настроен
- [ ] Бэкапы настроены

---

**Deployment Complete! 🎉**
