import pytest

from app.main import create_app


@pytest.fixture
def app():
    """App Flask com SQLite em memória (isolado por teste)."""
    return create_app("sqlite:///:memory:")


@pytest.fixture
def client(app):
    return app.test_client()
