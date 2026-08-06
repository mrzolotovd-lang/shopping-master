# Архитектура Агента Управления Домашними Запасами

**Версия:** 1.0  
**Дата:** 2026-08-06  
**Статус:** Phase 1 (Разработка)

---

## 1. Общее Описание

Агент для отслеживания домашних запасов товаров с автоматическим списанием по расписанию и NLP-интерфейсом для ручных обновлений.

### Цели
- Ежедневное автоматическое списание остатков по правилам
- Ручное обновление через естественный язык (чат/Telegram)
- Автоматическое добавление в список покупок при достижении порога
- Поддержка нескольких пользователей с приоритетами

---

## 2. Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                        ИНТЕРФЕЙСЫ                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Chat (MCP)    │  │  Telegram Bot   │  │   CLI Commands  │ │
│  │   (Phase 1)     │  │   (Phase 2)     │  │   (Phase 1)     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      NLP PROCESSOR                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Phase 1: Regex + Dictionary                            │   │
│  │  Phase 2: spaCy                                         │   │
│  │  Phase 3: LLM API (optional)                            │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CORE AGENT LOGIC                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Consumption  │  │  Threshold   │  │   Shopping List      │  │
│  │  Engine      │  │  Checker     │  │   Manager            │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Phase 1: SQLite (local dev)                            │   │
│  │  Phase 2: PostgreSQL (Yandex Cloud / Neon / Supabase)   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     ORCHESTRATION                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Phase 1: Local cron / manual trigger                   │   │
│  │  Phase 2: GitLab CI/CD Scheduled Pipeline               │   │
│  │  Phase 2: Yandex Cloud Functions + Timer                │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Схема Базы Данных

### 3.1. Таблицы

```sql
-- Пользователи
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE,
    name VARCHAR(100) NOT NULL,
    priority INTEGER DEFAULT 5,  -- 1 = highest priority
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Категории товаров
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    default_consumption_rule_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (default_consumption_rule_id) REFERENCES consumption_rules(id)
);

-- Правила списания (consumption rules)
CREATE TABLE consumption_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    rule_type VARCHAR(20) NOT NULL CHECK (rule_type IN ('percentage_daily', 'absolute_daily', 'manual')),
    value DECIMAL(10,4) NOT NULL,  -- процент или абсолютное значение
    unit VARCHAR(20) DEFAULT 'day',  -- day, week
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Товары
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    category_id INTEGER,
    current_stock DECIMAL(10,2) NOT NULL DEFAULT 0,  -- текущий остаток
    package_size DECIMAL(10,2) NOT NULL DEFAULT 1,  -- размер упаковки
    unit VARCHAR(50) NOT NULL DEFAULT 'шт',  -- единица измерения (л, кг, шт)
    reorder_threshold DECIMAL(5,2) NOT NULL DEFAULT 10,  -- порог покупки (% от package_size)
    consumption_rule_id INTEGER,  -- индивидуальное правило (null = наследовать от категории)
    auto_fill_mode VARCHAR(20) DEFAULT 'ask' CHECK (auto_fill_mode IN ('ask', 'package', 'smart')),
    purchase_count INTEGER DEFAULT 0,  -- счётчик покупок для ML-предложений
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (consumption_rule_id) REFERENCES consumption_rules(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Список покупок
CREATE TABLE shopping_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    user_id INTEGER,  -- кто добавил
    quantity DECIMAL(10,2) DEFAULT 1,  -- рекомендуемое количество (упаковок)
    reason VARCHAR(50) DEFAULT 'threshold',  -- threshold, manual, out_of_stock
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'cancelled')),
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES items(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(item_id, status)  -- один активный товар в списке
);

-- История операций (audit log)
CREATE TABLE operation_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    user_id INTEGER,
    operation_type VARCHAR(30) NOT NULL CHECK (operation_type IN (
        'purchase', 'manual_update', 'auto_consumption', 
        'added_to_shopping', 'removed_from_shopping', 'rule_change'
    )),
    old_value DECIMAL(10,2),
    new_value DECIMAL(10,2),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES items(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Индексы для производительности
CREATE INDEX idx_items_category ON items(category_id);
CREATE INDEX idx_items_active ON items(is_active);
CREATE INDEX idx_shopping_status ON shopping_list(status);
CREATE INDEX idx_operation_log_item ON operation_log(item_id);
CREATE INDEX idx_operation_log_created ON operation_log(created_at);
```

