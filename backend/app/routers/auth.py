from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app.auth_utils import create_access_token, get_user_by_email, hash_password, verify_password
from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.schemas import LoginRequest, Token, UserCreate, UserPublic

bp = Blueprint("auth", __name__)


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
