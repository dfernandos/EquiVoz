import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode, urljoin

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app.auth_utils import create_access_token, get_user_by_email, hash_password, verify_password
from app.config import settings
from app.database import get_db
from app.deps import get_current_user
from app.email_smtp import send_password_reset_email
from app.models import User
from app.schemas import (
    EsqueciSenhaRequest,
    LoginRequest,
    RedefinirSenhaRequest,
    Token,
    UserCreate,
    UserPublic,
)

_log = logging.getLogger(__name__)

bp = Blueprint("auth", __name__)

_MSG_ESQUECI = (
    "Se existir uma conta com este e-mail, enviaremos em instantes as instruções "
    "para redefinir a senha."
)


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _forgot_password_url(raw_token: str) -> str:
    base = str(settings.app_public_url).rstrip("/") + "/"
    return urljoin(base, f"redefinir-senha?{urlencode({'token': raw_token})}")


@bp.get("/me")
def me():
    user = get_current_user()
    return jsonify(UserPublic.model_validate(user).model_dump(mode="json"))


@bp.post("/register")
def register():
    try:
        body = UserCreate.model_validate(request.get_json(silent=True) or {})
    except ValidationError as e:
        return jsonify(detail=e.errors()), 422

    db = get_db()
    if get_user_by_email(db, str(body.email)):
        return jsonify(detail="E-mail já cadastrado"), 400

    user = User(
        email=str(body.email),
        hashed_password=hash_password(body.password),
        name=body.name.strip(),
        email_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return (
        jsonify(
            {
                **UserPublic.model_validate(user).model_dump(mode="json"),
                "mensagem": "Conta criada com sucesso. Já pode entrar com o seu e-mail e senha.",
            }
        ),
        201,
    )


@bp.post("/login")
def login():
    try:
        body = LoginRequest.model_validate(request.get_json(silent=True) or {})
    except ValidationError as e:
        return jsonify(detail=e.errors()), 422

    db = get_db()
    user = get_user_by_email(db, str(body.email))
    if user is None or not verify_password(body.password, user.hashed_password):
        return jsonify(detail="E-mail ou senha incorretos"), 401

    token = create_access_token(subject=user.email)
    return jsonify(Token(access_token=token).model_dump(mode="json"))


@bp.post("/esqueci-senha")
def esqueci_senha():
    try:
        body = EsqueciSenhaRequest.model_validate(request.get_json(silent=True) or {})
    except ValidationError as e:
        return jsonify(detail=e.errors()), 422

    db = get_db()
    user = get_user_by_email(db, str(body.email))
    if user is not None:
        raw = secrets.token_urlsafe(32)
        now = datetime.now(timezone.utc)
        user.password_reset_token_hash = _hash_token(raw)
        user.password_reset_expires_at = now + timedelta(hours=settings.password_reset_token_horas)
        db.add(user)
        db.commit()
        url = _forgot_password_url(raw)
        try:
            send_password_reset_email(user.email, user.name, url)
        except Exception:  # noqa: BLE001 — registo de falhas SMTP/ rede sem expor ao cliente
            _log.exception("Falha ao enviar e-mail de redefinição (ver Heroku logs / Brevo SMTP).")
    return jsonify(detail=_MSG_ESQUECI), 200


@bp.post("/redefinir-senha")
def redefinir_senha():
    try:
        body = RedefinirSenhaRequest.model_validate(request.get_json(silent=True) or {})
    except ValidationError as e:
        return jsonify(detail=e.errors()), 422

    db = get_db()
    h = _hash_token(body.token.strip())
    now = datetime.now(timezone.utc)
    user = db.query(User).filter(User.password_reset_token_hash == h).first()
    if user is None or user.password_reset_expires_at is None:
        return jsonify(detail="Link inválido ou expirado. Peça outro e-mail de redefinição."), 400
    exp = user.password_reset_expires_at
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if now > exp:
        return jsonify(detail="Link inválido ou expirado. Peça outro e-mail de redefinição."), 400

    user.hashed_password = hash_password(body.password)
    user.password_reset_token_hash = None
    user.password_reset_expires_at = None
    db.add(user)
    db.commit()
    return jsonify(detail="Senha redefinida. Já pode entrar com a nova senha."), 200