### 3.2. ER-диаграмма

```
┌─────────────┐       ┌──────────────┐       ┌──────────────────┐
│   users     │       │  categories  │       │consumption_rules │
├─────────────┤       ├──────────────┤       ├──────────────────┤
│ id          │       │ id           │       │ id               │
│ telegram_id │       │ name         │       │ name             │
│ name        │       │ description  │──┐    │ rule_type        │
│ priority    │       │ default_rule │──┼───▶│ value            │
└─────────────┘       └──────────────┘  │    │ unit             │
       │                                │    └──────────────────┘
       │                                │
       │                                │
       ▼                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                           items                                  │
├─────────────────────────────────────────────────────────────────┤
│ id | name | category_id │ current_stock | package_size | unit  │
│ consumption_rule_id | auto_fill_mode | purchase_count | active │
└─────────────────────────────────────────────────────────────────┘
       │
       ├──────────────┐
       ▼              ▼
┌──────────────┐  ┌──────────────────┐
│shopping_list │  │  operation_log   │
├──────────────┤  ├──────────────────┤
│ id           │  │ id               │
│ item_id      │  │ item_id          │
│ user_id      │  │ user_id          │
│ quantity     │  │ operation_type   │
│ status       │  │ old_value        │
│ completed_at │  │ new_value        │
└──────────────┘  │ comment          │
                  └──────────────────┘
```

---

## 4. Структура Проекта

```
shopping-master/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Точка входа
│   ├── config.py               # Конфигурация
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── agent.py            # Основная логика агента
│   │   ├── consumption.py      # Движок списания
│   │   ├── threshold.py        # Проверка порогов
│   │   └── shopping.py         # Управление списком покупок
│   │
│   ├── nlp/
│   │   ├── __init__.py
│   │   ├── processor.py        # NLP процессор
│   │   ├── patterns.py         # Regex паттерны
│   │   └── dictionary.py       # Словари (мало=10%, половина=50%)
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py       # Подключение к БД
│   │   ├── models.py           # SQLAlchemy модели
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── user_repo.py
│   │   │   ├── item_repo.py
│   │   │   ├── category_repo.py
│   │   │   ├── rule_repo.py
│   │   │   ├── shopping_repo.py
│   │   │   └── log_repo.py
│   │   └── migrations/
│   │       └── versions/       # Alembic миграции
│   │
│   ├── interfaces/
│   │   ├── __init__.py
│   │   ├── chat.py             # MCP чат интерфейс
│   │   ├── telegram.py         # Telegram бот (Phase 2)
│   │   └── cli.py              # CLI команды
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py           # Логирование
│       ├── notifications.py    # Уведомления
│       └── backup.py           # Бэкапы
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # pytest фикстуры
│   ├── unit/
│   │   ├── test_consumption.py
│   │   ├── test_threshold.py
│   │   └── test_nlp.py
│   ├── integration/
│   │   ├── test_database.py
│   │   └── test_agent.py
│   └── e2e/
│       └── test_scenarios.py
│
├── scripts/
│   ├── seed_data.py            # Тестовые данные
│   ├── export.py               # Экспорт (SQLite → JSON)
│   ├── import.py               # Импорт (JSON → PostgreSQL)
│   └── backup.py               # Ручной бэкап
│
├── migrations/                 # Alembic миграции
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── config/
│   ├── default.yaml            # Конфиг по умолчанию
│   ├── development.yaml        # Dev конфигурация
│   └── production.yaml         # Prod конфигурация
│
├── .gitlab-ci.yml              # GitLab CI/CD
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── pytest.ini
├── alembic.ini
└── README.md
```

---

## 5. План Реализации по Фазам

### Phase 1: MVP (2-3 недели)

**Цель:** Работающий агент с локальной БД и чат-интерфейсом

