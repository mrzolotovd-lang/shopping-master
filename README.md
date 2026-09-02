# Shopping Master

A home inventory management agent with automatic consumption tracking and a natural language interface.

## Features

- ✅ Daily automatic stock consumption based on configurable rules
- ✅ Manual stock updates via natural language (Russian)
- ✅ Automatic addition to shopping list when threshold is reached
- ✅ Multi-user support with priority levels
- ✅ Full operation history (audit log)
- ✅ Flexible consumption rules (% per day or absolute value)
- ✅ Multiple interfaces: CLI, Telegram bot, MCP-compatible chat
- ✅ SQLite (development) and PostgreSQL (production) support

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize database with test data

```bash
python -m src.main seed
```

### 3. Run commands

```bash
# Show all items
python -m src.main status

# Show shopping list
python -m src.main buy

# Run daily consumption
python -m src.main consume

# Check thresholds
python -m src.main check-thresholds
```

## Natural Language Examples

### Purchase

```
bought milk 2 liters
bought 5 yogurts
got cottage cheese
```

### Stock Update

```
half of the milk is left
milk is almost out
10 eggs left
sugar is running low
```

### Queries

```
what do we have at home?
shopping list
how much milk is left?
status milk
```

## Project Structure

```
shopping-master/
├── src/
│   ├── core/           # Business logic (agent, consumption, threshold)
│   ├── database/       # SQLAlchemy models and repositories
│   ├── nlp/            # NLP processor (regex + Russian dictionary)
│   ├── interfaces/     # Interfaces (chat, Telegram, CLI)
│   └── utils/          # Utilities
├── scripts/            # Utility scripts (seed, export, import, migrate)
├── tests/              # Unit and integration tests
├── config/             # YAML configuration files
└── migrations/         # Alembic migrations
```

## Configuration

Configuration files are located in `config/`:

- `default.yaml` — default configuration
- `development.yaml` — local development (SQLite)
- `production.yaml` — production (PostgreSQL)

Environment variables are supported via `${VAR_NAME}` syntax.

## Database

### Phase 1 (Development)
SQLite locally at `./data/shopping.db`

### Phase 2 (Production)
PostgreSQL (Yandex Cloud / Neon / Supabase)

Migration:

```bash
# Export
python -m src.main export --output data/backup.json

# Import
python -m src.main import --input data/backup.json
```

## Telegram Bot

```bash
# Set environment variables
export TELEGRAM_BOT_TOKEN="your_token_here"
export TELEGRAM_ADMIN_CHAT_ID="your_chat_id"

# Run bot
python -m src.bot
```

Supported commands:
- `/start` — welcome message
- `/buy` — show shopping list
- `/status` — show all items
- `/status <item>` — show specific item
- `/consume` — run daily consumption
- `/thresholds` — check thresholds
- `/help` — help

## Testing

```bash
pytest
pytest --cov=src --cov-report=html
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for full documentation.

### Key Design Decisions

- **Repository Pattern** — all database access goes through dedicated repository classes
- **Dependency Injection** — repositories and engines receive the database connection
- **Multi-layer NLP** — regex patterns + Russian word normalizer + unit/stock-level dictionaries
- **Audit Log** — every stock-changing operation is recorded in `operation_log`
- **Soft Delete** — items are marked inactive rather than deleted

## Roadmap

### Phase 1 (MVP) — Current
- [x] Project structure
- [x] Database schema
- [x] Core logic (consumption, thresholds)
- [x] NLP (regex + dictionary)
- [x] CLI interface
- [x] Unit and integration tests

### Phase 2 (Production)
- [x] Telegram bot
- [x] GitLab CI/CD
- [x] PostgreSQL migration
- [x] Backup scripts
- [ ] Yandex Cloud Functions deployment

### Phase 3 (Improvements)
- [ ] spaCy NLP
- [ ] LLM API integration
- [ ] Web interface
- [ ] Analytics dashboard

## Tech Stack

- **Python 3.11+**
- **SQLAlchemy 2.0** — ORM
- **Alembic** — database migrations
- **Pydantic v2** — configuration validation
- **Loguru** — logging
- **aiogram 3.x** — Telegram bot framework
- **pytest** — testing

## License

MIT
