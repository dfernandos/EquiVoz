from app.config import Settings


def test_database_url_normaliza_postgres_scheme():
    s = Settings(database_url="postgres://u:p@localhost:5432/db")
    assert s.database_url == "postgresql://u:p@localhost:5432/db"


def test_database_url_mantem_postgresql_psycopg():
    raw = "postgresql+psycopg://u:p@localhost:5432/db"
    s = Settings(database_url=raw)
    assert s.database_url == raw
