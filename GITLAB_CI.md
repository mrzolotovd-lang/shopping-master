# GitLab CI/CD — Shopping Master

## Настройка

### 1. GitLab Variables

В GitLab UI: **Settings → CI/CD → Variables**

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL URL | `postgresql://user:pass@host/db` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | `1234567890:ABCdef...` |
| `SSH_PRIVATE_KEY` | SSH key for deploy | `-----BEGIN OPENSSH...` |
| `STAGING_HOST` | Staging server | `staging.example.com` |
| `STAGING_USER` | Staging SSH user | `deploy` |
| `STAGING_DIR` | Staging app directory | `/var/www/shopping-master` |
| `PROD_HOST` | Production server | `prod.example.com` |
| `PROD_USER` | Production SSH user | `deploy` |
| `PROD_DIR` | Production app directory | `/var/www/shopping-master` |
| `S3_BUCKET` | S3 bucket for backups | `shopping-backups` |
| `AWS_ACCESS_KEY_ID` | AWS access key | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | `...` |

### 2. Pipeline Stages

```
test → lint → build → deploy_staging → deploy_production
```

**test:**
- Запускает pytest с coverage
- Артефакты: coverage.xml, htmlcov/
- Срабатывает на MR и main/develop

**lint:**
- ruff check + format
- mypy type checking
- allow_failure: true

**build:**
- Компиляция Python файлов
- Артефакты для деплоя

**deploy_staging:**
- Ручной запуск (manual)
- Только develop ветка
- SSH деплой

**deploy_production:**
- Ручной запуск (manual)
- Только main ветка
- SSH деплой + restart systemd

### 3. Scheduled Pipelines

В GitLab UI: **Build → Pipeline Schedules**

**Ежедневное списание:**
- Schedule: `0 3 * * *` (каждый день в 3:00)
- Branch: `main`
- Variables: `DATABASE_URL`

**Бэкап:**
- Schedule: `0 2 * * 0` (воскресенье в 2:00)
- Branch: `main`
- Variables: `S3_BUCKET`, `DATABASE_URL`, `PROD_*`

### 4. Protected Branches

**Settings → Repository → Protected Branches**

| Branch | Allowed to merge | Allowed to push |
|--------|------------------|-----------------|
| `main` | Maintainers | Maintainers |
| `develop` | Developers + | Developers + |

### 5. Merge Request Pipeline

Автоматически запускается при создании MR:
- ✅ Тесты (pytest)
- ✅Lint (ruff, mypy)
- ✅ Build

### 6. Деплой

**Staging (develop):**
```bash
# На сервере
cd /var/www/shopping-master
git pull
source venv/bin/activate
pip install -r requirements.txt
# Бот перезапустится автоматически (systemd)
```

**Production (main):**
```bash
# CI/CD делает:
ssh prod@host "cd /var/www/shopping-master && git pull"
ssh prod@host "systemctl restart shopping-bot"
```

### 7. Мониторинг

**Pipeline status:**
- https://gitlab.com/{user}/{project}/-/pipelines

**Coverage:**
- https://gitlab.com/{user}/{project}/-/commits/main

**Deployments:**
- https://gitlab.com/{user}/{project}/-/environments

### 8. Troubleshooting

**Pipeline failed:**
```bash
# Посмотреть логи в GitLab UI
# Или запустить локально:
docker run --rm -it -v $(pwd):/app python:3.12 bash
cd /app
pip install -r requirements.txt
pytest tests/ -v
```

**Deploy failed:**
```bash
# Проверить SSH ключ
ssh -i ~/.ssh/id_ed25519 deploy@staging.example.com

# Проверить переменные
echo $STAGING_HOST
echo $SSH_PRIVATE_KEY
```

**Daily consumption failed:**
```bash
# Запустить вручную
python scripts/daily_consumption.py

# Проверить логи
journalctl -u shopping-bot -f
```

## Примеры

### Создать MR

```bash
git checkout -b feature/new-feature
git commit -m "Add new feature"
git push origin feature/new-feature
# Создать MR в GitLab UI
```

### Запустить деплой вручную

1. Перейти в **Build → Pipelines**
2. Найти нужный pipeline
3. Нажать ▶️ на кнопке deploy
4. Выбрать environment

### Добавить переменную

```bash
# Или через GitLab API:
curl --request POST \
  --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.com/api/v4/projects/$PROJECT_ID/variables" \
  --form "key=MY_VAR" \
  --form "value=secret_value" \
  --form "protected=true"
```

## Интеграция с Telegram

После деплоя бот автоматически:
1. Подключается к PostgreSQL
2. Запускается через systemd
3. Отвечает на команды

Проверка:
```
/start
/status
купил молоко 2л
```
