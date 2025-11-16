import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base, get_db
from main import app
from utils.seed_exercises import seed_exercises


# Create test database in memory
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
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

    # Seed exercises
    from models.database import Exercise
    if db.query(Exercise).filter(Exercise.is_custom == False).count() == 0:
        # Manually seed a few exercises for testing
        exercises = [
            Exercise(name="Bench Press", category="push", muscle_groups=["chest", "triceps"], equipment="barbell", is_custom=False),
            Exercise(name="Squat", category="legs", muscle_groups=["quadriceps", "glutes"], equipment="barbell", is_custom=False),
            Exercise(name="Deadlift", category="pull", muscle_groups=["back", "hamstrings"], equipment="barbell", is_custom=False),
            Exercise(name="Pull-Ups", category="pull", muscle_groups=["back", "biceps"], equipment="bodyweight", is_custom=False),
            Exercise(name="Running", category="cardio", muscle_groups=["quadriceps", "hamstrings"], equipment="none", is_custom=False),
        ]
        for ex in exercises:
            db.add(ex)
        db.commit()

    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with overridden database."""
    app.dependency_overrides[get_db] = override_get_db

    # Recreate tables for this test
    Base.metadata.create_all(bind=engine)

    # Seed test exercises
    from models.database import Exercise
    db = TestingSessionLocal()
    if db.query(Exercise).filter(Exercise.is_custom == False).count() == 0:
        exercises = [
            Exercise(name="Bench Press", category="push", muscle_groups=["chest", "triceps"], equipment="barbell", is_custom=False),
            Exercise(name="Squat", category="legs", muscle_groups=["quadriceps", "glutes"], equipment="barbell", is_custom=False),
            Exercise(name="Deadlift", category="pull", muscle_groups=["back", "hamstrings"], equipment="barbell", is_custom=False),
            Exercise(name="Pull-Ups", category="pull", muscle_groups=["back", "biceps"], equipment="bodyweight", is_custom=False),
            Exercise(name="Running", category="cardio", muscle_groups=["quadriceps", "hamstrings"], equipment="none", is_custom=False),
        ]
        for ex in exercises:
            db.add(ex)
        db.commit()
    db.close()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_user(client):
    """Create a sample user for testing."""
    response = client.post("/api/users/", json={"name": "Test User"})
    return response.json()


@pytest.fixture
def sample_workout(client, sample_user):
    """Create a sample workout for testing."""
    from datetime import datetime, timezone
    response = client.post(
        f"/api/workouts/?user_id={sample_user['id']}",
        json={
            "name": "Test Workout",
            "notes": "Test notes",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "exercises": []
        }
    )
    return response.json()
