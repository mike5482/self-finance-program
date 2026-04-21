import pytest

from init_db import init_database
from main import create_app


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test_finance.db")


@pytest.fixture
def app(db_path):
    application = create_app(
        {
            "TESTING": True,
            "DATABASE": db_path,
            "SECRET_KEY": "test-secret",
        }
    )
    init_database(db_path)
    return application


@pytest.fixture
def client(app):
    return app.test_client()
