# GitLab Variables Setup Guide

## 🔴 Обязательные переменные

| Variable | Value | Protected | Masked | Описание |
|----------|-------|-----------|--------|----------|
| `DATABASE_TYPE` | `postgresql` | ❌ | ❌ | Тип БД |
| `DATABASE_URL` | `postgresql://...` | ✅ | ✅ | Connection string |
| `TELEGRAM_BOT_TOKEN` | `1234567890:ABC...` | ✅ | ✅ | Токен бота |
| `TELEGRAM_ADMIN_CHAT_ID` | `123456789` | ✅ | ❌ | Chat ID для алертов |

---

## Пошаговая инструкция

### 1. Открыть настройки

```
GitLab → Ваш проект → Settings → CI/CD → Variables → Add variable
```

### 2. Добавить DATABASE_TYPE

```
Key: DATABASE_TYPE
Value: postgresql
Protected: OFF
Masked: OFF
```

### 3. Добавить DATABASE_URL

```
Key: DATABASE_URL
Value: postgresql://neondb_owner:npg_8c3SwJvYVGNh@ep-twilight-rain-ag491odm.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require
Protected: ON
Masked: ON
```

⚠️ **Важно:** 
- Protected: ON (только для защищённых веток)
- Masked: ON (скрыть в логах)

### 4. Добавить TELEGRAM_BOT_TOKEN

```
Key: TELEGRAM_BOT_TOKEN
Value: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
Protected: ON
Masked: ON
```

📝 **Где взять токен:**
- @BotFather в Telegram
- Команда: /newbot

### 5. Добавить TELEGRAM_ADMIN_CHAT_ID

```
Key: TELEGRAM_ADMIN_CHAT_ID
Value: 123456789
Protected: ON
Masked: OFF
```

📝 **Как узнать Chat ID:**
- В Telegram: @userinfobot
- Отправить: /start
- Получить ID

---

## Проверка

После добавления проверьте список:

```
✅ DATABASE_TYPE = postgresql
✅ DATABASE_URL = postgresql://***:***@***/*** (masked)
✅ TELEGRAM_BOT_TOKEN = ***:*** (masked)
✅ TELEGRAM_ADMIN_CHAT_ID = 123456789
```

---

## Запуск pipeline

```bash
git add .
git commit -m "Production ready"
git push origin main
```

**В GitLab UI:**
```
Build → Pipelines → Выбрать pipeline → Проверить статус
```

---

## Деплой на production

**Автоматически:**
- При merge в `main` → запустится pipeline
- Миграции применятся автоматически
- Деплой требует ручного подтверждения

**Вручную:**
```
Build → Pipelines → ▶️ deploy_production → Confirm
```

---

## Troubleshooting

### Pipeline failed на этапе migrate

```
1. Проверить DATABASE_URL в Variables
2. Убедиться что SSL mode=require
3. Проверить доступность БД:
   psql $DATABASE_URL -c "SELECT 1"
```

### Бот не запускается

```
1. Проверить TELEGRAM_BOT_TOKEN
2. Проверить формат: 1234567890:ABCdef...
3. Пересоздать токен в @BotFather
```

### Алерты не приходят

```
1. Проверить TELEGRAM_ADMIN_CHAT_ID
2. Убедиться что ID числовой
3. Проверить что бот добавлен в чат
```

---

## Безопасность

✅ **Сделано:**
- Пароли скрыты (Masked)
- Доступ только для protected branches
- Переменные не попадают в логи

❌ **Не делать:**
- Не коммитить .env с реальными токенами
- Не показывать скриншоты с токенами
- Не передавать токены в чатах

---

## Ссылки

- [GitLab Variables Documentation](https://docs.gitlab.com/ee/ci/variables/)
- [Protected Variables](https://docs.gitlab.com/ee/ci/variables/#protect-a-variable)
- [Masked Variables](https://docs.gitlab.com/ee/ci/variables/#mask-a-variable)
