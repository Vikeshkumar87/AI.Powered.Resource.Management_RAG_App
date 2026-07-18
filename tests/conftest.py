"""
Test configuration and fixtures.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# In-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI test client with test database."""
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_resource_data():
    """Sample resource data for tests."""
    return {
        "name": "Test Employee",
        "email": "test@example.com",
        "employee_id": "TEST001",
        "department": "Engineering",
        "designation": "Software Engineer",
        "skills": ["Python", "FastAPI", "Docker"],
        "experience_years": 5.0,
        "location": "Bangalore",
        "availability_percentage": 100.0,
        "is_on_bench": True,
        "certifications": ["AWS"],
        "preferred_roles": ["Backend Developer"],
    }


@pytest.fixture
def sample_project_data():
    """Sample project data for tests."""
    return {
        "name": "Test Project",
        "project_code": "TEST_PROJ_001",
        "client": "Test Client Corp",
        "description": "A test project for unit testing",
        "status": "planning",
        "required_skills": ["Python", "Docker"],
        "team_size_required": 3,
        "priority": "high",
        "domain": "Testing",
    }
