"""Pytest fixtures and configuration."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.connection import DatabaseConnection
from src.database.models import Base


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def db_connection():
    """Create a test database connection."""
    db = DatabaseConnection("sqlite:///:memory:")
    db.create_tables()
    yield db


@pytest.fixture
def nlp_processor():
    """Create NLP processor instance."""
    from src.nlp.processor import NLPProcessor
    return NLPProcessor()
