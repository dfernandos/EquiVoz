from flask import Flask, g, jsonify
from flask_cors import CORS
from sqlalchemy import text

from app.database import Base, get_engine, get_session_factory
from app.deps import ApiError
from app.routers import auth, denuncias, geocoding


def create_app(database_url: str | None = None) -> Flask:
    if database_url is not None:
        from app.database import configure_engine

        configure_engine(database_url)
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    if engine.dialect.name == "sqlite":
        with engine.begin() as conn:
            r = conn.execute(text("PRAGMA table_info(denuncias)"))
            col_names = {row[1] for row in r}
            if col_names and "empresa" not in col_names:
                conn.execute(text("ALTER TABLE denuncias ADD COLUMN empresa VARCHAR(255)"))

    app = Flask(__name__)

    CORS(
        app,
        resources={r"/api/*": {"origins": ["http://localhost:5173", "http://localhost:8081", "http://127.0.0.1:5173", "http://127.0.0.1:8081"]}},
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
