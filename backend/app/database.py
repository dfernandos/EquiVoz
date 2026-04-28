from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

_engine = None
_session_factory = None


def configure_engine(database_url: str) -> None:
    """Define ou troca engine e fábrica de sessões (útil em testes com SQLite em memória)."""
    global _engine, _session_factory
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    _engine = create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)
    _session_factory = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def get_engine():
    if _engine is None:
        from app.config import settings

        configure_engine(settings.database_url)
    return _engine


def get_session_factory():
    if _session_factory is None:
        get_engine()
    return _session_factory


def get_db():
    """Sessão SQLAlchemy do request atual (requer `g.db` definido em `create_app`)."""
    from flask import g

    return g.db
