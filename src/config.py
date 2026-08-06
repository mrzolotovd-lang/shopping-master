"""Application configuration."""

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class DatabaseConfig(BaseModel):
    """Database configuration."""

    type: str = "sqlite"
    sqlite_path: str = "./data/shopping.db"
    postgresql_url: str | None = None


class UserPriority(BaseModel):
    """User priority configuration."""

    telegram_id: int | None = None
    name: str
    priority: int = 5


class UsersConfig(BaseModel):
    """Users configuration."""

    priorities: list[UserPriority] = Field(default_factory=list)


class ConsumptionConfig(BaseModel):
    """Consumption rules configuration."""

    default_unit: str = "шт"
    default_package_size: float = 1.0
    default_reorder_threshold: float = 10.0


class NLPConfig(BaseModel):
    """NLP configuration."""

    language: str = "ru"
    phase: int = 1


class NotificationsConfig(BaseModel):
    """Notifications configuration."""

    enabled: bool = False
    telegram_bot_token: str | None = None
    admin_chat_id: int | None = None


class BackupConfig(BaseModel):
    """Backup configuration."""

    enabled: bool = False
    schedule: str = "0 3 * * 0"
    storage: str = "s3"
    retention_days: int = 60


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = "INFO"
    format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    file: str = "./logs/shopping.log"


class AppConfig(BaseModel):
    """Main application configuration."""

    name: str = "Shopping Master"
    version: str = "1.0.0"
    environment: str = "development"


class Config(BaseModel):
    """Root configuration."""

    app: AppConfig = Field(default_factory=AppConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    users: UsersConfig = Field(default_factory=UsersConfig)
    consumption: ConsumptionConfig = Field(default_factory=ConsumptionConfig)
    nlp: NLPConfig = Field(default_factory=NLPConfig)
    notifications: NotificationsConfig = Field(default_factory=NotificationsConfig)
    backup: BackupConfig = Field(default_factory=BackupConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)


class ConfigManager:
    """Configuration manager."""

    def __init__(self, config_dir: Path | None = None):
        """Initialize config manager."""
        self.config_dir = config_dir or Path(__file__).parent.parent / "config"
        self._config: Config | None = None

    def load(self, environment: str = "development") -> Config:
        """Load configuration from YAML files."""
        default_path = self.config_dir / "default.yaml"
        env_path = self.config_dir / f"{environment}.yaml"

        config_dict: dict[str, Any] = {}

        if default_path.exists():
            with open(default_path) as f:
                config_dict.update(self._load_yaml(f))

        if env_path.exists():
            with open(env_path) as f:
                env_config = self._load_yaml(f)
                self._deep_update(config_dict, env_config)

        config_dict = self._expand_env_vars(config_dict)
        self._config = Config(**config_dict)
        return self._config

    def _load_yaml(self, file_obj) -> dict[str, Any]:
        """Load YAML from file object."""
        return yaml.safe_load(file_obj) or {}

    def _deep_update(self, base: dict[str, Any], update: dict[str, Any]) -> None:
        """Deep update nested dictionary."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value

    def _expand_env_vars(self, config: dict[str, Any]) -> dict[str, Any]:
        """Expand environment variables in config values."""
        result: dict[str, Any] = {}
        for key, value in config.items():
            if isinstance(value, dict):
                result[key] = self._expand_env_vars(value)
            elif isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                result[key] = os.environ.get(env_var, value)
            else:
                result[key] = value
        return result

    @property
    def config(self) -> Config:
        """Get loaded configuration."""
        if self._config is None:
            raise RuntimeError("Configuration not loaded. Call load() first.")
        return self._config


config_manager = ConfigManager()


def get_config() -> Config:
    """Get current configuration."""
    return config_manager.config
