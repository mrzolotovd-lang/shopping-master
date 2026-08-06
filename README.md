# Shopping Master

Агент для управления домашними запасами с автоматическим списанием и NLP-интерфейсом.

## Возможности

- ✅ Ежедневное автоматическое списание остатков по правилам
- ✅ Ручное обновление через естественный язык (русский)
- ✅ Автоматическое добавление в список покупок при достижении порога
- ✅ Поддержка нескольких пользователей с приоритетами
- ✅ Полная история операций (audit log)
- ✅ Гибкие правила списания (% в день или абсолютное значение)

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Инициализация БД и тестовые данные

```bash
python -m src.main seed
```

### 3. Запуск

```bash
# Показать все товары
python -m src.main status

# Показать список покупок
python -m src.main buy

# Запустить ежедневное списание
python -m src.main consume

# Проверить пороги
python -m src.main check-thresholds
```

## Примеры команд (NLP)

### Покупка
```
купил молоко 2 литра
купил 5 йогуртов
приобрёл творог
```

### Обновление остатка
```
молока осталось половина
молоко почти закончилось
яиц осталось 10 штук
сахара совсем мало
```

### Запросы
```
что есть дома?
список покупок
сколько осталось молока?
статус молоко
```

## Структура проекта

```
shopping-master/
├── src/
│   ├── core/           # Бизнес-логика агента
│   ├── database/       # Модели БД и репозитории
│   ├── nlp/            # NLP процессор (regex + словарь)
│   ├── interfaces/     # Интерфейсы (чат, Telegram, CLI)
│   └── utils/          # Утилиты
├── scripts/            # Скрипты (seed, export, import)
├── tests/              # Тесты
├── config/             # Конфигурация
└── migrations/         # Alembic миграции
```

## Конфигурация

Конфигурационные файлы в `config/`:

- `default.yaml` - конфигурация по умолчанию
- `development.yaml` - локальная разработка (SQLite)
- `production.yaml` - продакшен (PostgreSQL)

## База данных

### Phase 1 (Development)
SQLite локально в `./data/shopping.db`

### Phase 2 (Production)
PostgreSQL (Yandex Cloud / Neon / Supabase)

Миграция:
```bash
# Экспорт
python -m src.main export --output data/backup.json

# Импорт
python -m src.main import --input data/backup.json
```

## Тестирование

```bash
pytest
pytest --cov=src --cov-report=html
```

## Архитектура

См. [ARCHITECTURE.md](ARCHITECTURE.md) для полной документации.

## План развития

### Phase 1 (MVP) - Сейчас
- [x] Структура проекта
- [x] Схема БД
- [x] Core логика (списание, пороги)
- [x] NLP (regex + словарь)
- [ ] CLI интерфейс
- [ ] Тесты

### Phase 2 (Production)
- [ ] Telegram бот
- [ ] GitLab CI/CD
- [ ] Yandex Cloud Functions
- [ ] PostgreSQL миграция
- [ ] Бэкапы

### Phase 3 (Improvements)
- [ ] spaCy NLP
- [ ] LLM API интеграция
- [ ] Веб-интерфейс
- [ ] Аналитика

## Лицензия

MIT
