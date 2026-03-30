import os
import tempfile
import pytest
from fastapi.testclient import TestClient

_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["KANBAN_DB_PATH"] = _tmp.name

from app.main import app  # noqa: E402
from app.db import run_migrations  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    import app.db as db_mod
    db_mod.DB_PATH = _tmp.name
    run_migrations(_tmp.name)
    yield
    os.unlink(_tmp.name)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def seed_card():
    from app.repositories import cards as cards_repo
    card = cards_repo.create_card(
        column_id=1,
        title="Test user story",
        description="As a developer, I want tests, so that I have confidence",
    )
    yield card
    try:
        cards_repo.delete_card(card["id"])
    except Exception:
        pass
