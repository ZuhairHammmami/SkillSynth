import os
import shutil
import sys
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from backend.limiter import limiter

limiter.enabled = False
limiter._auto_check = False

_TEST_DIR = tempfile.mkdtemp(prefix="skillsynth_test_")
TEST_DB_PATH = os.path.join(_TEST_DIR, "skillsynth_test.db")
os.environ["SKILLSYNTH_TEST_DB_PATH"] = TEST_DB_PATH

test_engine = create_engine(
    f"sqlite:///{TEST_DB_PATH}",
    connect_args={"check_same_thread": False},
)


@event.listens_for(test_engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

import backend.database as database

database.engine = test_engine
database.SessionLocal = TestingSessionLocal

import backend.entities  # noqa: E402,F401

database.Base.metadata.create_all(bind=test_engine)

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import seed_v4  # noqa: E402

seed_v4.seed(engine=test_engine, session_factory=TestingSessionLocal)

from backend.main import app  # noqa: E402
from backend.database import get_db  # noqa: E402


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    yield
    client.close()
    test_engine.dispose()
    shutil.rmtree(_TEST_DIR, ignore_errors=True)


@pytest.fixture
def api_client():
    return client


@pytest.fixture
def db_session():
    """One direct session into the isolated test DB (for assertions that
    must inspect persisted state, e.g. user_skills after regeneration)."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def user_token():
    response = client.post(
        "/api/auth/token",
        data={"username": "veteran@skillsynth.io", "password": "Veteran@123456"},
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture
def admin_token():
    response = client.post(
        "/api/auth/token",
        data={"username": "admin@skillsynth.io", "password": "Admin@123456"},
    )
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
