import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlmodel import Session, SQLModel, create_engine

from App.config import settings
from App.database import get_session
from App.main import app

# Same server and password as your real database, but a different database name.
TEST_URL = make_url(settings.database_url).set(database="snipshare_test")

# Safety check: tests wipe tables, so refuse to run on anything not named *_test.
assert TEST_URL.database.endswith("_test"), "Refusing to run tests on a non-test database"

test_engine = create_engine(TEST_URL, pool_pre_ping=True)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)
    yield
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture(autouse=True)
def clean_tables():
    # Runs after every test: empty all tables and reset ids back to 1.
    yield
    with test_engine.begin() as conn:
        conn.execute(text('TRUNCATE TABLE vote, snip, "user" RESTART IDENTITY CASCADE'))


def override_get_session():
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def client():
    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Helper fixtures – keep tests short and readable
# ---------------------------------------------------------------------------

# A counter to make emails unique across fixtures in the same test.
_user_counter = 0


def _next_email(base="user"):
    """Return a unique email each time it's called."""
    global _user_counter
    _user_counter += 1
    return f"{base}{_user_counter}@test.com"


@pytest.fixture(autouse=True)
def _reset_user_counter():
    """Reset the counter before every test so emails are predictable."""
    global _user_counter
    _user_counter = 0


def register_user(client, email=None, password="securepass123"):
    """Register a user via the API. Returns the response."""
    if email is None:
        email = _next_email()
    return client.post(
        "/auth/register",
        data={"email": email, "password": password},
    )


def login_user(client, email, password="securepass123"):
    """Log in and return the response (contains access_token)."""
    return client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )


def get_auth_headers(client, email=None, password="securepass123"):
    """Register + login a user and return the Authorization header dict."""
    if email is None:
        email = _next_email()
    register_user(client, email=email, password=password)
    resp = login_user(client, email=email, password=password)
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers(client):
    """Headers for 'user A' — the primary test user."""
    return get_auth_headers(client, email="alice@test.com")


@pytest.fixture
def second_auth_headers(client):
    """Headers for 'user B' — a second user for permission tests."""
    return get_auth_headers(client, email="bob@test.com")


# Default snippet payload (all required fields filled in).
DEFAULT_SNIPPET = {
    "title": "Hello World",
    "language": "python",
    "code": "print('hello')",
    "description": "A simple snippet",
}


def create_snippet(client, headers, **overrides):
    """Create a snippet via the API. Returns the response."""
    payload = {**DEFAULT_SNIPPET, **overrides}
    return client.post("/api/snippets/", json=payload, headers=headers)


@pytest.fixture(autouse=True)
def redirect_uploads(tmp_path, monkeypatch):
    """Point settings.upload_dir at a temp directory so tests don't
    write files into the real uploads folder."""
    monkeypatch.setattr(settings, "upload_dir", tmp_path)