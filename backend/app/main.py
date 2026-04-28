import os

from flask import Flask, g, jsonify
from flask_cors import CORS
from sqlalchemy import inspect, text

from app.config import settings
from app.database import Base, get_engine, get_session_factory
from app.deps import ApiError
from app.routers import auth, denuncias, geocoding


def _cors_allowed_origins() -> list:
    locais = [
        "http://localhost:5173",
        "http://localhost:8081",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8081",
    ]
    extra = settings.cors_origins
    if not (extra and str(extra).strip()):
        return locais
    for parte in str(extra).split(","):
        p = parte.strip()
        if p:
            locais.append(p)
    return list(dict.fromkeys(locais))


def _ensure_user_email_verification_columns(engine) -> None:
    """Adiciona colunas de verificação de e-mail a `users` em BDs antigos. Contas anteriores à feature ficam com e-mail “verificado” (uma vez)."""
    if "users" not in inspect(engine).get_table_names():
        return
    cols = {c["name"] for c in inspect(engine).get_columns("users")}
    is_sqlite = engine.dialect.name == "sqlite"
    herdou_contas_existentes = "email_verified" not in cols
    with engine.begin() as conn:
        if herdou_contas_existentes:
            if is_sqlite:
                conn.execute(
                    text("ALTER TABLE users ADD COLUMN email_verified INTEGER NOT NULL DEFAULT 0")
                )
            else:
                conn.execute(
                    text("ALTER TABLE users ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT false")
                )
        if "verification_token_hash" not in cols:
            conn.execute(
                text("ALTER TABLE users ADD COLUMN verification_token_hash VARCHAR(64)")
            )
        if "verification_token_expires_at" not in cols:
            if is_sqlite:
                conn.execute(text("ALTER TABLE users ADD COLUMN verification_token_expires_at DATETIME"))
            else:
                conn.execute(
                    text("ALTER TABLE users ADD COLUMN verification_token_expires_at TIMESTAMPTZ")
                )
        if herdou_contas_existentes:
            if is_sqlite:
                conn.execute(text("UPDATE users SET email_verified = 1"))
            else:
                conn.execute(text("UPDATE users SET email_verified = true"))


def _ensure_password_reset_columns(engine) -> None:
    if "users" not in inspect(engine).get_table_names():
        return
    cols = {c["name"] for c in inspect(engine).get_columns("users")}
    is_sqlite = engine.dialect.name == "sqlite"
    with engine.begin() as conn:
        if "password_reset_token_hash" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN password_reset_token_hash VARCHAR(64)"))
        if "password_reset_expires_at" not in cols:
            if is_sqlite:
                conn.execute(text("ALTER TABLE users ADD COLUMN password_reset_expires_at DATETIME"))
            else:
                conn.execute(
                    text("ALTER TABLE users ADD COLUMN password_reset_expires_at TIMESTAMPTZ")
                )


def create_app(database_url: str | None = None) -> Flask:
    if database_url is not None:
        from app.database import configure_engine

        configure_engine(database_url)

    effective = database_url or settings.database_url
    if os.environ.get("DYNO") and "sqlite" in str(effective).lower():
        raise RuntimeError(
            "No Heroku o PostgreSQL é obrigatório. Adicione o add-on Heroku Postgres (recomendado) "
            "ou defina a variável DATABASE_URL com postgresql+psycopg://... ou postgresql://... . "
            "O SQLite no disco do dyno apaga os dados a cada deploy."
        )

    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    _ensure_user_email_verification_columns(engine)
    _ensure_password_reset_columns(engine)
    if engine.dialect.name == "sqlite":
        with engine.begin() as conn:
            r = conn.execute(text("PRAGMA table_info(denuncias)"))
            col_names = {row[1] for row in r}
            if col_names and "empresa" not in col_names:
                conn.execute(text("ALTER TABLE denuncias ADD COLUMN empresa VARCHAR(255)"))

    app = Flask(__name__)

    CORS(
        app,
        resources={r"/api/*": {"origins": _cors_allowed_origins()}},
        supports_credentials=True,
    )

    @app.before_request
    def open_db_session():
        g.db = get_session_factory()()

    @app.teardown_request
    def close_db_session(_exc):
        db = getattr(g, "db", None)
        if db is not None:
            db.close()

    app.register_blueprint(auth.bp, url_prefix="/api/auth")
    app.register_blueprint(denuncias.bp, url_prefix="/api/denuncias")
    app.register_blueprint(geocoding.bp, url_prefix="/api/geocoding")

    @app.errorhandler(ApiError)
    def handle_api_error(err: ApiError):
        return jsonify(detail=err.detail), err.status_code

    @app.get("/api/health")
    def health():
        return jsonify(status="ok", service="equivoz")

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=8000, debug=True)
