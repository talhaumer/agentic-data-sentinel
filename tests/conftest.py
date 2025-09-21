"""Pytest configuration and fixtures."""

import pytest
import asyncio
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db, Base

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def db_session() -> Generator:
    """Create a test database session."""
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create session
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Drop tables
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session) -> Generator:
    """Create a test client."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_dataset_data():
    """Sample dataset data for testing."""
    return {"name": "test_events", "owner": "test_user", "source": "test_source"}


@pytest.fixture
def sample_anomaly_data():
    """Sample anomaly data for testing."""
    return {
        "dataset_id": 1,
        "table_name": "test_events",
        "column_name": "price",
        "issue_type": "null_rate",
        "severity": 3,
        "description": "High null rate detected",
        "extra": {"null_rate": 0.15},
    }
