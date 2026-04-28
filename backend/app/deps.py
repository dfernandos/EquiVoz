from flask import Request

from app.auth_utils import decode_token, get_user_by_email
from app.database import get_db
from app.models import User


class ApiError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


def get_bearer_token(request: Request) -> str | None:
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return None


def get_current_user() -> User:
    from flask import request

    token = get_bearer_token(request)
    if not token:
        raise ApiError(401, "Não autenticado")

    email = decode_token(token)
    if email is None:
        raise ApiError(401, "Token inválido ou expirado")

    db = get_db()
    user = get_user_by_email(db, email)
    if user is None:
        raise ApiError(401, "Usuário não encontrado")
    return user


def get_current_user_optional() -> User | None:
    """Utilizador autenticado, ou None se não houver token / token inválido (sem lançar erro)."""
    from flask import request

    token = get_bearer_token(request)
    if not token:
        return None
    email = decode_token(token)
    if email is None:
        return None
    db = get_db()
    return get_user_by_email(db, email)
