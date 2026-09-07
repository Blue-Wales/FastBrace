"""
测试配置
Pytest配置和共享固定件。
"""

from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture(scope="session")
def db_engine():
    """Create a test database engine."""
    # Use SQLite for testing
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
    )
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create a new database session for each test."""
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client():
    """Create a test client for API testing."""
    from fastapi.testclient import TestClient

    from infrastructure.core.app import create_app
    from infrastructure.core.settings import app_settings

    app = create_app(app_settings)
    with TestClient(app) as test_client:
        yield test_client
