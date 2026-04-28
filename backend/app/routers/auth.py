import secrets
from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from app.auth_utils import create_access_token, get_user_by_email, hash_password, verify_password
from app.config import settings
from app.database import get_db
from app.deps import get_current_user
from app.email_smtp import enviar_email_verificacao, hash_token_verificacao
from app.models import User
from app.schemas import (
    LoginRequest,
    ReenviarVerificacaoRequest,
    Token,
    UserCreate,
    UserPublic,
)

bp = Blueprint("auth", __name__)


def _definir_token_verificacao(user: User) -> str:
    token = secrets.token_urlsafe(32)
    agora = datetime.now(timezone.utc)
    user.verification_token_hash = hash_token_verificacao(token)
    user.verification_token_expires_at = agora + timedelta(hours=settings.verificacao_email_horas)
    return token


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
        email_verified=False,
    )
    token_plano = _definir_token_verificacao(user)
    db.add(user)
    try:
        db.flush()
        enviar_email_verificacao(user.email, user.name, token_plano)
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        return jsonify(
            detail="Não foi possível enviar o e-mail de confirmação. Tente novamente mais tarde.",
        ), 500
    return (
        jsonify(
            {
                **UserPublic.model_validate(user).model_dump(mode="json"),
                "mensagem": "Enviamos um link de confirmação para o seu e-mail. Verifique a caixa de entrada e o spam.",
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
    if not user.email_verified:
        return jsonify(
            detail="Confirme o link que enviamos para o seu e-mail antes de entrar. Pode reenviar na página de cadastro ou de login."
        ), 403

    token = create_access_token(subject=user.email)
    return jsonify(Token(access_token=token).model_dump(mode="json"))


def _expirou_token(ate: datetime | None) -> bool:
    if ate is None:
        return True
    agora = datetime.now(timezone.utc)
    exp = ate
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    return exp < agora


@bp.get("/verificar-email")
def verificar_email():
    token_plano = (request.args.get("token") or "").strip()
    if not token_plano:
        return jsonify(detail="Token ausente ou inválido"), 400

    h = hash_token_verificacao(token_plano)
    db = get_db()
    user = db.query(User).filter(User.verification_token_hash == h).first()
    if user is None or _expirou_token(user.verification_token_expires_at):
        return jsonify(detail="Link inválido ou expirado. Peça um novo e-mail de verificação."), 400

    user.email_verified = True
    user.verification_token_hash = None
    user.verification_token_expires_at = None
    db.commit()
    return jsonify(
        detail="E-mail confirmado. Já pode entrar com o seu e-mail e senha.",
    )


@bp.post("/reenviar-verificacao")
def reenviar_verificacao():
    try:
        body = ReenviarVerificacaoRequest.model_validate(request.get_json(silent=True) or {})
    except ValidationError as e:
        return jsonify(detail=e.errors()), 422

    db = get_db()
    user = get_user_by_email(db, str(body.email))
    if user and not user.email_verified:
        token_plano = _definir_token_verificacao(user)
        try:
            db.flush()
            enviar_email_verificacao(user.email, user.name, token_plano)
            db.commit()
        except Exception:
            db.rollback()
            return jsonify(detail="Falha ao reenviar o e-mail. Tente mais tarde."), 500

    return jsonify(
        detail="Se o e-mail estiver cadastrado e ainda não tiver sido confirmado, enviámos um novo link.",
    )
