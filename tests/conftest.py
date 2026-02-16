import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import os

from app.main import app
from app.database import Base, get_db
from app.models import Voucher

# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def db():
    """Database session fixture"""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


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