"""Database connection management."""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base


class DatabaseConnection:
    """Database connection manager."""

    def __init__(self, database_url: str, echo: bool = False):
        """Initialize database connection."""
        self.database_url = database_url
        self.echo = echo
        self.engine = create_engine(database_url, echo=echo)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self) -> None:
        """Create all tables."""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self) -> None:
        """Drop all tables."""
        Base.metadata.drop_all(bind=self.engine)

    def get_session(self):
        """Get database session."""
        return self.SessionLocal()

    @staticmethod
    def get_sqlite_url(db_path: str = "./data/shopping.db") -> str:
        """Get SQLite connection URL."""
        path = Path(db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{path.absolute()}"

    @staticmethod
    def get_postgresql_url(
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
    ) -> str:
        """Get PostgreSQL connection URL."""
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