| Задача | Оценка | Приоритет |
|--------|--------|-----------|
| 1.1. Настройка проекта (структура, зависимости) | 0.5 дня | P0 |
| 1.2. Схема БД + SQLAlchemy модели | 1 день | P0 |
| 1.3. Repositories (CRUD для всех таблиц) | 2 дня | P0 |
| 1.4. Consumption Engine (списание по правилам) | 1 день | P0 |
| 1.5. Threshold Checker (проверка порогов) | 0.5 дня | P0 |
| 1.6. NLP Processor (regex + словарь) | 2 дня | P0 |
| 1.7. Chat Interface (MCP) | 1 день | P0 |
| 1.8. CLI Commands (status, buy, add) | 1 день | P1 |
| 1.9. Тестовые данные (10 категорий, 10 товаров) | 0.5 дня | P1 |
| 1.10. Юнит-тесты (80% покрытие) | 2 дня | P1 |
| 1.11. Интеграционные тесты | 1 день | P2 |

**Итого Phase 1:** ~13 рабочих дней

---

### Phase 2: Production (2-3 недели)

**Цель:** Развёртывание в облаке + Telegram бот

| Задача | Оценка | Приоритет |
|--------|--------|-----------|
| 2.1. Миграция на PostgreSQL (Neon/Supabase) | 1 день | P0 |
| 2.2. GitLab CI/CD Pipeline | 1 день | P0 |
| 2.3. Yandex Cloud Functions настройка | 1 день | P0 |
| 2.4. Scheduled Pipeline (cron ежедневно) | 0.5 дня | P0 |
| 2.5. Telegram Bot (aiogram) | 2 дня | P0 |
| 2.6. NLP улучшение (spaCy) | 2 дня | P1 |
| 2.7. Уведомления (Telegram при критических ошибках) | 1 день | P1 |
| 2.8. Бэкапы (еженедельно в Object Storage) | 1 день | P1 |
| 2.9. Мониторинг (GitLab notifications) | 0.5 дня | P1 |
| 2.10. Документация (README, API) | 1 день | P2 |

**Итого Phase 2:** ~11 рабочих дней

---

### Phase 3: Улучшения (опционально)

| Задача | Оценка |
|--------|--------|
| 3.1. LLM API для NLP (GPT/Claude) | 2 дня + $ |
| 3.2. GitLab Issues для списка покупок | 1 день |
| 3.3. Аналитика потребления (графики, отчёты) | 3 дня |
| 3.4. Мульти-язычность | 1 день |
| 3.5. Веб-интерфейс (FastAPI + React) | 5 дней |

---

## 6. API / Команды

### 6.1. Чат-команды (Phase 1)

```
# Покупка
"купил молоко 2 литра"
"купил 5 йогуртов"
"приобрёл творог"

# Обновление остатка
"молока осталось половина"
"молоко почти закончилось"
"яиц осталось 10 штук"
"сахара совсем мало"

# Запросы
"что есть дома?"
"список покупок"
"сколько осталось молока?"
"статус молоко"

# Управление
"добавь товар молоко категория молочные упаковка 1л"
"измени правило молоко 5% в день"
"удали товар молоко"
```

### 6.2. CLI Команды (Phase 1)

```bash
# Запуск агента
python src/main.py run              # Основной цикл
python src/main.py consume          # Принудительное списание
python src/main.py check-thresholds # Проверка порогов

# Управление данными
python src/main.py status           # Все товары с остатками
python src/main.py buy              # Список покупок
python src/main.py item milk        # Статус конкретного товара

# Администрирование
python src/main.py seed             # Заполнить тестовыми данными
python src/main.py export           # Экспорт в JSON
python src/main.py import           # Импорт из JSON
python src/main.py backup           # Создать бэкап
```

### 6.3. Telegram Команды (Phase 2)

```
/start - Приветствие и инструкции
/buy - Список покупок
/status - Все товары
/status <товар> - Статус товара
/add <товар> - Добавить товар
/help - Справка
```

---

## 7. NLP Словарь (Phase 1)

### 7.1. Паттерны для покупок

