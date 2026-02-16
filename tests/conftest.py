import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import app
from app.database import Base, get_db
from app.models import Voucher

# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# StaticPool is required for in-memory SQLite to persist across connections
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override get_db to use test database"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Create tables once at startup
Base.metadata.create_all(bind=engine)

# Override the dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db():
    """Database session fixture - creates fresh session for each test"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db):
    """Test client fixture - ensures database is available"""

    def override_get_db_for_tests():
        yield db

    app.dependency_overrides[get_db] = override_get_db_for_tests

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def valid_future_date():
    """Generate a valid future date"""
    return datetime.now() + timedelta(days=30)


@pytest.fixture
def expired_date():
    """Generate an expired date"""
    return datetime.now() - timedelta(days=1)


@pytest.fixture
def sample_voucher_data(valid_future_date):
    """Sample voucher creation data"""
    return {
        "discount_percentage": 15.5,
        "expiration_date": valid_future_date.isoformat()
    }


@pytest.fixture
def sample_voucher(db, valid_future_date):
    """Create a sample voucher in the database"""
    voucher = Voucher(
        code="TEST123456",
        discount_percentage=20.0,
        expiration_date=valid_future_date,
        active=True
    )
    db.add(voucher)
    db.commit()
    db.refresh(voucher)
    return voucher