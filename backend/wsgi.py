"""Ponto de entrada WSGI para Gunicorn (p. ex. Heroku, produção)."""

from app.main import create_app

app = create_app()