```python
PURCHASE_PATTERNS = [
    r"купил\s+(?P<item>.+?)\s+(?P<amount>\d+(?:\.\d+)?)\s*(?P<unit>л|кг|г|мл|шт|упак)?",
    r"купил\s+(?P<item>.+?)(?:\s|$)",
    r"приобрёл\s+(?P<item>.+?)\s+(?P<amount>\d+(?:\.\d+)?)\s*(?P<unit>л|кг|г|мл|шт|упак)?",
    r"добавь\s+(?P<item>.+?)\s+(?P<amount>\d+(?:\.\d+)?)\s*(?P<unit>л|кг|г|мл|шт|упак)?",
]
```

### 7.2. Паттерны для обновления остатка

```python
UPDATE_PATTERNS = [
    r"(?P<item>.+?)\s+осталось\s+(?P<amount>\d+(?:\.\d+)?)\s*(?P<unit>л|кг|г|мл|шт)?",
    r"(?P<item>.+?)\s+(?P<percent>половина|50%)\s*",
    r"(?P<item>.+?)\s+(?P<level>совсем\s+мало|почти\s+нет|мало|немного|много|почти\s+полная)",
]
```

### 7.3. Словарь уровней

```python
STOCK_LEVELS = {
    "совсем мало": 0.10,
    "почти нет": 0.10,
    "нет": 0.0,
    "закончилось": 0.0,
    "мало": 0.25,
    "немного": 0.25,
    "половина": 0.50,
    "пол-упаковки": 0.50,
    "больше половины": 0.70,
    "почти полная": 0.90,
    "много": 0.90,
    "новая упаковка": 1.0,
    "полная": 1.0,
}
```

---

## 8. Зависимости

### 8.1. requirements.txt

```
# Core
sqlalchemy>=2.0.0
alembic>=1.13.0
pyyaml>=6.0
python-dotenv>=1.0.0

# NLP (Phase 1)
# No external dependencies - regex only

# NLP (Phase 2)
# spacy>=3.7.0
# razdel>=0.5.0  # Russian NLP

# Telegram (Phase 2)
# aiogram>=3.4.0

# Database
# psycopg2-binary>=2.9.0  # PostgreSQL
aiosqlite>=0.19.0  # SQLite (Phase 1)

# Utils
pydantic>=2.0.0
loguru>=0.7.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-asyncio>=0.21.0
```

### 8.2. requirements-dev.txt

```
-r requirements.txt

# Development
black>=23.0.0
flake8>=6.1.0
mypy>=1.7.0
isort>=5.12.0

# Debugging
ipdb>=0.13.0
```

---

## 9. Конфигурация

### 9.1. config/default.yaml

```yaml
app:
  name: "Shopping Master"
  version: "1.0.0"
  environment: "development"

database:
  type: "sqlite"  # Phase 1: sqlite, Phase 2: postgresql
  sqlite_path: "./data/shopping.db"
  postgresql_url: "${DATABASE_URL}"  # Phase 2

users:
  priorities:
    - telegram_id: null  # Owner (Phase 1)
      name: "Owner"
      priority: 1
    - telegram_id: null  # Wife (Phase 2)
      name: "Wife"
      priority: 2

consumption:
  default_unit: "шт"
  default_package_size: 1
  default_reorder_threshold: 10  # percent

nlp:
  language: "ru"
  phase: 1  # 1=regex, 2=spacy, 3=llm

notifications:
  enabled: false  # Phase 2
  telegram_bot_token: "${TELEGRAM_BOT_TOKEN}"
  admin_chat_id: null

backup:
  enabled: false  # Phase 2
  schedule: "0 3 * * 0"  # Weekly on Sunday 03:00
  storage: "s3"  # or "local"
  retention_days: 60

logging:
  level: "INFO"
  format: "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
  file: "./logs/shopping.log"
```

---

## 10. Тестовые Данные (Seed)

### 10.1. Категории (10)

```python
CATEGORIES = [
    "Молочные продукты",
    "Детское питание",
    "Мясо/Птица/Рыба",
    "Крупы/Макароны/Хлеб",
    "Овощи/Фрукты",
    "Бакалея",
    "Бытовая химия",
    "Гигиена",
    "Напитки",
    "Снеки/Сладости",
]
```

### 10.2. Правила списания

```python
RULES = [
    {"name": "Скоропорт (5%/день)", "type": "percentage_daily", "value": 5},
    {"name": "Среднее (2%/день)", "type": "percentage_daily", "value": 2},
    {"name": "Долгое (0.5%/день)", "type": "percentage_daily", "value": 0.5},
    {"name": "Не портится (0%)", "type": "percentage_daily", "value": 0},
    {"name": "Ручное", "type": "manual", "value": 0},
]
```

### 10.3. Товары для отладки (10)

```python
ITEMS = [
    {"name": "Молоко", "category": "Молочные продукты", "package_size": 1, "unit": "л", "rule": "Скоропорт"},
    {"name": "Кефир", "category": "Молочные продукты", "package_size": 0.5, "unit": "л", "rule": "Скоропорт"},
    {"name": "Йогурт", "category": "Молочные продукты", "package_size": 1, "unit": "шт", "rule": "Скоропорт"},
    {"name": "Творог", "category": "Молочные продукты", "package_size": 0.2, "unit": "кг", "rule": "Скоропорт"},
    {"name": "Пюре детское", "category": "Детское питание", "package_size": 1, "unit": "шт", "rule": "Долгое"},
    {"name": "Каша детская", "category": "Детское питание", "package_size": 0.4, "unit": "кг", "rule": "Долгое"},
    {"name": "Подгузники", "category": "Гигиена", "package_size": 1, "unit": "упак", "rule": "Не портится"},
    {"name": "Влажные салфетки", "category": "Гигиена", "package_size": 1, "unit": "упак", "rule": "Не портится"},
    {"name": "Стиральный порошок", "category": "Бытовая химия", "package_size": 1.5, "unit": "кг", "rule": "Не портится"},
    {"name": "Туалетная бумага", "category": "Бытовая химия", "package_size": 1, "unit": "упак", "rule": "Не портится"},
]
```

---

## 11. Риски и Митигация

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| NLP не понимает команды | Средняя | Высокое | Уточняющие вопросы, логирование непонятых фраз |
| Конфликты пользователей | Средняя | Среднее | Audit log + уведомления |
| Потеря данных БД | Низкая | Критичное | Еженедельные бэкапы + Point-in-time recovery |
| Telegram API лимиты | Низкая | Среднее | Rate limiting, очередь сообщений |
| Cloud Functions холодный старт | Средняя | Низкое | Keep-warm пинг каждые 5 мин |

---

## 12. Метрики Успеха

### Phase 1 (MVP)
- [ ] 10+ товаров в БД
- [ ] 80%+ покрытие тестами
- [ ] NLP распознаёт 80% типовых команд
- [ ] Ежедневное списание работает

### Phase 2 (Production)
- [ ] Развёрнуто в облаке
- [ ] Telegram бот работает
- [ ] Бэкапы настроены
- [ ] 2+ активных пользователя

### Phase 3 (Improvements)
- [ ] 50+ товаров отслеживается
- [ ] <1% ложных NLP-распознаваний
- [ ] Пользователи довольны UX

---

## 13. Следующие Шаги

1. **Создать структуру проекта** (скрипт инициализации)
2. **Настроить БД и миграции** (Alembic + SQLAlchemy)
3. **Реализовать repositories** (CRUD операции)
4. **Написать Consumption Engine** (списание по расписанию)
5. **Создать NLP Processor** (regex + словарь)
6. **Добавить тестовые данные** (seed скрипт)
7. **Покрыть тестами** (pytest)

---

## Приложения

### A. Глоссарий

| Термин | Определение |
|--------|-------------|
| Item | Товар, который отслеживается |
| Package Size | Размер упаковки (1л молока, 10шт яиц) |
| Consumption Rule | Правило списания (% в день или абсолютное значение) |
| Reorder Threshold | Порог для добавления в список покупок |
| Auto-fill Mode | Режим авто-заполнения количества (ask/package/smart) |

### B. Ссылки

- [GitLab CI/CD Docs](https://docs.gitlab.com/ee/ci/)
- [Yandex Cloud Functions](https://yandex.cloud/ru/docs/functions/)
- [Neon PostgreSQL](https://neon.tech/)
- [Supabase](https://supabase.com/)
- [aiogram Docs](https://docs.aiogram.dev/)
- [spaCy Russian](https://spacy.io/models/ru)
